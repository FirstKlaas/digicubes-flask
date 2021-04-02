from datetime import datetime, date
from typing import Optional

import pydantic as pyd


class UnitModel(pyd.BaseModel):
    id: Optional[pyd.PositiveInt]
    created_at: Optional[datetime]
    modified_at: Optional[datetime]
    course_id: Optional[pyd.PositiveInt]
    name: Optional[pyd.constr(strip_whitespace=True, max_length=32)]
    position: Optional[int]
    is_active: Optional[bool]
    is_visible: Optional[bool]
    short_description: Optional[pyd.constr(strip_whitespace=True, max_length=64)]
    long_description: Optional[str]
