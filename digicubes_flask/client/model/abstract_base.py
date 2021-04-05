from typing import Any, Union

import orjson
from pydantic import BaseModel

__all__ = ["DigiBaseModel", "orjson_dumps", "orjson_loads"]


def orjson_dumps(v, *, default):
    # orjson.dumps returns bytes, to match standard json.dumps we need to decode
    return orjson.dumps(v, default=default).decode()


def orjson_loads(obj: Union[bytes, bytearray, str]) -> Any:
    return orjson.loads(obj)


class DigiBaseModel(BaseModel):

    class Config:
        json_loads = orjson_loads
        json_dumps = orjson_dumps
