from datetime import date, datetime
from typing import Optional

import pydantic as pyd


class CourseModel(pyd.BaseModel):
    id: Optional[pyd.PositiveInt]
    created_at: Optional[datetime]
    modified_at: Optional[datetime]
    school_id: Optional[int]
    name: Optional[pyd.constr(strip_whitespace=True, max_length=32)]
    is_private: Optional[bool]
    description: Optional[str]
    created_by_id: Optional[int]
    from_date: Optional[date]
    until: Optional[date]
