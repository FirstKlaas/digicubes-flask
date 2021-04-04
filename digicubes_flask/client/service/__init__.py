"""
Just importing the classes.
"""
from .abstract_service import AbstractService
from .right_service import RightService
from .role_service import RoleService
from .school_service import SchoolService
from .user_service import UserService

__all__ = ["AbstractService", "UserService", "RoleService", "RightService", "SchoolService"]
