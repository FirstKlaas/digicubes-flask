"""
The Admin Blueprint

All routes should be only accessible by users, who have the
role 'admin'
"""
import logging

from flask import Blueprint, redirect, render_template, request, url_for
from flask.helpers import flash

from digicubes_flask import digicubes, login_required
from digicubes_flask.client.model import RoleModel, SchoolModel, UserModel
from digicubes_flask.web.account_manager import DigicubesAccountManager

from .forms import SimpleTextForm
from .rfc import AdminRFC, RfcRequest

admin_blueprint = Blueprint("admin", __name__, template_folder="templates")

logger = logging.getLogger(__name__)

server: DigicubesAccountManager = digicubes


@admin_blueprint.route("/")
@login_required
def index():
    """The home/index route"""
    return render_template("admin/index.jinja")


@admin_blueprint.route("/roles/")
def roles():
    """
    Display all roles
    """
    role_list = digicubes.role.all(digicubes.token)
    return render_template("role/roles.jinja", roles=role_list)


@admin_blueprint.route("/user/<int:user_id>/addrole/<int:role_id>")
def add_user_role(user_id: int, role_id: int):
    server.user.add_role(server.token, UserModel(id=user_id), RoleModel(id=role_id, name=""))
    return redirect(url_for("user.update", user_id=user_id))


@admin_blueprint.route("/user/<int:user_id>/removerole/<int:role_id>")
def remove_user_role(user_id: int, role_id: int):
    server.user.remove_role(server.token, UserModel(id=user_id), RoleModel(id=role_id, name=""))
    return redirect(url_for("user.update", user_id=user_id))


@admin_blueprint.route("/rfc/", methods=("GET", "POST", "PUT"))
@login_required
def rfc():

    rfc_request = RfcRequest(request.headers.get("x-digicubes-rfcname", None), request.get_json())

    response = AdminRFC.call(rfc_request)
    return {"status": response.status, "text": response.text, "data": response.data}


@admin_blueprint.route("/school/<int:school_id>/addteacher/", methods=("GET", "POST"))
def school_add_teacher(school_id: int):

    form = SimpleTextForm()

    if form.is_submitted():
        if form.validate():
            login = form.login.data
            # Check if a user with the given login exists
            user = server.user.get_by_login_or_none(server.token, login)
            if user is None:
                flash("No such user")
            elif server.school.add_teacher(server.token, SchoolModel(id=school_id), user):
                flash("Teacher added successfully")
                return redirect(url_for('school.get', school_id=school_id))
            else:
                # Now lets see, if the user has not the right role.
                if server.user.has_role(server.token, user, "teacher"):
                    flash("Teacher not added. No reason.")
                else:
                    flash("User is not a teacher.")

    return render_template(
        "admin/school_add_teacher.jinja",
        form=form,
        action=url_for("admin.school_add_teacher", school_id=school_id),
        teacher=server.school.get_school_teacher(server.token, school_id),
    )
