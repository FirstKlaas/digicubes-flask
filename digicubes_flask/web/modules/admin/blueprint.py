"""
The Admin Blueprint

All routes should be only accessible by users, who have the
role 'admin'
"""
import logging
from datetime import date
from typing import List
from flask import Blueprint, render_template, abort, request, url_for, redirect

from digicubes_flask import login_required, needs_right, digicubes, current_user, CurrentUser
from digicubes_flask.web.account_manager import DigicubesAccountManager

from digicubes_common.exceptions import DigiCubeError
from digicubes_client.client.proxy import UserProxy, SchoolProxy, CourseProxy, RoleProxy
from digicubes_client.client.service import SchoolService, UserService

from .forms import CreateSchoolForm, CreateUserForm, CreateCourseForm, UpdateUserForm
from .rfc import AdminRFC, RfcResponse, RfcRequest

admin_blueprint = Blueprint("admin", __name__, template_folder="templates")

logger = logging.getLogger(__name__)

server: DigicubesAccountManager = digicubes
user: CurrentUser = current_user


@admin_blueprint.route("/")
@login_required
def index():
    """The home/index route"""
    return render_template("admin/index.jinja")


@admin_blueprint.route("/users/")
@login_required
def users():
    """The user list route."""
    user_list = digicubes.user.all(digicubes.token)
    return render_template("admin/users.jinja", users=user_list)


@admin_blueprint.route("/cuser/", methods=("GET", "POST"))
@login_required
def create_user():
    """Create a new user"""
    form = CreateUserForm()
    if form.validate_on_submit():
        new_user = UserProxy()
        form.populate_obj(new_user)
        new_user = digicubes.user.create(digicubes.token, new_user)
        return redirect(url_for("admin.edit_user", user_id=new_user.id))

    return render_template("admin/create_user.jinja", form=form)


@admin_blueprint.route("/uuser/<int:user_id>/", methods=("GET", "POST"))
@login_required
def update_user(user_id: int):
    service: UserService = digicubes.user
    token = digicubes.token
    form = UpdateUserForm()

    if form.validate_on_submit():
        user_proxy = UserProxy(id=user_id)
        form.populate_obj(user_proxy)
        digicubes.user.update(token, user_proxy)
        return redirect(url_for("admin.edit_user", user_id=user_id))

    user_proxy: UserProxy = service.get(token, user_id)
    form.process(obj=user_proxy)

    return render_template("admin/update_user.jinja", form=form, user=user_proxy)


@admin_blueprint.route("/duser/<int:user_id>/")
@login_required
def delete_user(user_id: int):
    """Delete an existing user"""
    token = digicubes.token
    # Gettting the school details from the server
    # TODO: Was, wenn das Objekt nicht existiert?
    digicubes.user.delete(token, user_id)
    return redirect(url_for("admin.users"))


@admin_blueprint.route("/euser/<int:user_id>/")
@login_required
def edit_user(user_id: int):
    """Editing an existing user"""
    form = CreateUserForm()

    token = server.token
    # Gettting the user details from the server
    # TODO: Was, wenn der User nicht existiert?
    user: UserProxy = server.user.get(token, user_id)

    # Proxy is needed to request the roles
    user_proxy = UserProxy(id=user_id)

    # Getting the user roles from the server
    user_roles_names = [role.name for role in server.user.get_roles(token, user_proxy)]
    all_roles = server.role.all(token)

    role_list = [(role, role.name in user_roles_names) for role in all_roles]
    return render_template("admin/user.jinja", user=user, roles=role_list, form=form)


@admin_blueprint.route("/panel/usertable/")
@login_required
def panel_user_table():
    """The user list route."""
    offset = request.args.get("offset", None)
    count = request.args.get("count", None)
    token = digicubes.token
    try:
        user_list = digicubes.user.all(token, offset=offset, count=count)
        return render_template("admin/panel/user_table.jinja", users=user_list)
    except DigiCubeError:
        abort(500)


@admin_blueprint.route("/right_test/")
@login_required
def right_test():
    """
    This is just a test route to check, if the needs_right decorator works
    correctly.
    """
    return "YoLo"


@admin_blueprint.route("/roles/")
def roles():
    """
    Display all roles
    """
    role_list = digicubes.role.all(digicubes.token)
    return render_template("admin/roles.jinja", roles=role_list)


