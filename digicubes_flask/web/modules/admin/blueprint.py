"""
The Admin Blueprint

All routes should be only accessible by users, who have the
role 'admin'
"""
import logging
from datetime import date

from flask import Blueprint, render_template, abort, request, url_for, redirect

from digicubes_flask import login_required, needs_right, digicubes, current_user, CurrentUser
from digicubes_flask.web.account_manager import DigicubesAccountManager

from digicubes_common.exceptions import DigiCubeError
from digicubes_client.client.proxy import UserProxy, SchoolProxy, CourseProxy
from digicubes_client.client.service import SchoolService

from .forms import CreateSchoolForm, CreateUserForm, CreateCourseForm

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
        new_user = UserProxy(
            login=form.login.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
        )
        digicubes.user.create(digicubes.token, new_user)
        return redirect(url_for("admin.users"))

    return render_template("admin/create_user.jinja", form=form)


@admin_blueprint.route("/euser/<int:user_id>/")
@login_required
def edit_user(user_id: int):
    """Editing an existing user"""
    form = CreateUserForm()

    token = digicubes.token
    # Gettting the user details from the server
    # TODO: Was, wenn der User nicht existiert?
    user = digicubes.user.get(token, user_id)

    # Proxy is needed to request the roles
    user_proxy = UserProxy(id=user_id)

    # Getting the user roles from the server
    roles_list = digicubes.user.get_roles(token, user_proxy)

    # rights_list = account_manager.user.get_rights(token, user_proxy)

    return render_template("admin/edit_user.jinja", user=user, roles=roles_list, form=form)


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
    role_list = digicubes.role.all(digicubes.token)
    return render_template("admin/roles.jinja", roles=role_list)


@admin_blueprint.route("/rights/")
@needs_right("no_limits")
def rights():
    """
    Display all roles
    """
    rights_list = digicubes.right.all(digicubes.token)
    return render_template("admin/rights.jinja", rights=rights_list)


@admin_blueprint.route("/schools/")
@needs_right("no_limits")
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


@admin_blueprint.route("/eschool/<int:school_id>/")
@login_required
def edit_school(school_id: int):
    """Editing an existing school"""
    service: SchoolService = digicubes.school
    token = digicubes.token
    # Gettting the school details from the server
    # TODO: Was, wenn die Schule nicht existiert?
    school = service.get(token, school_id)
    courses = service.get_courses(digicubes.token, school)
    print('#'*80)
    print(courses)
    return render_template("admin/edit_school.jinja", school=school, courses=courses)


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
            )
        )

        return redirect(url_for("admin.edit_school", school_id=school_id))

    token: str = server.token
    school: SchoolProxy = server.school.get(token, school_id)
    return render_template("admin/create_course.jinja", school=school, form=form)
