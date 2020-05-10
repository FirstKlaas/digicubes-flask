"""
The Admin Blueprint

All routes should be only accessible by users, who have the
role 'admin'
"""
import logging

from flask import Blueprint, render_template, abort, request, url_for, redirect, flash

from digicubes_common import exceptions as ex
from digicubes_client.client import proxy, service as srv

from digicubes_flask import login_required, digicubes, current_user, CurrentUser
from digicubes_flask.web.account_manager import DigicubesAccountManager
from digicubes_flask.email import mail_cube

from .forms import (
    SchoolForm,
    UserForm,
    CourseForm,
    SchoolNameAvailable,
    UserLoginAvailable,
    SetPasswordForm,
)

from .rfc import AdminRFC, RfcRequest

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
    form = UserForm()
    if form.is_submitted():
        if form.validate({"login": [UserLoginAvailable()]}):
            new_user = proxy.UserProxy()
            form.populate_obj(new_user)

            # When users are created by an admin,
            # he decides, whether the user is verified or not.
            # if current_app.config.get("auto_verify", False):
            #    new_user.is_verified = True
            new_user = digicubes.user.create(digicubes.token, new_user)
            flash(f"User {new_user.login} successfully created")
            if not new_user.is_verified:
                # Newly created user is not verified. Now sending him an
                # email with a verification link.
                if mail_cube.is_enabled:
                    try:
                        mail_cube.send_verification_email(new_user)
                    except ex.DigiCubeError:
                        logger.exception("Sending a verification email failed.")
                else:
                    link = mail_cube.create_verification_link(new_user)
                    return render_template(
                        "admin/send_verification_link.jinja", user=new_user, link=link
                    )

            return redirect(url_for("admin.edit_user", user_id=new_user.id))

    # Form not submitted or validation failed.
    form.submit.label.text = "Create"
    action = url_for("admin.create_user")
    return render_template("admin/create_user.jinja", form=form, action=action)


@admin_blueprint.route("/verify/renew/<int:user_id>/")
def verify_renew(user_id: int):
    service: srv.UserService = digicubes.user
    token = digicubes.token
    user_proxy: proxy.UserProxy = service.get(token, user_id)
    link = mail_cube.create_verification_link(user_proxy)
    return render_template("admin/send_verification_link.jinja", user=user_proxy, link=link)


@admin_blueprint.route("/uuser/<int:user_id>/", methods=("GET", "POST"))
@login_required
def update_user(user_id: int):
    """
    Route to update an existing user.
    """
    service: srv.UserService = digicubes.user
    token = digicubes.token
    form = UserForm()
    user_proxy: proxy.UserProxy = service.get(token, user_id)

    if form.is_submitted():
        if form.validate({"login": [UserLoginAvailable(user_id=user_id)]}):
            user_proxy = proxy.UserProxy(id=user_id)
            form.populate_obj(user_proxy)
            digicubes.user.update(token, user_proxy)
            return redirect(url_for("admin.edit_user", user_id=user_id))
    else:
        form.process(obj=user_proxy)

    return render_template(
        "admin/update_user.jinja",
        form=form,
        user=user_proxy,
        action=url_for("admin.update_user", user_id=user_id),
    )


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
    """Display detaild information for an existing user"""
    token = server.token
    # Getting the user details from the server
    user_proxy: proxy.UserProxy = server.user.get(token, user_id)

    # Getting the user roles from the server
    user_roles_names = [role.name for role in server.user.get_roles(token, user_proxy)]
    all_roles = server.role.all(token)

    role_list = [(role, role.name in user_roles_names) for role in all_roles]
    return render_template("admin/user.jinja", user=user_proxy, roles=role_list)


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
    except ex.DigiCubeError:
        abort(500)


@admin_blueprint.route("/roles/")
def roles():
    """
    Display all roles
    """
    role_list = digicubes.role.all(digicubes.token)
    return render_template("admin/roles.jinja", roles=role_list)


@admin_blueprint.route("/user/<int:user_id>/addrole/<int:role_id>")
def add_user_role(user_id: int, role_id: int):
    server.user.add_role(
        server.token, proxy.UserProxy(id=user_id), proxy.RoleProxy(id=role_id, name="")
    )
    return redirect(url_for("admin.edit_user", user_id=user_id))


@admin_blueprint.route("/user/<int:user_id>/removerole/<int:role_id>")
def remove_user_role(user_id: int, role_id: int):
    server.user.remove_role(
        server.token, proxy.UserProxy(id=user_id), proxy.RoleProxy(id=role_id, name="")
    )
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
    form = SchoolForm()
    if form.is_submitted():
        if form.validate({"name": [SchoolNameAvailable()]}):
            new_school = proxy.SchoolProxy(name=form.name.data, description=form.description.data,)
            digicubes.school.create(digicubes.token, new_school)
            return redirect(url_for("admin.schools"))

    form.submit.label.ttext = "Create"
    return render_template(
        "admin/create_school.jinja", form=form, action=url_for("admin.create_school")
    )


