"""
The data representation of a user.
"""
from copy import copy
from typing import Optional
import attr
from .abstract_proxy import AbstractProxy


@attr.s(auto_attribs=True)
class UserProxy(AbstractProxy):
    """
    Represents a user.

    :param int id: The ``id`` attribute is the primary key and
        cannot be changed.

    :param str login: The ``login`` attribute is mandatory.
        The login must be unique. All other fields are optional.

    :param str email: A valid email for the user
    """

    login: Optional[str] = None
    password: Optional[str] = None
    id: Optional[int] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    verified_at: Optional[str] = None
    created_at: Optional[str] = None
    modified_at: Optional[str] = None
    last_login_at: Optional[str] = None

    def is_hollow(self):
        """Check, if the user is hollow.
        A hollow user is a user, that is not
        stored in the database and represents
        a kind of None user."""
        return self.id is None or self.id < 0

    def copy(self):
        """Creates a shallow copy of this instance"""
        return copy(self)

    @staticmethod
    def create_hollow():
        """Create a hollow user instance"""
        return UserProxy(id=-1)
