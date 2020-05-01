"""
Some forms to be used with the wtforms package.
"""
import logging
from datetime import date

from flask_wtf import FlaskForm
from wtforms import (
    PasswordField,
    StringField,
    SubmitField,
    validators,
    TextAreaField,
    HiddenField,
    BooleanField,
    DateField,
)

import digicubes_flask.web.wtforms_widgets as w
from digicubes_flask import digicubes

logger = logging.getLogger(__name__)

__ALL__ = [
    "UserForm",
    "SchoolForm",
    "CourseForm",
    "CourseForm",
]


class UserForm(FlaskForm):
    """
    The user form that is used by the admin to create or update
    users.
    """

    first_name = StringField("First Name", widget=w.materialize_input)
    last_name = StringField("Last Name", widget=w.materialize_input)
    email = StringField(
        "Email",
        widget=w.materialize_input,
        validators=[validators.Email(), validators.InputRequired()],
    )
    login = StringField(
        "The Account Name", widget=w.materialize_input, validators=[validators.InputRequired()]
    )
    password = PasswordField("Password", widget=w.materialize_password)
    is_active = BooleanField("Active", widget=w.materialize_checkbox)
    is_verified = BooleanField("Verified", widget=w.materialize_checkbox)

    submit = SubmitField("Update", widget=w.materialize_submit)

    def validate_login(self, field):
        """
        Checks, if the login already exists, as is has to be unique
        """
        digicubes.user.get_by_login(digicubes.token, field.data)
        # raise ValueError("Login already exists.")


class SchoolForm(FlaskForm):
    """
    Create school form
    """

    name = StringField("Name", widget=w.materialize_input)
    description = TextAreaField("Description", widget=w.materialize_textarea)
    submit = SubmitField("Ok", widget=w.materialize_submit)


class CourseForm(FlaskForm):
    """
    Create new Course Form
    """

    school_id = HiddenField()
    name = StringField("Name", widget=w.materialize_input, validators=[validators.InputRequired()])

    description = TextAreaField("Description", widget=w.materialize_textarea)
    from_date = DateField(
        "Starting from", default=date.today(), format="%d.%m.%Y", widget=w.materialize_picker
    )
    until_date = DateField(
        "Ending at", default=date.today(), format="%d.%m.%Y", widget=w.materialize_picker
    )
    is_private = BooleanField("Private", widget=w.materialize_switch)
    submit = SubmitField("Ok", widget=w.materialize_submit)
