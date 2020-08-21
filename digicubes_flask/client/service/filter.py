from enum import IntEnum
from typing import Any, Dict


class FilterFunction(IntEnum):

    EQUALS = 0
    IEQUALS = 1
    STARTSWITH = 2
    ISTARTSWITH = 3
    ENDSWITH = 4
    IENDSWITH = 5
    CONTAINS = 6
    ICONTAINS = 7

    def __str__(self):
        return FilterFunction.to_name(self.value)

    @staticmethod
    def to_name(i: int):
        return [
            None,
            "iequals",
            "startswith",
            "istartswith",
            "endswith",
            "iendswith",
            "contains",
            "icontains",
        ][i]

    def build(self, attribute: str):
        return (
            attribute
            if self == FilterFunction.EQUAL
            else f"{attribute}__{FilterFunction.to_name(self.value)}"
        )


class Query:
    def __init__(self):
        self._filter_elems = []
        self._specials = []
        self._columns = []
        self._page = None
        self._order_by = []

    def order_by(self, *attributes):
        self._order_by = attributes
        return self

    def count(self):
        self._specials.append("count")
        return self

    def columns(self, *fields):
        self._columns = fields
        return self

    def first(self):
        self._specials.append("first")
        return self

    def page(self, offset: int, limit: int):
        self._page = (offset, limit)
        return self

    def add_filter(self, attribute: str, filter_function: FilterFunction, value: Any):
        self._filter_elems.append((attribute, filter_function, value))
        return self

    def build(self) -> Dict[str, Any]:
        result = {}
        if len(self._specials) > 0:
            result["s"] = ",".join(self._specials)

        if len(self._order_by) > 0:
            result["o"] = ",".join(self._order_by)

        if len(self._columns) > 0:
            result["c"] = ",".join(self._columns)

        if len(self._filter_elems) > 0:
            filter_defs = []
            for elem in self._filter_elems:
                print(elem)
                filter_defs.append(f"{elem[0]},{int(elem[1])},{elem[2]}")
            result["f"] = ":".join(filter_defs)

        return result

    def _asdict(self):
        return self.build_query()
