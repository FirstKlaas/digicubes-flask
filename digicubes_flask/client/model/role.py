from datetime import datetime
from typing import Optional

from pydantic import BaseModel, constr, PositiveInt


class RoleModel(BaseModel):
    id: Optional[PositiveInt]
    created_at: Optional[datetime]
    modified_at: Optional[datetime]
    home_route: Optional[constr(strip_whitespace=True, max_length=40)]
    name: constr(strip_whitespace=True, max_length=32)
    description: Optional[constr(strip_whitespace=True, max_length=60)]
