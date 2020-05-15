import pickle
from typing import Optional, List

import redis

from digicubes_flask.client import proxy as p
from .cache import Cache


class RedisCache(Cache):
    def __init__(
        self,
        host: str = None,
        port: int = None,
        db: str = None,
        password: str = None,
        max_age: int = 1800,
    ):
        kwargs = {}

        if host is not None:
            kwargs["host"] = host

        if port is not None:
            kwargs["port"] = port

        if db is not None:
            kwargs["db"] = db

        if password is not None:
            kwargs["password"] = password

        self.max_age = int(max_age)

        self.redis = redis.Redis(**kwargs)

    def get_user(self, user_id: int) -> p.UserProxy:
        raw_data = self.redis.get(f"USER:{user_id}")
        return None if raw_data is None else pickle.loads(raw_data)

    def set_user(self, user: p.UserProxy):
        key = f"USER:{user.id}"
        self.redis.set(key, pickle.dumps(user), ex=self.max_age)

    def get_user_rights(self, user_id: int) -> Optional[List[str]]:
        raw_data = self.redis.get(f"USER:{user_id}:RIGHTS")
        return None if raw_data is None else pickle.loads(raw_data)

    def set_user_rights(self, user_id: int, rights: List[str]):
        key = f"USER:{user_id}:RIGHTS"
        self.redis.set(key, pickle.dumps(rights), ex=self.max_age)

    def get_user_roles(self, user_id: int) -> Optional[List[p.RoleProxy]]:
        raw_data = self.redis.get(f"USER:{user_id}:ROLES")
        return None if raw_data is None else pickle.loads(raw_data)

    def set_user_roles(self, user_id: int, roles: List[p.RoleProxy]):
        key = f"USER:{user_id}:ROLES"
        self.redis.set(key, pickle.dumps(roles), ex=self.max_age)

    def get_roles(self) -> List[p.RoleProxy]:
        raw_data = self.redis.get(f"ROLES")
        return None if raw_data is None else pickle.loads(raw_data)

    def set_roles(self, roles: List[p.RoleProxy]):
        self.redis.set("ROLES", pickle.dumps(roles), ex=self.max_age)
