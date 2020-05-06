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

from wtforms.validators import ValidationError

from digicubes_common import exceptions as ex

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

    first_name = StringField(
        "First Name", widget=w.materialize_input, validators=[validators.InputRequired()]
    )

    last_name = StringField(
        "Last Name", widget=w.materialize_input, validators=[validators.InputRequired()]
    )

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
        try:
            digicubes.user.get_by_login(digicubes.token, field.data)
            # If we can find an account, we raise the ValidatioNerror to
            # signal, that this account is not available
            raise ValidationError("Account already exists")
        except ex.DoesNotExist:
            pass  # If we can not find the account, that's perfect.


class SchoolForm(FlaskForm):
    """
    Create school form
    """

    name = StringField("Name", widget=w.materialize_input, validators=[validators.InputRequired()])
    description = TextAreaField(
        "Description", widget=w.materialize_textarea, validators=[validators.InputRequired()]
    )
    submit = SubmitField("Ok", widget=w.materialize_submit)

    def validate_name(self, field):
        """
        Checks, if the school already exists, as the name has to be unique
        """
        try:
            digicubes.school.get_by_name(digicubes.token, field.data)
            # If we can find an account, we raise the ValidatioNerror to
            # signal, that this account is not available
            raise ValidationError("School already exists")
        except ex.DoesNotExist:
            pass  # If we can not find the account, that's perfect.


class CourseForm(FlaskForm):
    """
    Create new Course Form
    """

    school_id = HiddenField()
    name = StringField("Name", widget=w.materialize_input, validators=[validators.InputRequired()])

    description = TextAreaField(
        "Description", widget=w.materialize_textarea, validators=[validators.InputRequired()]
    )

    from_date = DateField(
        "Starting from", default=date.today(), format="%d.%m.%Y", widget=w.materialize_picker
    )

    until_date = DateField(
        "Ending at", default=date.today(), format="%d.%m.%Y", widget=w.materialize_picker
    )

    is_private = BooleanField("Private", widget=w.materialize_switch)

    submit = SubmitField("Ok", widget=w.materialize_submit)
