"""
The data representation of a role.
"""
from typing import Optional

import attr

from .abstract_proxy import AbstractProxy


@attr.s(auto_attribs=True)
class RoleProxy(AbstractProxy):
    """
    Represents a role.

    The ``id`` attribute is the primary key
    and cannot be changed.

    The ``name`` attribute is mandatory. All
    other fields are optional.
    """

    name: Optional[str]
    id: Optional[int] = None
    home_route: Optional[str] = ""
    description: Optional[str] = ""
    created_at: Optional[str] = None
    modified_at: Optional[str] = None
