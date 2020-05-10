"""
Some forms to be used with the wtforms package.
"""
import logging
from datetime import date

from flask_wtf import FlaskForm
from wtforms import (
    Field,
    PasswordField,
    StringField,
    SubmitField,
    validators,
    TextAreaField,
    HiddenField,
    BooleanField,
    DateField,
)

from wtforms.validators import ValidationError

from digicubes_common import exceptions as ex
from digicubes_client.client import proxy

import digicubes_flask.web.wtforms_widgets as w
from digicubes_flask import digicubes

logger = logging.getLogger(__name__)

__ALL__ = [
    "UserForm",
    "SchoolForm",
    "CourseForm",
    "CourseForm",
]


class SetPasswordForm(FlaskForm):
    """
    Form to set a new password.
    """

    password = PasswordField(
        "New Password",
        widget=w.materialize_password,
        validators=[
            validators.InputRequired(),
            validators.EqualTo("confirm", message="Passwords must match"),
        ],
    )
    confirm = PasswordField("Retype Password", widget=w.materialize_password)
    submit = SubmitField("Update", widget=w.materialize_submit)


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
        "The Account Name",
        widget=w.materialize_input,
        validators=[
            validators.InputRequired(),
            validators.Length(max=20, message="Max size exceeded"),
        ],
    )

    password = PasswordField("Password", widget=w.materialize_password)
    is_active = BooleanField("Active", widget=w.materialize_checkbox)
    is_verified = BooleanField("Verified", widget=w.materialize_checkbox)

    submit = SubmitField("Update", widget=w.materialize_submit)


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
            user_proxy: proxy.UserProxy = digicubes.user.get_by_login(digicubes.token, field.data)
            if self.user_id is not None and self.user_id == user_proxy.id:
                return

            raise ValidationError("User already exists. Try a different login.")
        except ex.DoesNotExist:
            pass


class SchoolNameAvailable:
    """
    Field validator to check, if the name (field.data) is available,
    and the school may be created or updated.

    If a school_id is provided, checks, if the school with the name
    is the the same school. Aka, the name hasn't changed. This might
    be the case, when updating a school.
    """

    def __init__(self, school_id: int = None):
        self.school_id = school_id

    def __call__(self, form: FlaskForm, field):
        """
        Checks, if the school already exists, as the name has to be unique
        """
        try:
            if not field.data:
                raise ValidationError("Name may not be empty")

            school: proxy.SchoolProxy = digicubes.school.get_by_name(digicubes.token, field.data)

            if self.school_id is not None and school.id == self.school_id:
                # Of course the school may keep its name
                return

            # Now we know that there is another school with the same
            # name
            raise ValidationError("School already exists")
        except ex.DoesNotExist:
            pass  # If we can not find the account, that's perfect.


class SchoolForm(FlaskForm):
    """
    Create or update school form
    """

    name = StringField(
        "Name",
        widget=w.materialize_input,
        validators=[validators.InputRequired("A name is required.")],
    )
    description = TextAreaField(
        "Description",
        widget=w.materialize_textarea,
        validators=[validators.InputRequired("A description is required.")],
    )
    submit = SubmitField("Ok", widget=w.materialize_submit)


class CourseForm(FlaskForm):
    """
    Create new Course Form
    """

    school_id = HiddenField()
    name = StringField(
        "Name",
        widget=w.materialize_input,
        validators=[validators.InputRequired("A name is required")],
    )

    description = TextAreaField(
        "Description",
        widget=w.materialize_textarea,
        validators=[validators.InputRequired("A desciption is required")],
    )

    from_date = DateField(
        "Starting from",
        default=date.today(),
        format="%d.%m.%Y",
        widget=w.materialize_picker,
        validators=[validators.InputRequired("The course needs a starting date.")],
    )

    until_date = DateField(
        "Ending at",
        default=date.today(),
        format="%d.%m.%Y",
        widget=w.materialize_picker,
        validators=[validators.InputRequired("A course needs a ending date.")],
    )

    is_private = BooleanField("Private", widget=w.materialize_switch)

    submit = SubmitField("Ok", widget=w.materialize_submit)
