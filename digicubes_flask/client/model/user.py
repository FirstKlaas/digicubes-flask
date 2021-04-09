from datetime import datetime
from typing import Optional, Text, List, TypeVar

import pydantic as pyd

USER = TypeVar("USER", bound="UserModel")
USERS = TypeVar("USERS", bound="UserListModel")


class UserModelUpsert(pyd.BaseModel):
    first_name: Optional[pyd.constr(strip_whitespace=True, max_length=20)]
    last_name: Optional[pyd.constr(strip_whitespace=True, max_length=20)]
    login: pyd.constr(strip_whitespace=True, max_length=20)
    email: pyd.constr(strip_whitespace=True, max_length=60)
    is_active: Optional[bool]
    is_verified: Optional[bool]
    password: Optional[Text]


class UserModel(pyd.BaseModel):
    id: Optional[pyd.PositiveInt]
    created_at: Optional[datetime]
    modified_at: Optional[datetime]
    verified_at: Optional[datetime]
    last_login_at: Optional[datetime]
    first_name: Optional[pyd.constr(strip_whitespace=True, max_length=20)]
    last_name: Optional[pyd.constr(strip_whitespace=True, max_length=20)]
    login: Optional[pyd.constr(strip_whitespace=True, max_length=20)]
    email: Optional[pyd.constr(strip_whitespace=True, max_length=60)]
    is_active: Optional[bool]
    is_verified: Optional[bool]

    @staticmethod
    def list_model(users: List[USER]) -> USERS:
        return UserModel(__root__=users)


class UserListModel(pyd.BaseModel):
    __root__: List[UserModel]
