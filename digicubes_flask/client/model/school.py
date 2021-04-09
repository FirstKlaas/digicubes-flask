from datetime import datetime
from typing import List, Optional, TypeVar

import pydantic as pyd

SCHOOL = TypeVar("SCHOOL", bound="SchoolModel")
SCHOOLS = TypeVar("SCHOOLS", bound="SchoolListModel")


class SchoolModel(pyd.BaseModel):
    id: Optional[pyd.PositiveInt]
    created_at: Optional[datetime]
    modified_at: Optional[datetime]
    name: Optional[pyd.constr(strip_whitespace=True, max_length=32)]
    description: Optional[str]

    @staticmethod
    def list_model(schools: List[SCHOOL]) -> SCHOOLS:
        return SchoolListModel(__root__=schools)


class SchoolListModel(pyd.BaseModel):
    __root__: List[SchoolModel]
