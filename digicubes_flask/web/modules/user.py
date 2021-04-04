"""
The User Blueprint
"""
import logging
from typing import List

from flask import (Blueprint, abort, flash, redirect, render_template, request,
                   url_for)
from flask_wtf import FlaskForm
from wtforms import (BooleanField, Field, FormField, StringField, SubmitField,
                     ValidationError, validators)

import digicubes_flask.web.wtforms_widgets as w
from digicubes_flask import CurrentUser, current_user, digicubes
from digicubes_flask import exceptions as ex
from digicubes_flask import login_required
from digicubes_flask.client import service as srv
from digicubes_flask.client.model import RoleModel, UserModel, UserModelUpsert
from digicubes_flask.email import mail_cube
from digicubes_flask.web.account_manager import DigicubesAccountManager

blueprint = Blueprint("user", __name__, url_prefix="/user")

logger = logging.getLogger(__name__)

server: DigicubesAccountManager = digicubes
user: CurrentUser = current_user

# =========================================================================
# THE FORMS
# =========================================================================


class UserForm(FlaskForm):
    """
    The user form that is used by the admin to create or update
    users.
    """

    first_name = StringField(
        "First Name",
        widget=w.materialize_input,
        validators=[
            validators.InputRequired(),
            validators.Length(max=20, message="Max size exceeded"),
        ],
    )

    last_name = StringField(
        "Last Name",
        widget=w.materialize_input,
        validators=[
            validators.InputRequired(),
            validators.Length(max=20, message="Max size exceeded"),
        ],
    )

    email = StringField(
        "Email",
        widget=w.materialize_input,
        validators=[
            validators.Email(),
            validators.InputRequired(),
            validators.Length(max=60, message="Max size exceeded"),
        ],
    )

    login = StringField(
        "Login",
        widget=w.materialize_input,
        validators=[
            validators.InputRequired(),
            validators.Length(max=20, message="Max size exceeded"),
        ],
    )

    is_active = BooleanField("Active", widget=w.materialize_checkbox)
    is_verified = BooleanField("Verified", widget=w.materialize_checkbox)

    submit = SubmitField("Update", widget=w.materialize_submit)


def create_userform_with_roles(roles: List[RoleModel]) -> UserForm:
    """
    Function to create a user form, that boolean fields for all defined
    roles.
    """

    class UserFormWithRoles(FlaskForm):
        """
        Aggregated Form that holds the UserForm as well as a dynamically
        generated RoleSelectionForm.
        """

    class RoleSelectionForm(FlaskForm):
        """
        Form for the User Roles. Entries for the roles are added
        dynamically.
        """

    for role in roles:
        setattr(
            RoleSelectionForm,
            f"{role.name}",
            BooleanField(role.name, widget=w.materialize_checkbox),
        )

    setattr(UserFormWithRoles, "user", FormField(UserForm, label="User"))
    setattr(UserFormWithRoles, "role", FormField(RoleSelectionForm, label="Roles"))
    return UserFormWithRoles()


class UserLoginAvailable:
    """
    Custom validator to check, if a user with the login name
    from the field already exists and therefor cannot be used.
    """

    def __init__(self, user_id: int = None):
        self.user_id = user_id

    def __call__(self, form: UserForm, field: Field):
        if not field.data:
            raise ValidationError("Login may not be empty.")

        try:
            user_model = digicubes.user.get_by_login(digicubes.token, field.data)
            if self.user_id is not None and self.user_id == user_model.id:
                return

            raise ValidationError("User already exists. Try a different login.")
        except ex.DoesNotExist:
            pass


# =========================================================================
# THE ROUTES
# =========================================================================


@blueprint.route("/all/")
@login_required
def get_all():
    """The user list route."""
    user_list = digicubes.user.all(digicubes.token)
    return render_template("admin/users.jinja", users=user_list)


@blueprint.route("/create/", methods=("GET", "POST"))
@login_required
def create():
    """Create a new user"""
    db_roles = server.role.all(digicubes.token)
    form = create_userform_with_roles(db_roles)

    # Setting the active state true as the default
    form.user.is_active.data = True

    # TODO We have to tabe better care of the verified flag.
    # If auto_verify is true, then there is no chance of setting
    # the password. So in this case we need a way to set the initial
    # password. Maybe as a field of this form.

    if form.is_submitted():
        if form.user.validate({"login": [UserLoginAvailable()]}):
            new_user = UserModelUpsert.parse_obj(form.user.form.data)

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

            return redirect(url_for("user.update", user_id=new_user.id))

    # Form not submitted or validation failed.
    form.user.submit.label.text = "Create"
    action = url_for("user.create")
    return render_template("admin/create_user.jinja", form=form, action=action)


@blueprint.route("/verify/renew/<int:user_id>/")
def verify_renew(user_id: int):
    service: srv.UserService = digicubes.user
    token = digicubes.token
    user: UserModel = service.get(token, user_id)
    link = mail_cube.create_verification_link(user)
    return render_template("admin/send_verification_link.jinja", user=user, link=link)


@blueprint.route("/update/<int:user_id>/", methods=("GET", "POST"))
@login_required
def update(user_id: int):
    """
    Route to update an existing user.
    """
    service: srv.UserService = digicubes.user
    token = digicubes.token
    form = UserForm()
    user_model: UserModel = None

    if form.is_submitted():
        if form.validate({"login": [UserLoginAvailable(user_id=user_id)]}):
            user_model = UserModel.parse_obj(form.data)
            user_model.id = user_id
            digicubes.user.update(token, user_model)
            return redirect(url_for("user.get", user_id=user_id))
        else:
            user_model: UserModel = service.get(token, user_id)
    else:
        user_model: UserModel = service.get(token, user_id)
        form.process(obj=user_model)

    return render_template(
        "admin/update_user.jinja",
        form=form,
        user=user_model,
        action=url_for("user.update", user_id=user_id),
    )


@blueprint.route("/delete/<int:user_id>/")
@login_required
def delete(user_id: int):
    """Delete an existing user"""
    token = digicubes.token
    # Gettting the school details from the server
    # TODO: Was, wenn das Objekt nicht existiert?
    digicubes.user.delete(token, user_id)
    return redirect(url_for("user.get_all"))


@blueprint.route("/get/<int:user_id>/")
@login_required
def get(user_id: int):
    """Display detaild information for an existing user"""
    token = server.token
    # Getting the user details from the server
    user: UserModel = server.user.get(token, user_id)

    # Getting the user roles from the server
    user_roles_names = [role.name for role in server.user.get_roles(token, user)]
    all_roles = server.role.all(token)

    role_list = [(role, role.name in user_roles_names) for role in all_roles]

    return render_template(
        "user/user.jinja",
        user=user,
        roles=role_list,
        headmaster_schools=server.school.get_headmaster_schools(token, user),
        teacher_schools=server.school.get_teacher_schools(token, user),
        student_schools=server.school.get_student_schools(token, user),
    )


@blueprint.route("/panel/all/")
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
