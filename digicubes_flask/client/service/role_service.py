"""
All service calls for roles.
"""
from typing import List, Optional

from pydantic import parse_obj_as

from digicubes_flask.client.model import RightModel, RoleModel
from digicubes_flask.exceptions import DoesNotExist

from .abstract_service import AbstractService

RoleList = Optional[List[RoleModel]]


class RoleService(AbstractService):
    """
    All role services
    """

    def create(self, token, role: RoleModel) -> RoleModel:
        """
        Creates a new role.

        The parameter role contains the data for the new role. Not every attribute
        has to carry values. But at least all mandatory attributes must. If any
        model constraint is violated by the provided data, a ``ConstraintViolation``
        error will be raised. THe message of the error should give you a good indication
        what is wrong with the data.

        :param RoleModel role: The role you want to create. Be shure, that at least all
            non null attributes have meaningful values. Attributes like ``id``, ``created_at``
            and ``modified_at`` will be ignored.

        """
        headers = self.create_default_header(token)
        data = role.json()
        url = self.url_for("/roles/")
        response = self.requests.post(url, data=data, headers=headers)

        self.check_response_status(response, expected_status=201)
        return RoleModel.parse_obj(response.json())

    def all(self, token) -> List[RoleModel]:
        """
        Returns all roles

        The result is a list of ``RoleModel`` objects
        """
        cached_roles = self.cache.get_roles()
        if cached_roles is not None:
            return cached_roles

        headers = self.create_default_header(token)
        url = self.url_for("/roles/")
        response = self.requests.get(url, headers=headers)

        self.check_response_status(response)
        roles = parse_obj_as(List[RoleModel], response.json())
        self.cache.set_roles(roles)
        return roles

    def get(self, token, role_id: int) -> Optional[RoleModel]:
        """
        Get a single role.

        The requested role is specified by the ``id``.
        If the requested role was found, a ``RoleModel`` object
        will be returned. ``None`` otherwise.
        """
        headers = self.create_default_header(token)
        url = self.url_for(f"/role/{role_id}")
        response = self.requests.get(url, headers=headers)
        self.check_response_status(response)
        return RoleModel.parse_obj(response.json())

    def get_by_name(self, token: str, name: str) -> RoleModel:
        """
        Get a single role by the name.

        DoesNotExist exception is raised, if the role does
        not exist.

        :param str name: The name of the role.
        :return: The role
        :rtype: :class:`digicubes_flask.client.model.RoleModel`
        """
        headers = self.create_default_header(token)
        url = self.url_for(f"/role/byname/{name}")
        response = self.requests.get(url, headers=headers)
        self.check_response_status(response, expected_status=200)
        return RoleModel.parse_obj(response.json())

    def get_by_name_or_none(self, token: str, name: str) -> RoleModel:
        """
        Get a single role by the name.

        Returns None, if the role does
        not exist.
        """
        try:
            return self.get_by_name(token, name)
        except DoesNotExist:
            return None

    def delete(self, token, role_id: int) -> Optional[RoleModel]:
        """
        Deletes a role from the database
        """
        headers = self.create_default_header(token)
        url = self.url_for(f"/role/{role_id}")
        response = self.requests.delete(url, headers=headers)
        self.check_response_status(response)
        return RoleModel.parse_obj(response.json())

    def delete_all(self, token):
        """
        Removes all roles from the database.This operation is atomic.
        A successful operation is indicated by a 200 status.
        If the operation fails, a ``ServerError`` is thrown.

        .. warning:: This operation cannot be undone. So be shure you know, what you are doing.
        """
        headers = self.create_default_header(token)
        url = self.url_for("/roles/")
        response = self.requests.delete(url, headers=headers)
        self.check_response_status(response)

    def get_rights(self, token, role: RoleModel) -> List[RightModel]:
        """
        Get all rights assiciated with this role.
        """
        headers = self.create_default_header(token)
        url = self.url_for(f"/role/{role.id}/rights/")
        response = self.requests.get(url, headers=headers)
        self.check_response_status(response)
        return [RightModel.parse(right) for right in response.json()]
