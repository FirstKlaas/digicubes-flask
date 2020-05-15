from typing import Optional, List

from digicubes_flask.client import proxy as p


class Cache:
    def get_user_rights(self, user_id: int) -> Optional[List[str]]:
        return None

    def set_user_rights(self, user_id: int, rights: List[str]):
        pass

    def get_user(self, user_id: int) -> p.UserProxy:
        return None

    def set_user(self, user: p.UserProxy):
        pass

    def get_user_roles(self, user_id: int) -> Optional[List[p.RoleProxy]]:
        pass

    def set_user_roles(self, user_id: int, roles: List[p.RoleProxy]):
        pass

    def get_roles(self) -> List[p.RoleProxy]:
        return None

    def set_roles(self, roles: List[p.RoleProxy]):
        pass
