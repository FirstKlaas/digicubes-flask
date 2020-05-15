"""
The data representation of a school.
"""
from datetime import date

from typing import Optional
import attr
from .abstract_proxy import AbstractProxy


@attr.s(auto_attribs=True)
class SchoolProxy(AbstractProxy):
    """
    Represents a school.
    """

    id: Optional[int] = None
    name: Optional[str] = None
    created_at: Optional[str] = None
    modified_at: Optional[str] = None
    description: Optional[str] = None


@attr.s(auto_attribs=True)
class CourseProxy(AbstractProxy):
    """
    Represents a school.
    """

    id: Optional[int] = None
    name: Optional[str] = None
    is_private: Optional[bool] = None
    school_id: Optional[int] = None
    created_by_id: Optional[int] = None
    description: Optional[str] = None
    from_date: Optional[date] = None
    until_date: Optional[date] = None
    created_at: Optional[str] = None
    modified_at: Optional[str] = None

    def to_json_dict(self):

        data = self.unstructure()
        data["from_date"] = self.from_date.isoformat()
        data["until_date"] = self.until_date.isoformat()
        return data


@attr.s(auto_attribs=True)
class UnitProxy(AbstractProxy):
    id: Optional[int] = None
    name: Optional[str] = None
    position: Optional[int] = None

    is_active: Optional[bool] = None
    is_visible: Optional[bool] = None

    short_description: Optional[str] = None
    long_description: Optional[str] = None
