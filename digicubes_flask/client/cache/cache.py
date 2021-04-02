from typing import Optional, List

from digicubes_flask.client.model import UserModel, RoleModel


class Cache:
    def get_user_rights(self, user_id: int) -> Optional[List[str]]:
        return None

    def set_user_rights(self, user_id: int, rights: List[str]):
        pass

    def get_user(self, user_id: int) -> UserModel:
        return None

    def set_user(self, user: UserModel):
        pass

    def get_user_roles(self, user_id: int) -> Optional[List[RoleModel]]:
        pass

    def set_user_roles(self, user_id: int, roles: List[RoleModel]):
        pass

    def get_roles(self) -> List[RoleModel]:
        return None

    def set_roles(self, roles: List[RoleModel]):
        pass
