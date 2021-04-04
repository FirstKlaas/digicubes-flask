from datetime import datetime
from typing import Optional

import pydantic as pyd


class RightModel(pyd.BaseModel):
    id: Optional[pyd.PositiveInt]
    created_at: Optional[datetime]
    modified_at: Optional[datetime]

    name: pyd.constr(strip_whitespace=True, max_length=32)
    description: Optional[pyd.constr(strip_whitespace=True, max_length=60)]
