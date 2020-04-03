"""
The Admin Blueprint

All routes should be only accessible by users, who have the
role 'admin'
"""
import logging
from flask import Blueprint, render_template, abort, request

from digicubes_flask import login_required, needs_right, account_manager
from digicubes_common.exceptions import DigiCubeError

from .forms import CreateUserForm

admin_blueprint = Blueprint("admin", __name__, template_folder="templates")

logger = logging.getLogger(__name__)


@admin_blueprint.route("/")
@login_required
def index():
    """The home/index route"""
    return render_template("index.jinja")


@admin_blueprint.route("/users/")
@login_required
def users():
    """The user list route."""
    user_list = account_manager.user.all(account_manager.token)
    return render_template("admin/users.jinja", users=user_list)

@admin_blueprint.route("/cuser/")
@login_required
def create_user():
    """Create a new user"""
    form = CreateUserForm()

    return render_template("admin/create_user.jinja", form=form)

@admin_blueprint.route("/panel/usertable/")
@login_required
def panel_user_table():
    """The user list route."""
    offset = request.args.get("offset", None)
    count = request.args.get("count", None)
    token = account_manager.token
    try:
        user_list = account_manager.user.all(token, offset=offset, count=count)
        return render_template("admin/panel/user_table.jinja", users=user_list)
    except DigiCubeError:
        abort(500)

@admin_blueprint.route("/right_test/")
@login_required
@needs_right("test_right")
def right_test():
    """
    This is just a test route to check, if the needs_right decorator works
    correctly.
    """
    return "YoLo"


@admin_blueprint.route("/roles/")
@needs_right("no_limits")
def roles():
    """
    Display all roles
    """
    role_list = account_manager.role.all(account_manager.token)
    return render_template("admin/roles.jinja", roles=role_list)

@admin_blueprint.route("/rights/")
@needs_right("no_limits")
def rights():
    """
    Display all roles
    """
    rights_list = account_manager.right.all(account_manager.token)
    return render_template("admin/rights.jinja", rights=rights_list)

@admin_blueprint.route("/schools/")
@needs_right("no_limits")
def schools():
    """
    Display all schools
    """
    school_list = account_manager.school.all(account_manager.token)
    return render_template("admin/schools.jinja", schools=school_list)