@admin_blueprint.route("/school/<int:school_id>/")
@login_required
def school(school_id: int):
    """Schow details of an existing school"""
    service: srv.SchoolService = digicubes.school
    token = digicubes.token
    # Gettting the school details from the server
    # TODO: Was, wenn die Schule nicht existiert?
    db_school = service.get(token, school_id)
    courses = service.get_courses(digicubes.token, db_school)
    teacher = service.get_school_teacher(digicubes.token, school_id)
    return render_template("admin/school.jinja", school=db_school, courses=courses, teacher=teacher)


@admin_blueprint.route("/uschool/<int:school_id>/", methods=("GET", "POST"))
@login_required
def update_school(school_id: int):
    service: srv.SchoolService = digicubes.school
    token = digicubes.token
    form = SchoolForm()
    db_school: proxy.SchoolProxy = service.get(token, school_id)

    # What about the creation date and the modified date?
    if form.is_submitted():
        if form.validate({"name": [SchoolNameAvailable(school_id=school_id)]}):
            upschool = proxy.SchoolProxy()
            form.populate_obj(upschool)
            upschool.id = school_id
            digicubes.school.update(token, upschool)

            return redirect(url_for("admin.school", school_id=school_id))
    else:
        # This is the request to display the form with
        # the current data ofthe school
        form = SchoolForm(obj=db_school)

    form.submit.label.text = "Update"

    return render_template(
        "admin/update_school.jinja",
        form=form,
        school=db_school,
        action=url_for("admin.update_school", school_id=db_school.id),
    )


@admin_blueprint.route("/dschool/<int:school_id>/")
@login_required
def delete_school(school_id: int):
    """Delete an existing school"""
    token = digicubes.token
    # Gettting the school details from the server
    # TODO: Was, wenn die Schule nicht existiert?
    digicubes.school.delete(token, school_id)
    return redirect(url_for("admin.schools"))


@admin_blueprint.route("/school/<int:school_id>/dcourse/<int:course_id>/")
def delete_course(school_id: int, course_id: int):
    """
    Delete an existing course.
    """
    token = digicubes.token
    service: srv.SchoolService = digicubes.school

    # Deleteing the course
    # TODO: catch 404
    try:
        service.delete_course(token, course_id)
    except ex.NotAuthenticated:
        return redirect(url_for("admin.login"))

    return redirect(url_for("admin.school", school_id=school_id))


@admin_blueprint.route("/school/<int:school_id>/ucourse/<int:course_id>/", methods=["GET", "POST"])
@login_required
def update_school_course(school_id: int, course_id: int):
    service: srv.SchoolService = digicubes.school
    token = digicubes.token
    form = CourseForm()

    # First get the course to be updated
    service.get_courses(token, proxy.SchoolProxy(id=school_id))

    # if method is post and all fields are valid,
    # create the new course.
    if form.validate_on_submit():

        course = proxy.CourseProxy()
        form.populate_obj(course)
        course.school_id = int(course.school_id)
        course.id = int(course_id)
        service.update_course(token, course)
        return redirect(url_for("admin.school", school_id=school_id))

    school_proxy: proxy.SchoolProxy = service.get(token, school_id)
    course: proxy.CourseProxy = service.get_course(token, course_id)
    action_url = url_for(
        "admin.update_school_course", school_id=school_proxy.id, course_id=course.id
    )
    form = CourseForm(obj=course)
    form.submit.label.text = "Update"
    return render_template(
        "admin/update_course.jinja",
        school=school_proxy,
        course=course,
        form=form,
        action=action_url,
    )


@admin_blueprint.route("/school/<int:school_id>/ccourse/", methods=("GET", "POST"))
@login_required
def create_school_course(school_id: int):
    """
        Create a new course for the school

        The method GET will render the creation form, while
        the method POST will validate the form and create the
        course, if possible.

        If any errors occure during the validation of the form,
        the form will be rerendered.
    """

    # Create the form instance
    form: CourseForm = CourseForm()

    # if method is post and all fields are valid,
    # create the new course.
    if form.validate_on_submit():

        new_course = proxy.CourseProxy(created_by_id=user.id)
        form.populate_obj(new_course)

        # Create the course.
        # TODO: Errors may occoure and have to be handled in a proper way.
        server.school.create_course(server.token, proxy.SchoolProxy(id=school_id), new_course)

        # After succesfully creating the course go back to
        # the administration page of the school.
        return redirect(url_for("admin.school", school_id=school_id))

    # Get the school proxy from the server and render out the form.
    token: str = server.token
    school_proxy: proxy.SchoolProxy = server.school.get(token, school_id)
    form.submit.label.text = "Create"
    action_url = url_for("admin.create_school_course", school_id=school_proxy.id)
    return render_template(
        "admin/create_course.jinja", school=school_proxy, form=form, action=action_url,
    )


@admin_blueprint.route("/course/<int:course_id>/cunit/", methods=("GET", "POST"))
@login_required
def create_course_unit(school_id: int):
    # TODO: Nothing implemented
    pass


@admin_blueprint.route("/rfc/", methods=("GET", "POST", "PUT"))
@login_required
def rfc():

    rfc_request = RfcRequest(request.headers.get("x-digicubes-rfcname", None), request.get_json())

    response = AdminRFC.call(rfc_request)
    return {"status": response.status, "text": response.text, "data": response.data}
