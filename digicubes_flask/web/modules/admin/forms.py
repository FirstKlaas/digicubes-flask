"""
Some forms to be used with the wtforms package.
"""
import logging

from flask_wtf import FlaskForm
from wtforms import (
    PasswordField,
    StringField,
    SubmitField,
    validators,
    TextAreaField,
)

from wtforms.validators import ValidationError

from digicubes_flask.client import proxy

from digicubes_flask import exceptions as ex
import digicubes_flask.web.wtforms_widgets as w
from digicubes_flask import digicubes

logger = logging.getLogger(__name__)

__ALL__ = [
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


class EmailForm(FlaskForm):
    """
    Simple Emailform, to update a users email address
    """

    email = StringField(
        "Email",
        widget=w.materialize_input,
        validators=[
            validators.Email(),
            validators.InputRequired(),
            validators.Length(max=60, message="Max size exceeded"),
        ],
    )

    submit = SubmitField("Update", widget=w.materialize_submit)


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

class SimpleTextForm(FlaskForm):
    login = StringField(
        "Login",
        widget=w.materialize_input,
        validators=[validators.InputRequired("A login is required.")],
    )
    submit = SubmitField("Ok", widget=w.materialize_submit)
