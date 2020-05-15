"""
Abstract proxy class

Proxies are pure data containers, that represent orm objects of the server.
Proxies van be converted to json representation as well as created from
a json representation.

The ``AbstractProxy`` just defines the two methos for serialization
and deserialization.
"""
import datetime
from typing import Any, Dict, List, Optional

import cattr
from cattr import register_structure_hook, register_unstructure_hook

THeader = Dict[str, str]
TFields = Optional[List[str]]
TStructuredData = Dict[str, Any]


def unstructure_hook_date(d: datetime.date):
    """
        Converts a string to an datetime object.
        The string is expected to have the following
        format: yyyy-mm-dd. (ISO format)

        It is used by cattr to convert json responses
        to corresponding data structures.
    """
    return d.isoformat()


def unstructure_hook_datetime(d: datetime.datetime):
    """
        Converts a string to an datetime object.
        The string is expected to have the following
        format: yyyy-mm-dd. (ISO format)

        It is used by cattr to convert json responses
        to corresponding data structures.
    """
    return d.isoformat()


def structure_hook_date(s: str, t):
    """
        Converts a string to an datetime object.
        The string is expected to have the following
        format: yyyy-mm-dd. (ISO format)

        It is used by cattr to convert json responses
        to corresponding data structures.
    """
    return datetime.date.fromisoformat(s)


def structure_hook_datetime(s: str, t):
    """
        Converts a string to an datetime object.
        The string is expected to have the following
        format: yyyy-mm-dd. (ISO format)

        It is used by cattr to convert json responses
        to corresponding data structures.
    """
    return datetime.datetime.fromisoformat(s)


register_unstructure_hook(datetime.date, unstructure_hook_date)
register_unstructure_hook(datetime.datetime, unstructure_hook_datetime)
register_structure_hook(datetime.date, structure_hook_date)
register_structure_hook(datetime.datetime, structure_hook_datetime)


class AbstractProxy:
    """
    An abstract proxy class
    """

    @staticmethod
    def set_filter_fields_header(
        headers: Optional[THeader] = None, fields: TFields = None  # pylint: disable=C0330
    ) -> THeader:
        """
        Set the X-Filter-Fields header. If fields is None, no header is set.
        """
        if headers is None:
            raise ValueError("No header provided")

        if fields is not None:
            headers["X-Filter-Fields"] = ",".join(fields)

        return headers

    @classmethod
    def structure(cls, data: TStructuredData) -> Any:
        """
        This class method creates an instance of this class
        based on the provided data. The data object must
        have at least the attributes defined by the class.
        """
        return cattr.structure(data, cls)

    def unstructure(self, exclude_nones: bool = True) -> TStructuredData:
        """
        Creates a json representation of this instance.

        If the parameter ``exclude_nones`` is ``True``,
        attributes that have a ``None`` value are omitted.

        The default is ``True``.

        :param exclude_nones bool:
            Should atttributes with None value be excluded
            from the result?

        """
        if not exclude_nones:
            return cattr.unstructure(self)

        return {k: v for k, v in cattr.unstructure(self).items() if v is not None}
