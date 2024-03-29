"""
Here we imort all known blueprints and offer one central
method to register these blueprints. All blueprints need
to have there own url_prefix already set."""
import logging

from flask import Flask

from .account import account_service as account_blueprint
from .admin import admin_blueprint
from .blockly import blockly_blueprint
from .course import blueprint as course_blueprint
from .headmaster import headmaster_blueprint
from .right import blueprint as right_blueprint
from .school import blueprint as school_blueprint
from .student import student_blueprint
from .teacher import teacher_blueprint
from .unit import unit_service as unit_blueprint
from .user import blueprint as user_blueprint

__all__ = ["register_blueprints"]

logger = logging.getLogger(__name__)

blueprints = [
    admin_blueprint,
    account_blueprint,
    blockly_blueprint,
    headmaster_blueprint,
    school_blueprint,
    course_blueprint,
    unit_blueprint,
    user_blueprint,
    right_blueprint,
    student_blueprint,
    teacher_blueprint,
]


def register_blueprints(app: Flask) -> None:
    """
    Register all known blueprints with the given flask app.
    """
    for blueprint in blueprints:
        logger.info("Register blueprint at %s", blueprint.url_prefix)
        app.register_blueprint(blueprint)
