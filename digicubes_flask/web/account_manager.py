"""
The main extension module
"""
import logging
import os
from datetime import datetime

from flask import Flask, abort, current_app, redirect, url_for
from flask_wtf.csrf import CSRFError
from markdown import markdown

from digicubes_flask import account_manager, current_user, get_version_string
from digicubes_flask.client import (DigiCubeClient, RightService, RoleService,
                                    SchoolService, UserService)
from digicubes_flask.client.model import BearerTokenData

from .momentjs import to_local_datetime

logger = logging.getLogger(__name__)

__all__ = ["DigicubesAccountManager"]


class DigicubesAccountManager:
    """
    Flask extension which is responsible for login and
    logout procedures.
    """

    def __init__(self, app=None):
        # Callbacks
        self.app = app
        self.init_app(app)
        self.unauthorized_callback = None
        self.successful_logged_in_callback = None

    def init_app(self, app: Flask) -> None:
        """
        Initialises the login manager and adds itself
        to the app.
        """
        if app is not None:
            app.digicubes_account_manager = self
            login_view = app.config.get("DIGICUBES_ACCOUNT_LOGIN_VIEW", "account.login")
            index_view = app.config.get("DIGICUBES_ACCOUNT_INDEX_VIEW", "account.index")
            self.unauthorized_callback = lambda: redirect(url_for(login_view))
            self.successful_logged_in_callback = lambda: redirect(url_for(index_view))

            self._client = DigiCubeClient(
                protocol=os.getenv("DIGICUBES_API_SERVER_PROTOCOL", "http"),
                hostname=os.getenv("DIGICUBES_API_SERVER_HOST", "localhost"),
                port=int(os.getenv("DIGICUBES_API_SERVER_PORT", "3548")),
            )

            # At the end of each request the session
            # variables are updated. The token as well as the session id
            # are written to the session. Or removed if requested.
            # app.after_request(update_current_user)

            def has_role(role_name: str) -> bool:
                # TODO: Using cached roles
                for role in self.user.get_my_roles(self.token):
                    if role.name == role_name:
                        return True

                return False

            def has_right(right: str) -> bool:
                # Vielleicht nicht über den user_service machen, sondern
                # über den account manager. Dann hätte man die Möglichkeit,
                # die Rechte zumindest im g Scope zu sichern.
                rights = self.user.get_my_rights(self.token)
                return "no_limits" in rights or right in rights

            def is_root(user_id: int) -> bool:
                return has_right("no_limits")

            @app.template_filter()
            def format_datetime(
                value, date_format="%d %b %Y %I:%M %p"
            ):  # pylint: disable=unused-variable
                """Format a date time to (Default): d Mon YYYY HH:MM P"""
                if value is None:
                    return ""

                if isinstance(value, str):
                    return datetime.fromisoformat(value).strftime(date_format)

                return value.strftime(date_format)

            # Make certain objects available to be used in jinja2 templates
            app.context_processor(
                lambda: {
                    "digicubes": account_manager,
                    "current_user": current_user,
                    "has_right": has_right,
                    "is_root": is_root,
                    "version": get_version_string(),
                    "has_role": has_role,
                    "md": markdown,
                    "format_datetime": format_datetime,
                    "to_local_datetime": to_local_datetime,
                }
            )

            @app.errorhandler(CSRFError)
            def handle_csrf_error(e):  # pylint: disable=unused-variable
                logger.error("A CSFR error occorred. %s", e.description)
                return e.description, 400

    @property
    def auto_verify(self):
        """
        Returns the status of auto verify. If true, new users will
        automatically be verified, after creating an account.
        """
        return current_app.config.get("auto_verify", False)

    @property
    def token(self):
        """
        Returns the token for the current user.
        """
        return current_user.token if current_user is not None else None

    @property
    def authenticated(self):
        """
        Test, wether a user has successfully logged into the system.
        """
        # A bit crude the test.
        # Mayby a server call would be better,
        # as we do not know if it is a valid
        # token. But for the time being it
        # will do the job.
        return current_user.token is not None

    def successful_logged_in_handler(self, callback):
        """
        Setting the handler that is called, after a user
        has succesfully logged in. This callback is used by
        the `login` route.def login

        The callback must return the response, like any route.

        :param callback: The callback for successfully logged in users.
        :type callback: callable
        """
        self.successful_logged_in_callback = callback
        return callback

    def unauthorized_handler(self, callback):
        """
        This will set the callback for the `unauthorized` method, which among
        other things is used by `login_required`. It takes no arguments, and
        should return a response to be sent to the user instead of their
        normal view.

        :param callback: The callback for unauthorized users.
        :type callback: callable
        """
        self.unauthorized_callback = callback
        return callback

    def unauthorized(self):
        """
        Calls the unauthorized handler, or if no handler was
        set aborts with status 401.
        """
        if self.unauthorized_callback:
            return self.unauthorized_callback()

        # No handler set. Defaults to 401 error
        return abort(401)

    def successful_logged_in(self):
        """
        Calls the 'successful_logged_in` handler, or if no
        handler was registered aborts with status 404
        """
        if self.successful_logged_in_callback:
            return self.successful_logged_in_callback()
        return abort(404)

    @property
    def config(self):
        app = current_app
        return app.config

    def login(self, login: str, password: str) -> BearerTokenData:
        """
        Checks the credentials and, if successfully, adds
        user id and token to the session.

        :returns: The access token
        :rtype: BearerTokenData
        :raises: DoesNotExist, ServerError
        """
        data = self._client.login(login, password)
        current_user.set_data(data)
        return data

    def generate_token_for(self, login: str, password: str) -> str:
        """
        Generates a token for the given credentials.

        :param str login: The user login
        :param str password: The user password
        :returns: The access token
        :rtype: BearerTokenData
        :raises: DoesNotExist, ServerError
        """
        return self._client.generate_token_for(login, password)

    def logout(self):
        """
        Logs the current user out
        """
        current_user.reset()

    @property
    def user(self) -> UserService:
        """user servives"""
        return self._client.user_service

    @property
    def role(self) -> RoleService:
        """role services"""
        return self._client.role_service

    @property
    def right(self) -> RightService:
        return self._client.right_service

    @property
    def school(self) -> SchoolService:
        return self._client.school_service

    def refresh_token(self, token) -> BearerTokenData:
        return self._client.refresh_token(token)
