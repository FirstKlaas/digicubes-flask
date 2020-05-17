"""
    Client for the DigiCubeServer
"""

import json
import logging

import cattr
import requests

from digicubes_flask import structures as st
from digicubes_flask.exceptions import TokenExpired, ServerError, DoesNotExist

# from digicubes_flask.configuration import url_for, Route

from .proxy import UserProxy
from .service import RoleService, UserService, SchoolService, RightService
from .cache import create_cache

logger = logging.getLogger(__name__)


class DigiCubeClient:
    """
    The main client class, to communicate with the digicube server
    """

    @staticmethod
    def create_from_server(server):
        """Factory method to create special client used in tests."""
        client = DigiCubeClient()
        client.requests = server.api.requests
        return client

    __slots__ = [
        "protocol",
        "hostname",
        "port",
        "user_service",
        "role_service",
        "right_service",
        "school_service",
        "requests",
        "cache",
        "__token",
    ]

    def __init__(
        self, protocol: str = "http", hostname: str = "localhost", port: int = 3000
    ) -> None:
        self.protocol = protocol
        self.hostname = hostname
        self.port = port
        self.user_service: UserService = UserService(self)
        self.role_service: RoleService = RoleService(self)
        self.right_service: RightService = RightService(self)
        self.school_service: SchoolService = SchoolService(self)

        self.requests = requests

        # The configured cache. The function returns always
        # a valid cache object. When no implementation is spcified,
        # A NoneCache instance is returned, wich will not cache anything
        # but can be used in the code.
        self.cache = create_cache()

    def generate_token_for(self, login: str, password: str):
        """
        Log into the server with the given credentials.
        If successfull, the it returns the access token.

        :param str login: The user login
        :param str password: The user password
        :returns: The access token
        :rtype: BearerTokenData
        :raises: DoesNotExist, ServerError
        """
        logger.info("Login with account %s to get bearer token.", login)
        data = {"login": login, "password": password}
        headers = {"accept": "application/json"}
        # TODO: Use url_for
        response = self.requests.post(self.url_for("/login/"), data=data, headers=headers)

        if response.status_code == 404:
            raise DoesNotExist(f"User with login {login} does not exist.")

        if response.status_code != 200:
            raise ServerError(response.text)

        return st.BearerTokenData.structure(response.json())

    def login(self, login: str, password: str) -> str:
        """
        Log into the server with the given credentials.
        If successfull, the it returns the access token.

        :param str login: The user login
        :param str password: The user password
        :returns: The access token
        :rtype: BearerTokenData
        :raises: DoesNotExist, ServerError
        """
        token: st.BearerTokenData = self.generate_token_for(login, password)
        me = self.user_service.me(token.bearer_token)
        self.cache.set_user(me)
        return token

    def url_for(self, route: str, **kwargs):
        """
        Get the formatted url for a given route.
        """
        if isinstance(route, str):
            return f"{self.base_url}{route.format(**kwargs)}"

        raise ValueError("Unsupported route type")

    @property
    def base_url(self):
        """
        Returns the base url for the server.
        """
        if self.hostname is None:
            return ""

        return f"{self.protocol}://{self.hostname}:{self.port}"

    def create_default_header(self, token):
        """
        Creates the default header for a standard
        call. Sets the bearer token as well as the
        accept header.
        """
        auth_value = f"Bearer {token}"
        return {"Authorization": auth_value, "Accept": "application/json"}

    def refresh_token(self, token) -> st.BearerTokenData:
        """
        Requesting a new bearer token.
        """
        logger.info("Refreshing bearer token. Old token is %s", token)
        url = self.url_for("/token/")
        headers = self.create_default_header(token)
        response = self.requests.post(url, headers=headers)
        if response.status_code == 200:
            data = st.BearerTokenData.structure(response.json())
            return data
        if response.status_code == 401:
            raise TokenExpired("Your auth token has expired.")

        raise ServerError("A server error occurred.")

    def home_routes(self):
        url = self.url_for("/info/")
        response = self.requests.post(f"{url}?w=home_routes")
        return response.json()
