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
    HiddenField,
    DateField,
    BooleanField,
)

from digicubes_client.client.proxy import CourseProxy

import digicubes_flask.web.wtforms_widgets as w

logger = logging.getLogger(__name__)


class CreateUserForm(FlaskForm):
    """
    The create user form
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
    password = PasswordField(
        "Password", widget=w.materialize_password, validators=[validators.InputRequired()]
    )
    password2 = PasswordField(
        "Retype Password",
        widget=w.materialize_password,
        validators=[
            validators.InputRequired(),
            validators.EqualTo("password", message="Passwords are not identical."),
        ],
    )
    submit = SubmitField("Register", widget=w.materialize_submit)


class UpdateUserForm(FlaskForm):
    """
    The update user form
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
    is_active = BooleanField("Active", widget=w.materialize_checkbox)
    is_verified = BooleanField("Verified", widget=w.materialize_checkbox)

    submit = SubmitField("Update", widget=w.materialize_submit)


class CreateSchoolForm(FlaskForm):
    """
    Create school form
    """

    name = StringField("Name", widget=w.materialize_input)
    description = TextAreaField("Description", widget=w.materialize_textarea)
    submit = SubmitField("Create", widget=w.materialize_submit)


class CreateCourseForm(FlaskForm):
    """
    Create new Course Form
    """

    school_id = HiddenField()
    name = StringField("Name", widget=w.materialize_input, validators=[validators.InputRequired()])

    description = TextAreaField("Description", widget=w.materialize_textarea)
    from_date = StringField("Starting from", widget=w.materialize_picker)
    until_date = StringField("Ending at", widget=w.materialize_picker)
    is_private = BooleanField("Private", widget=w.materialize_switch)
    submit = SubmitField("Create", widget=w.materialize_submit)
