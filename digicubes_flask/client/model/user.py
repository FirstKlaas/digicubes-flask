from typing import Optional, Text
from datetime import datetime

from pydantic import BaseModel, PositiveInt, constr

class UserModelUpsert(BaseModel):
    first_name: Optional[constr(strip_whitespace=True, max_length=20)]
    last_name: Optional[constr(strip_whitespace=True, max_length=20)]
    login: constr(strip_whitespace=True, max_length=20)
    email: constr(strip_whitespace=True, max_length=60)
    is_active: Optional[bool]
    is_verified: Optional[bool]
    password: Optional[Text]

class UserModel(BaseModel):
    id: Optional[PositiveInt]
    created_at: Optional[datetime]
    modified_at: Optional[datetime]
    verified_at: Optional[datetime]
    first_name: Optional[constr(strip_whitespace=True, max_length=20)]
    last_name: Optional[constr(strip_whitespace=True, max_length=20)]
    login: Optional[constr(strip_whitespace=True, max_length=20)]
    email: Optional[constr(strip_whitespace=True, max_length=60)]
    is_active: Optional[bool]
    is_verified: Optional[bool]
