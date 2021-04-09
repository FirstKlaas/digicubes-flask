from datetime import datetime
from typing import List, Optional, TypeVar

from pydantic import PositiveInt, constr

from .abstract_base import DigiBaseModel

RIGHT = TypeVar("RIGHT", bound="RightModel")
RIGHTS = TypeVar("RIGHTS", bound="RightListModel")


class RightModel(DigiBaseModel):
    id: Optional[PositiveInt]
    created_at: Optional[datetime]
    modified_at: Optional[datetime]

    name: constr(strip_whitespace=True, max_length=32)
    description: Optional[constr(strip_whitespace=True, max_length=60)]

    @staticmethod
    def list_model(rights: List[RIGHT]) -> RIGHTS:
        return RightModel(__root__=rights)


class RightListModel(DigiBaseModel):
    __root__: List[RightModel]
