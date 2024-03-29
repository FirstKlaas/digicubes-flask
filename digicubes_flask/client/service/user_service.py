"""
All user requests
"""
import logging
from typing import List, Optional, Text

from pydantic import parse_obj_as

from digicubes_flask.client.model import (BearerTokenData, RoleModel,
                                          UserModel, UserModelUpsert)
from digicubes_flask.exceptions import (ConstraintViolation, DigiCubeError,
                                        DoesNotExist, ServerError,
                                        TokenExpired)

from .abstract_service import AbstractService
from .filter import Query

UserList = List[UserModel]
XFieldList = Optional[List[Text]]

logger = logging.getLogger(__name__)


class UserService(AbstractService):
    """
    The ``UserService`` offers a set of service calls to manage
    user accounts. This includes calls to manipulate the user itself,
    as well as related objects, likes roles or rights.

    :author: FirstKlaas
    """

    def all(
        self,
        token,
        fields: XFieldList = None,
        offset: Optional[int] = None,
        count: Optional[int] = None,
        **kwargs,
    ) -> UserList:
        """
        Get all users in the database.

        Returns a list of :class:`UserModel` instances.
        If ``X-Filter-Fields`` is provided, only attributes are send back that
        are in the list. If an attribute has no value it will be omitted.

        :Route: ``GET /users/``
        :param str token: The authentification token
        :param XFieldList fields: A list of fieldnames that should be send back.
            If omitted all attributes will be send back. *[Optional]*
        :offset: Starting with the n-th element in the database. If omitted, the
            list will start with the first element in the database.
        :count: Limits the number of returned items. If omitted, it will fallback
            to the configured maximum number of items. The number of returned
            items may of course be smaller than count.
        :kwargs: These named parameters will be added as query parameters
        :return: The requested Users
        :rtype: A list of :class:`UserModel` objects.
        :raises InsufficientRights: If the requesting user has not the permission.
        :raises TokenExpired: is the token has expired.
        :raises ServerError: if an unpredicted exception occurred.
        """
        headers = self.create_default_header(token, fields=fields)
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
            raise ServerError("Got an server error.")

        data = result.json()
        user_data = data.get("result", None)
        if user_data is None:
            raise ServerError("No content provided.")

        return parse_obj_as(List[UserModel], user_data)

    def user_schema(self, token):
        headers = self.create_default_header(token=token)
        headers["Accept"] = "application/schema+json"
        url = self.url_for("/users/")
        result = self.requests.get(url, headers=headers)
        return result.json()

    def get_my_rights(self, token, fields: XFieldList = None):
        "Get my rights"
        headers = self.create_default_header(token=token)
        if fields is not None:
            headers[self.X_FILTER_FIELDS] = ",".join(fields)

        url = self.url_for("/me/rights/")
        result = self.requests.get(url, headers=headers)
        logger.debug("Requested rights. Status is %s", result.status_code)

        if result.status_code == 200:
            data = result.json()
            return data

        raise TokenExpired("Could not read user rights. Token expired.")

    def get_my_roles(self, token, fields: XFieldList = None) -> List[RoleModel]:
        """
        Get my roles. Returns a list of role names, that the
        current user has.
        """
        headers = self.create_default_header(token=token)
        if fields is not None:
            headers[self.X_FILTER_FIELDS] = ",".join(fields)
        url = self.url_for("/me/roles/")
        result = self.requests.get(url, headers=headers)

        if result.status_code == 200:
            return parse_obj_as(List[RoleModel], result.json())

        if result.status_code == 404:
            raise DoesNotExist()

        raise TokenExpired("Could not read user roles. Token expired.")

    def me(self, token, fields: XFieldList = None) -> Optional[UserModel]:
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
            return UserModel.parse_obj(result.json())

        return None

    def get_by_login(self, token: str, login: str) -> UserModel:
        """
        Get a single user by his login, if existent.

        :Route: ``/user/bylogin/{login}``
        :param str token: The authentification token
        :param str login: The login of the user to be looked up.
        :return: The found user
        :rtype: UserModel
        :raises InsufficientRights: If the requesting user has not the permission.
        :raises DoesNotExist: if no user exists with the provided login.
        :raises TokenExpired: is the token has expired.
        :raises ServerError: if an unpredicted exception occurred.
        """
        headers = self.create_default_header(token)
        url = self.url_for(f"/user/bylogin/{login}")
        response = self.requests.get(url, headers=headers)
        self.check_response_status(response, expected_status=200)
        return UserModel.parse_obj(response.json())

    def get_by_login_or_none(self, token: str, login: str) -> UserModel:
        """
        Get a single user by his login or none, if the user does not
        exist.

        :param str token: The authentification token
        :param str login: The login of the user to be looked up.
        :return: The found user or None, if nor user with the login exists
        :rtype: UserModel
        :raises InsufficientRights: If the requesting user has not the permission.
        :raises TokenExpired: is the token has expired.
        :raises ServerError: if an unpredicted exception occurred.
        """
        try:
            return self.get_by_login(token, login)
        except DoesNotExist:
            return None

    def filter(self, token, query: Query):

        response = self.requests.get(
            self.url_for("/users/filter/"),
            headers=self.create_default_header(token),
            params=query.build,
        )

        self.check_response_status(response, expected_status=200)
        return parse_obj_as(List[UserModel], response.json())

    def get_by_email(self, token: str, email: str) -> Optional[UserModel]:
        """
        Get a single user by his email, if existent.

        :Route: ``/user/byemail/{email}``
        :param str token: The authentification token
        :param str email: The email of the user to be looked up.
        :return: The found user
        :rtype: UserModel
        :raises InsufficientRights: If the requesting user has not the permission.
        :raises DoesNotExist: if no user exists with the provided login.
        :raises TokenExpired: is the token has expired.
        :raises ServerError: if an unpredicted exception occurred.
        """
        response = self.requests.get(
            self.url_for("/users/filter/email/"),
            headers=self.create_default_header(token),
            params={"v": email},
        )
        self.check_response_status(response, expected_status=200)
        users = parse_obj_as(List[UserModel], response.json())
        # TODO: len > 1 ?
        return users[0] if len(users) > 0 else None

    def get(self, token, user_id: int, fields: XFieldList = None) -> Optional[UserModel]:
        """
        Get a single user with the given id.

        :param str token: The authentification token.
        :param int user_id: The id of the requested user.
        :param XFieldList fields: The fields of the user, that should be returned.
        :return: The requested user.
        :rtype: :class:`UserModel`
        :raises InsufficientRights: If the requesting user has not the permission.
        :raises DoesNotExist: if no user exists with the provided login.
        :raises TokenExpired: is the token has expired.
        :raises ServerError: if an unpredicted exception occurred.
        """
        # user = self.cache.get_user(user_id)
        # if user is not None:
        #    logger.info("Cache hit for user %s", user.login)
        #    return user  # Cache hit

        # Cache miss
        headers = self.create_default_header(token, fields=fields)
        url = self.url_for(f"/user/{user_id}")
        response = self.requests.get(url, headers=headers)

        self.check_response_status(response, expected_status=200)
        user = UserModel.parse_obj(response.json())
        # self.cache.set_user(user)  # Cache the fetched user.
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

    def delete(self, token, user_id: int) -> Optional[UserModel]:
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

        return UserModel.parse_obj(result.json())

    def delete_all(self, token) -> None:
        """
        Delete all users from the database
        """
        headers = self.create_default_header(token)
        url = self.url_for("/users/")
        result = self.requests.delete(url, headers=headers)

        if result.status_code != 200:
            raise ServerError(f"Wrong status. Expected 200. Got {result.status_code}")

    def register(self, user: UserModel) -> UserModel:
        """
        Registers a new user.

        If the user cannot register, because the login or the the ameil are already in use,
        a `ConstraintViolation` exception is raised.

        The student role is added automaticall to the new user.

        :param UserModel user: The userdate for the new user.
        """
        data = user.json()
        url = self.url_for("/user/register/")
        result = self.requests.post(url, data=data)

        # Status 201: Ressource created
        if result.status_code == 201:
            response_data = result.json()
            user = UserModel.raw(response_data["user"])
            bearer_token_data = BearerTokenData.parse_obj(response_data["bearer_token_data"])

            # Not get the student role
            student_role = self.client.role_service.get_by_name_or_none(
                bearer_token_data.bearer_token, "student"
            )
            if student_role:
                self.add_role(bearer_token_data.bearer_token, user, student_role)
            return (
                user,
                bearer_token_data,
            )

        raise DigiCubeError(f"Something went wrong. Status {result.status_code}")

    def create(self, token: str, user: UserModelUpsert, fields: XFieldList = None) -> UserModel:
        """
        Creates a new user
        """
        headers = self.create_default_header(token, fields=fields)
        data = user.json()
        url = self.url_for("/users/")
        result = self.requests.post(url, data=data, headers=headers)

        if result.status_code == 201:
            # User created successfully. We cannot create the user directly
            # with the password, so we have to set the password in a second step.
            #
            # TODO: Why not able to set the password directly in the
            # REST call? Check is and change it, if possible.
            user_model = UserModel.parse_obj(result.json())
            if not user.password:
                logger.debug("Created user without password.")
            else:
                self.set_password(token=token, user_id=user_model.id, new_password=user.password)

            return user_model

        if result.status_code == 409:
            raise ConstraintViolation(result.text)

        if result.status_code == 500:
            raise ServerError(result.text)

        raise ServerError(f"Unknown error. [{result.status_code}] {result.text}")

    def get_verification_token(self, user_id: int) -> str:
        """
        Creates a new verification token for the user with the provided id.
        The verification token is valid for a certain amount of time. How
        long the token is valid is defined by the server. Check out the
        documentation to learn more about expirations times and how to
        configure them.

        :Route: /verify/user/{user_id}
        :Method: GET
        :param int id: The user id
        :return: The newly created token
        :rtype: str
        :raises InsufficientRights: If the requesting user has not the permission.
        :raises TokenExpired: is the token has expired.
        :raises ServerError: if an unpredicted exception occurred.
        """
        url = self.url_for(f"/verify/user/{user_id}")
        response = self.requests.get(url)
        data = response.json()
        return data["token"]

    def verify_user(self, token: str):
        """
        Verifies the user, that is connected to this token. If the token is
        valid and nor expired, the user, that belongs to this token, will be
        verified.

        :Route: /verify/user/{token}
        :Method: PUT
        :param str token: The verification token returned by ``get_verification_token``
        :return: The verified user.
        :rtype: :class:`UserModel`
        :raises InsufficientRights: If the requesting user has not the permission.
        :raises DoesNotExist: if the user connected to the token does not exist.
        :raises TokenExpired: is the token has expired.
        :raises ServerError: if an unpredicted exception occurred.
        """
        url = self.url_for(f"/verify/user/{token}")
        response = self.requests.put(url)
        data = response.json()

        return UserModel.parse_obj(data["user"]), data["token"]

    def update(self, token, user: UserModelUpsert) -> UserModel:
        """
        Update an existing user.
        If successfull, a new user model is returned with the latest version of the
        user data.
        """
        response = self.requests.put(
            self.url_for(f"/user/{user.id}"),
            data=user.json(),
            headers=self.create_default_header(token),
        )

        if response.status_code == 404:
            raise DoesNotExist(response.text)

        if response.status_code == 500:
            raise ServerError(response.text)

        if response.status_code != 200:
            raise ServerError(f"Wrong status. Expected 200. Got {response.status_code}")

        user = UserModel.parse_obj(response.json())

        # Add or update the cached user
        # self.cache.set_user(user)
        return user  # TODO Check other status_codes

    def get_rights(self, token: str, user_id: int) -> List[str]:
        """
        Get all rights. The rest method returns an array of right names
        and not json objects.
        """
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
        return user_rights

    def has_role(self, token, user: UserModel, role_name: str) -> bool:
        """
        Checks if the given user has the requested role. The role is specified
        by its name.
        """
        for role in self.get_my_roles(token, fields=["name"]):
            if role.name == role_name:
                return True
        return False

    def get_roles(self, token, user: UserModel) -> List[RoleModel]:
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

        return parse_obj_as(List[RoleModel], result.json())

    def add_role(self, token, user: UserModel, role: RoleModel) -> bool:
        """
        Adds a role to the user
        """
        headers = self.create_default_header(token)
        url = self.url_for(f"/user/{user.id}/role/{role.id}")
        result = self.requests.put(url, headers=headers)
        return result.status_code == 200

    def remove_role(self, token, user: UserModel, role: RoleModel) -> bool:
        """
        Remove a role from the user
        """
        headers = self.create_default_header(token)
        url = self.url_for(f"/user/{user.id}/role/{role.id}")
        result = self.requests.delete(url, headers=headers)
        return result.status_code == 200
