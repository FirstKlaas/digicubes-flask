"""
All serice calls for rights
"""
from typing import List, Optional

from digicubes_flask.exceptions import ConstraintViolation, ServerError, DoesNotExist
from digicubes_flask.client.model import RightModel, RoleModel

from .abstract_service import AbstractService

RightList = List[RightModel]


class RightService(AbstractService):
    """
    The rights service
    """

    def create(self, token, right: RightModel) -> RightModel:
        """
        Creates a new right
        """
        headers = self.create_default_header(token)
        data = right.json()
        url = self.url_for("/rights/")
        result = self.requests.post(url, json=data, headers=headers)

        if result.status_code == 201:
            return RightModel.parse_raw(result.json())

        if result.status_code == 409:
            raise ConstraintViolation(result.text)

        if result.status_code == 500:
            raise ServerError(result.text)

        raise ServerError(f"Unknown error. [{result.status_code}] {result.text}")

    def create_multiple(self, token, rights: RightList):
        """
        Creates a set of rights and returns a list of created
        right proxies. The creation of the rights is not an atomic
        operation.
        """
        # TODO: Maybe e could do this as an parallel async operation
        # TODO: Also we should return two sets. One for the successfully
        # created and one for the failed.
        return [self.create(token, right) for right in rights]

    def all(self, token) -> RightList:
        """
        Returns all rigths.
        The result is a list of ``RightModel`` objects.
        """
        headers = self.create_default_header(token)
        url = self.url_for("/rights/")
        result = self.requests.get(url, headers=headers)

        if result.status_code == 404:
            return []

        return [RightModel.parse_raw(right) for right in result.json()]

    def get(self, token, right_id: int) -> Optional[RightModel]:
        """
        Get a single right by id
        """
        headers = self.create_default_header(token)
        url = self.url_for(f"/right/{right_id}")
        result = self.requests.get(url, headers=headers)
        if result.status_code == 404:
            return None

        if result.status_code == 200:
            return RightModel.parse_raw(result.json())

        return None

    def delete_all(self, token):
        """
        Delete all digicube rights. This operation is atomic.
        A successful operation is indicated by a 200 status.
        If the operation fails, a ``ServerError`` is thrown.

        .. warning:: This operation cannot be undone. So be shure you know, what you are doing.

        """
        headers = self.create_default_header(token)
        url = self.url_for("/rights/")
        result = self.requests.delete(url, headers=headers)
        if result.status_code != 200:
            raise ServerError(result.text)

    def get_roles(self, token, right: RightModel) -> List[RoleModel]:
        # TODO: Use Filter fields
        """
        Get all roles associated with this right
        """
        headers = self.create_default_header(token)
        url = self.url_for(f"/right/{right.id}/roles/")
        result = self.requests.get(url, headers=headers)

        if result.status_code == 404:
            raise DoesNotExist(result.text)

        if result.status_code == 200:
            return [RoleModel.parse_raw(role) for role in result.json()]

        raise ServerError(result.text)

    def add_role(self, token, right: RightModel, role: RoleModel) -> bool:
        """
        Add a role to this right. The role and the right must exist.
        If not, a DoesNotExist error is raised.
        """
        headers = self.create_default_header(token)
        url = self.url_for(f"/right/{right.id}/role/{role.id}")
        result = self.requests.put(url, headers=headers)
        if result.status_code == 404:
            raise DoesNotExist(result.text)

        return result.status_code == 200

    def remove_role(self, token, right: RightModel, role: RoleModel) -> bool:
        """
        Removes a role from this right. Both, the role and the right must exist.
        If not, a ``DoesNotExist`` exception is thrown.
        """
        response = self.requests.delete(
            self.url_for(f"/right/{right.id}/role/{role.id}"),
            headers=self.create_default_header(token),
        )

        if response.status_code == 200:
            return True

        if response.status_code == 404:
            raise DoesNotExist(response.text)

        return False

    def clear_roles(self, token, right: RightModel) -> bool:
        """
        Clears all roles from the right. After a succesful call no
        role is associated with this right. The right must exist.
        At least the id of the right has to be set.

        :param RightModel right: The right, where the roles should be cleared.

        :return bool: True, if the operation was successful, False else.
        """
        response = self.requests.delete(
            self.url_for(f"/right/{right.id}/roles/"), headers=self.create_default_header(token)
        )

        if response.status_code == 200:
            return True

        if response.status_code == 404:
            raise DoesNotExist(response.text)

        return False
