from datetime import datetime
from typing import Optional

from pydantic import PositiveInt, constr

from .abstract_base import DigiBaseModel


class RightModel(DigiBaseModel):
    id: Optional[PositiveInt]
    created_at: Optional[datetime]
    modified_at: Optional[datetime]

    name: constr(strip_whitespace=True, max_length=32)
    description: Optional[constr(strip_whitespace=True, max_length=60)]
