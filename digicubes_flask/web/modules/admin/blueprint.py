"""
The Admin Blueprint

All routes should be only accessible by users, who have the
role 'admin'
"""
import logging

from flask import Blueprint, render_template, abort, request, url_for, redirect, flash

from digicubes_flask.client import proxy, service as srv

from digicubes_flask import login_required, digicubes
from digicubes_flask.web.account_manager import DigicubesAccountManager
from digicubes_flask.email import mail_cube
from digicubes_flask import exceptions as ex

from .forms import (
    UserForm,
    UserLoginAvailable,
    create_userform_with_roles,
)

from .rfc import AdminRFC, RfcRequest

admin_blueprint = Blueprint("admin", __name__, template_folder="templates")

logger = logging.getLogger(__name__)

server: DigicubesAccountManager = digicubes


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
    db_roles = server.role.all(digicubes.token)
    form = create_userform_with_roles(roles)

    # Setting the active state true as the default
    form.user.is_active.data = True

    # TODO We have to tabe better care of the verified flag.
    # If auto_verify is true, then there is no chance of setting
    # the password. So in this case we need a way to set the initial
    # password. Maybe as a field of this form.

    if form.is_submitted():
        if form.user.validate({"login": [UserLoginAvailable()]}):
            new_user = proxy.UserProxy()
            form.user.form.populate_obj(new_user)

            # When users are created by an admin,
            # he decides, whether the user is verified or not.
            # if current_app.config.get("auto_verify", False):
            #    new_user.is_verified = True
            new_user = digicubes.user.create(digicubes.token, new_user)

            # TODO: Te newly created user should have at least one role
            # Most probably the student role. Alternatively we could
            # improve the form by adding checkboxes for every role.

            flash(f"User {new_user.login} successfully created")

            # Now set the user roles.
            for db_role in db_roles:
                if form.role[db_role.name].data:
                    server.user.add_role(digicubes.token, new_user, db_role)

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
    form.user.submit.label.text = "Create"
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


@admin_blueprint.route("/school/<int:school_id>/headmaster/", methods=("GET", "POST"))
@login_required
def add_school_headmaster():
    """
    Get or add an headmaster to the school with the id `school_id`. If no such school
    exists, an 404 status code is send back.

    :Methods:

        - **GET:** Returns all headmasters, associated with this school ordered in
          lexical ascending order by their last name, followed by the first name.
          There is no pagination support. The endpoint displays always all
          headmaster.
    """
    #user: CurrentUser = current_user

    #form = EmailForm()

    #if form.is_submitted():
    #    if form.validate():
    #        email = form.email.data
    #        # Now check, if a user with this
    #        # Emailadress already is registered


@admin_blueprint.route("/rfc/", methods=("GET", "POST", "PUT"))
@login_required
def rfc():

    rfc_request = RfcRequest(request.headers.get("x-digicubes-rfcname", None), request.get_json())

    response = AdminRFC.call(rfc_request)
    return {"status": response.status, "text": response.text, "data": response.data}