@admin_blueprint.route("/user/<int:user_id>/addrole/<int:role_id>")
def add_user_role(user_id: int, role_id: int):
    server.user.add_role(server.token, UserProxy(id=user_id), RoleProxy(id=role_id, name=""))
    return redirect(url_for("admin.edit_user", user_id=user_id))


@admin_blueprint.route("/user/<int:user_id>/removerole/<int:role_id>")
def remove_user_role(user_id: int, role_id: int):
    server.user.remove_role(server.token, UserProxy(id=user_id), RoleProxy(id=role_id, name=""))
    return redirect(url_for("admin.edit_user", user_id=user_id))


@admin_blueprint.route("/rights/")
def rights():
    """
    Display all roles
    """
    rights_list = digicubes.right.all(digicubes.token)
    return render_template("admin/rights.jinja", rights=rights_list)


@admin_blueprint.route("/schools/")
def schools():
    """
    Display all schools
    """
    school_list = digicubes.school.all(digicubes.token)
    return render_template("admin/schools.jinja", schools=school_list)


@admin_blueprint.route("/cschool/", methods=("GET", "POST"))
@login_required
def create_school():
    """Create a new school"""
    # token = digicubes.token
    form = CreateSchoolForm()
    if form.validate_on_submit():
        new_school = SchoolProxy(name=form.name.data, description=form.description.data,)
        digicubes.school.create(digicubes.token, new_school)
        return redirect(url_for("admin.schools"))

    return render_template("admin/create_school.jinja", form=form)


@admin_blueprint.route("/school/<int:school_id>/")
@login_required
def school(school_id: int):
    """Schow details of an existing school"""
    service: SchoolService = digicubes.school
    token = digicubes.token
    # Gettting the school details from the server
    # TODO: Was, wenn die Schule nicht existiert?
    db_school = service.get(token, school_id)
    courses = service.get_courses(digicubes.token, db_school)
    return render_template("admin/school.jinja", school=db_school, courses=courses)


@admin_blueprint.route("/uschool/<int:school_id>/", methods=("GET", "POST"))
@login_required
def update_school(school_id: int):
    service: SchoolService = digicubes.school
    token = digicubes.token
    form = CreateSchoolForm()

    if form.validate_on_submit():
        digicubes.school.update(
            token, SchoolProxy(id=school_id, name=form.name.data, description=form.description.data)
        )

        return redirect(url_for("admin.school", school_id=school_id))

    # Gettting the school details from the server
    # TODO: Was, wenn die Schule nicht existiert?
    db_school: SchoolProxy = service.get(token, school_id)
    form.name.data = db_school.name
    form.description.data = db_school.description

    return render_template("admin/update_school.jinja", form=form, school=db_school)


@admin_blueprint.route("/dschool/<int:school_id>/")
@login_required
def delete_school(school_id: int):
    """Delete an existing school"""
    token = digicubes.token
    # Gettting the school details from the server
    # TODO: Was, wenn die Schule nicht existiert?
    digicubes.school.delete(token, school_id)
    return redirect(url_for("admin.schools"))


@admin_blueprint.route("/school/<int:school_id>/ccourse/", methods=("GET", "POST"))
@login_required
def create_school_course(school_id: int):
    """Create a new course for the school"""

    def create_date_from_string(d: str) -> date:
        values = d.split(".")
        return date(int(values[2]), int(values[1]), int(values[0]))

    form = CreateCourseForm()
    if form.validate_on_submit():
        from_date = (
            date.today()
            if not form.from_date.data
            else create_date_from_string(form.from_date.data)
        )

        until_date = (
            date.today()
            if not form.until_date.data
            else create_date_from_string(form.until_date.data)
        )

        course = server.school.create_course(
            server.token,
            SchoolProxy(id=school_id),
            CourseProxy(
                name=form.name.data,
                description=form.description.data,
                is_private=form.is_private.data,
                from_date=from_date,
                until_date=until_date,
                created_by_id=user.id,
            ),
        )

        return redirect(url_for("admin.school", school_id=school_id))

    token: str = server.token
    school_proxy: SchoolProxy = server.school.get(token, school_id)
    return render_template("admin/create_course.jinja", school=school_proxy, form=form)


@admin_blueprint.route("/rfc/", methods=("GET", "POST", "PUT"))
@login_required
def rfc():

    rfc_request = RfcRequest(
        request.headers.get("x-digicubes-rfcname", None),
        request.get_json()
    )

    response = AdminRFC.call(rfc_request)
    return {
        "status": response.status,
        "text": response.text,
        "data": response.data}
