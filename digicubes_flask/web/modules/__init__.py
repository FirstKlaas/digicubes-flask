""" Here we expose all known blueprints """

from .account.blueprint import account_service as account_blueprint
from .admin.blueprint import admin_blueprint
from .headmaster.blueprint import headmaster_service as headmaster_blueprint
from .teacher.blueprint import teacher_service as teacher_blueprint
from .student.blueprint import student_service as student_blueprint
from .blockly import blockly_blueprint
