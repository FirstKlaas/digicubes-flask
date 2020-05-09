"""
The main extension module
"""
import logging
from functools import wraps
from datetime import datetime, timedelta
from importlib.resources import open_text
import json
from typing import Optional, List

from flask import abort, current_app, request, Response, redirect, Flask, url_for, g
from flask_wtf.csrf import CSRFError
from werkzeug.local import LocalProxy

from digicubes_client.client import DigiCubeClient, service

from digicubes_common.structures import BearerTokenData
from digicubes_common.exceptions import DigiCubeError
from digicubes_common.entities import RightEntity

from .email.automailer import MailCube

logger = logging.getLogger(__name__)

# pylint: disable=unnecessary-lambda
account_manager = LocalProxy(lambda: _get_account_manager())
digicubes = account_manager
current_user = LocalProxy(lambda: _get_current_user())

DIGICUBES_ACCOUNT_ATTRIBUTE_NAME = "digicubes_account_manager"


def get_version_string():
    """Returns the version string for this module"""
    with open_text("digicubes_flask", "version.json") as f:
        data = json.load(f)
        return ".".join(str(n) for n in data["version"])


class CurrentUser:
    """
    This is the the current user logged in.
    It stores the token and the id during login
    or after authentification (via session cookie).
    If any other property requested, it loads the
    database user and delegates the request to that
    user instance.
    """

    def __init__(self):
        self._rights: List[str] = None  # Cached User rights
        self._dbuser = None
        self._token = None
        self._lifetime = None
        self._expires_at = None

    def set_data(self, data: BearerTokenData):
        self._token = data.bearer_token
        self._lifetime = data.lifetime
        self._expires_at = data.expires_at

    def reset(self):
        """
        Resets all internal fields and removes it from
        the global request context.
        """
        g.pop("digiuser", None)
        self._dbuser = None
        self._rights = None
        self._lifetime = None
        self._expires_at = None

    @property
    def token(self) -> str:
        return self._token

    @token.setter
    def token(self, value: str):
        self._token = value

    @property
    def lifetime(self) -> int:
        """
        Returns the lifetime (max age) of the token in seconds
        """
        return self._lifetime

    @property
    def expires_at(self) -> datetime:
        """
        Returns the expiration date as an datetime object
        """
        return self._expires_at

    def __str__(self):
        return f"CurrentUser(id={self.id}, token={self.token}"

    def __repr__(self):
        return f"CurrentUser(id={self.id}, token={self.token}"

    @property
    def id(self):
        if self.token is None:
            return None

        return self.dbuser.id

    @property
    def dbuser(self):
        """
        Lazy loading of the database user.

        After loading the user, it is cached in this instance.
        So multiple calls during one request will be faster.
        The instance is valid for the lifetime of a request.
        """
        if self.token is None:
            return None

        if self._dbuser is None:
            self._dbuser = account_manager.user.me(self.token)
            logger.debug("Loaded db user %s: %s", self._dbuser.id, self._dbuser.login)
        return self._dbuser

    def has_right(self, right):
        """
        Test, wether the current user has the given right.
        """
        return right in self.rights or "no_limits" in self.rights

    @property
    def is_root(self):
        """
        Test, if the current user has root privilidges.
        """
        return self.has_right("no_limits")

    @property
    def rights(self):
        """
        Getting the lazy loaded rights for the current
        user.
        """
        if self.token is None:
            return []

        if self._rights is None:
            self._rights = [str(r) for r in account_manager.user.get_my_rights(self.token)]

        return self._rights


def _get_current_user():
    if "digiuser" not in g or g.digiuser is None:
        g.digiuser = CurrentUser()
    return g.digiuser


def _get_account_manager():
    return getattr(current_app, DIGICUBES_ACCOUNT_ATTRIBUTE_NAME, None)


class needs_right:
    """
    Decorator for checking the needed rights to execute a method, function
    or route.

    The provided rights can be strings or items of the RightsEntity enum.
    You can call it with a single right or with a list of rights. In case
    where you call it witrh a list of rights, the semantic is the following:
    The condition is true, if the intersection of the provided rights and
    the user rigths is not empty. So the the list means "or". If you want
    to express the fact, that the user needs more than one rignt, simply
    add the decorator more than once.

    Example 1: The user needs to have right A or right B

    @needs_right("A", "B")
    def do_something():

    Example 1: The user needs to have right A and right B

    @needs_right("A")
    @needs_right("B")
    def do_something():

    """

    def __init__(self, rights, exclude_root=False):
        self._names = self._normalize_rights(rights)
        # Always add the root right as this is the joker
        # and doesn't have to be claimed explicitely as
        # the root can do anything.
        if not exclude_root:
            self._names.append(RightEntity.ROOT_RIGHT.name)

    def _normalize_right(self, right):
        if isinstance(right, str):
            return right

        if isinstance(right, RightEntity):
            return str(right.name)

        raise ValueError(
            "Provided right has wrong class. Has to be an instance of string or RIghtEntity"
        )

    def _check_rights(self):
        user_rights = [str(r) for r in current_user.rights]

        for right in user_rights:
            if right in self._names:
                return True
        return False

    def _normalize_rights(self, names):
        if isinstance(names, list):
            return [self._normalize_right(right) for right in names]

        return [self._normalize_right(names)]

    def __call__(self, f):
        # update_wrapper(self, f)
        @wraps(f)
        def wrapped_f(*args, **kwargs):
            if self._check_rights():
                return f(*args, **kwargs)
            # Call the handler for unauthorized requests
            return account_manager.unauthorized()

        return wrapped_f


def login_required(f):
    """
    Decorator for routes which should be only accessible for
    authorized user. The decorator tries to find the bearer
    token and if found checks if the token is equal to the
    one we have stored in the current api client.

    If no token can be found, or the tokens are not equal,
    the registered handler is called.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):

        # Check if we can find the token
        token = current_user.token

        if token is not None:
            # We have a token
            return f(*args, **kwargs)

        # Call the handler for unauthorized requests
        return account_manager.unauthorized()

    return decorated_function
