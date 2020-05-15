"""
All user requests
"""
import logging
from typing import Optional, List

from digicubes_flask.exceptions import (
    ConstraintViolation,
    ServerError,
    DoesNotExist,
    InsufficientRights,
    TokenExpired,
)

from .abstract_service import AbstractService
from ..proxy import UserProxy, RoleProxy

UserList = List[UserProxy]
XFieldList = Optional[List[str]]

logger = logging.getLogger(__name__)


class UserService(AbstractService):
    """
    All user calls
    """

    def all(
        self,
        token,
        fields: XFieldList = None,
        offset: Optional[int] = None,
        count: Optional[int] = None,
    ) -> UserList:
        """
        Gets all users.

        Returns a list of UserProxies. ``X-Filter-Fields`` is supported.
        """
        headers = self.create_default_header(token)
        if fields is not None:
            headers[self.X_FILTER_FIELDS] = ",".join(fields)

        url = self.url_for("/users/")
        params = {}
        if offset:
            params["offset"] = offset

        if count:
            params["count"] = count

        result = self.requests.get(url, headers=headers, params=params)

        if result.status_code == 404:
            return []

        if result.status_code == 401:
            raise ValueError("Not authenticated")

        if result.status_code != 200:
            raise ServerError("Got an server error")

        data = result.json()
        user_data = data.get("result", None)
        if user_data is None:
            raise ServerError("No content provided.")

        return [UserProxy.structure(user) for user in user_data]

    def get_my_rights(self, token, fields: XFieldList = None):
        "Get my rights"
        headers = self.create_default_header(token=token)
        if fields is not None:
            headers[self.X_FILTER_FIELDS] = ",".join(fields)

        url = self.url_for("/me/rights")
        result = self.requests.get(url, headers=headers)
        logger.debug("Requested rights. Status is %s", result.status_code)
        if result.status_code == 200:
            data = result.json()
            return data

        raise TokenExpired("Could not read user rights. Token expired.")

    def get_my_roles(self, token, fields: XFieldList = None):
        "Get my roles"
        headers = self.create_default_header(token=token)
        if fields is not None:
            headers[self.X_FILTER_FIELDS] = ",".join(fields)

        url = self.url_for("/me/roles/")
        result = self.requests.get(url, headers=headers)

        if result.status_code == 200:
            data = result.json()
            return [RoleProxy.structure(role) for role in data]

        raise TokenExpired("Could not read user roles. Token expired.")

    def me(self, token, fields: XFieldList = None) -> Optional[UserProxy]:
        """
        Get a single user
        """
        headers = self.create_default_header(token)
        if fields is not None:
            headers[self.X_FILTER_FIELDS] = ",".join(fields)

        url = self.url_for("/me/")
        result = self.requests.get(url, headers=headers)

        if result.status_code == 401:
            raise TokenExpired("Could not read user details. Token expired.")

        if result.status_code == 404:
            return None

        if result.status_code == 200:
            return UserProxy.structure(result.json())

        return None

    def get_by_login(self, token: str, login: str) -> UserProxy:
        """
        Get a single user by his login, if existent.

        :param str token: The authentification token
        :param str login: The login of the user to be looked up.
        :return: The found user
        :rtype: UserProxy
        :raises InsufficientRights: If the requesting user has not the permission.
        :raises DoesNotExist: if no user exists with the provided login.
        :raises TokenExpired: is the token has expired.
        :raises ServerError: if an unpredicted exception occurred.
        """
        headers = self.create_default_header(token)
        url = self.url_for(f"/user/bylogin/{login}")
        response = self.requests.get(url, headers=headers)
        self.check_response_status(response, expected_status=200)
        return UserProxy.structure(response.json())

    def get_by_login_or_none(self, token: str, login: str) -> UserProxy:
        """
        Get a single user by his login or none, if the user does not
        exist.

        :param str token: The authentification token
        :param str login: The login of the user to be looked up.
        :return: The found user or None, if nor user with the login exists
        :rtype: UserProxy
        :raises InsufficientRights: If the requesting user has not the permission.
        :raises TokenExpired: is the token has expired.
        :raises ServerError: if an unpredicted exception occurred.
        """
        try:
            return self.get_by_login(token, login)
        except DoesNotExist:
            return None

    def get(self, token, user_id: int, fields: XFieldList = None) -> Optional[UserProxy]:
        """
        Get a single user
        """
        user = self.cache.get_user(user_id)
        if user is not None:
            logger.info("Cache hit for user %s", user.login)
            return user  # Cache hit

        # Cache miss
        headers = self.create_default_header(token)
        if fields is not None:
            headers[self.X_FILTER_FIELDS] = ",".join(fields)

        url = self.url_for(f"/user/{user_id}")
        response = self.requests.get(url, headers=headers)

        self.check_response_status(response, expected_status=200)
        user = UserProxy.structure(response.json())
        self.cache.set_user(user)  # Cache the fetched user.
        return user

    def set_password(
        self, token, user_id: int, new_password: str = None, old_password: str = None
    ) -> None:
        """
        Sets the password fo a user. If the current user has root rights, the old_password
        is not needed.
        """
        headers = self.create_default_header(token)
        data = {"password": new_password}
        url = self.url_for(f"/password/{user_id}")
        response = self.requests.post(url, headers=headers, data=data)
        self.check_response_status(response, expected_status=200)

    def delete(self, token, user_id: int) -> Optional[UserProxy]:
        """
        Deletes a user from the database
        """
        # TODO: Clear from cache (or wait for expiration of the key)
        headers = self.create_default_header(token)
        url = self.url_for(f"/user/{user_id}")
        result = self.requests.delete(url, headers=headers)

        if result.status_code == 404:
            raise DoesNotExist(f"User with user id {user_id} not found.")

        if result.status_code != 200:
            raise ServerError(f"Wrong status. Expected 200. Got {result.status_code}")

        return UserProxy.structure(result.json())

    def delete_all(self, token) -> None:
        """
        Delete all users from the database
        """
        headers = self.create_default_header(token)
        url = self.url_for("/users/")
        result = self.requests.delete(url, headers=headers)

        if result.status_code != 200:
            raise ServerError(f"Wrong status. Expected 200. Got {result.status_code}")

    def create(self, token: str, user: UserProxy, fields: XFieldList = None) -> UserProxy:
        """
        Creates a new user
        """
        headers = self.create_default_header(token)
        data = user.unstructure()

        if fields is not None:
            headers[self.X_FILTER_FIELDS] = ",".join(fields)

        url = self.url_for("/users/")
        result = self.requests.post(url, json=data, headers=headers)

        if result.status_code == 201:
            # User created successfully. We cannot create the user directly
            # with the password, so we have to set the password in a second step.
            #
            # TODO: Why not able to set the password directly in the
            # REST call? Check is and change it, if possible.
            user_proxy: UserProxy = UserProxy.structure(result.json())
            if not user.password:
                logger.debug("Created user without password.")
            else:
                self.set_password(token=token, user_id=user_proxy.id, new_password=user.password)

            return user_proxy

        if result.status_code == 409:
            raise ConstraintViolation(result.text)

        if result.status_code == 500:
            raise ServerError(result.text)

        raise ServerError(f"Unknown error. [{result.status_code}] {result.text}")

    def create_bulk(self, token, users: List[UserProxy]) -> None:
        """
        Create multiple users
        """
        headers = self.create_default_header(token)
        data = [user.unstructure() for user in users]
        url = self.url_for("/users/")
        result = self.requests.post(url, json=data, headers=headers)
        if result.status_code == 201:
            return

        if result.status_code == 409:
            raise ConstraintViolation(result.text)

        if result.status_code == 500:
            raise ServerError(result.text)

        raise ServerError(f"Unknown error. [{result.status_code}] {result.text}")

    def get_verification_token(self, user_id: int) -> str:
        url = self.url_for(f"/verify/user/{user_id}")
        response = self.requests.get(url)
        data = response.json()
        return data["token"]

    def verify_user(self, token: str):
        url = self.url_for(f"/verify/user/{token}")
        response = self.requests.put(url)
        data = response.json()

        return UserProxy.structure(data["user"]), data["token"]

    def update(self, token, user: UserProxy) -> UserProxy:
        """
        Update an existing user.
        If successfull, a new user proxy is returned with the latest version of the
        user data.
        """
        response = self.requests.put(
            self.url_for(f"/user/{user.id}"),
            json=user.unstructure(),
            headers=self.create_default_header(token))

        if response.status_code == 404:
            raise DoesNotExist(response.text)

        if response.status_code == 500:
            raise ServerError(response.text)

        if response.status_code != 200:
            raise ServerError(f"Wrong status. Expected 200. Got {response.status_code}")

        user = UserProxy.structure(response.json())

        # Add or update the cached user
        self.cache.set_user(user)
        return user  # TODO Check other status_codes

    def get_rights(self, token: str, user_id: int) -> List[str]:
        """
        Get all rights. The rest method returns an array of right names
        and not json objects.
        """
        user_rights = self.cache.get_user_rights(user_id)
        if user_rights is not None:
            # cache hit
            return user_rights

        # cache miss
        headers = self.create_default_header(token)
        url = self.url_for(f"/user/{user_id}/rights/")
        result = self.requests.get(url, headers=headers)

        if result.status_code == 401:
            raise TokenExpired()

        if result.status_code == 404:
            raise DoesNotExist(result.text)

        if result.status_code != 200:
            raise ServerError(f"Wrong status. Expected 200. Got {result.status_code}")

        user_rights = result.json()
        self.cache.set_user_rights(user_id, user_rights)  # cache user rights
        return user_rights

    def get_roles(self, token, user: UserProxy) -> List[RoleProxy]:
        """
        Get all roles for user.
        """
        if user is None:
            raise ValueError("No user provided")

        if user.id is None:
            raise ValueError("Invalid user provided. No id.")

        # TODO Filter fields as parameter
        headers = self.create_default_header(token)
        url = self.url_for(f"/user/{user.id}/roles/")
        result = self.requests.get(url, headers=headers)

        if result.status_code == 404:
            raise DoesNotExist(result.text)

        if result.status_code != 200:
            raise ServerError(f"Wrong status. Expected 200. Got {result.status_code}")

        return [RoleProxy.structure(role) for role in result.json()]

    def add_role(self, token, user: UserProxy, role: RoleProxy) -> bool:
        """
        Adds a role to the user
        """
        headers = self.create_default_header(token)
        url = self.url_for(f"/user/{user.id}/role/{role.id}")
        result = self.requests.put(url, headers=headers)
        return result.status_code == 200

    def remove_role(self, token, user: UserProxy, role: RoleProxy) -> bool:
        """
        Remove a role from the user
        """
        headers = self.create_default_header(token)
        url = self.url_for(f"/user/{user.id}/role/{role.id}")
        result = self.requests.delete(url, headers=headers)
        return result.status_code == 200
