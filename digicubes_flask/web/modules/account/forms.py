"""
Some forms to be used with the wtforms package.
"""
import logging

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, validators

from digicubes_flask.web.wtforms_widgets import materialize_input, materialize_submit

logger = logging.getLogger(__name__)


class RegisterForm(FlaskForm):
    """
    The registration form
    """

    first_name = StringField("First Name", widget=materialize_input)
    last_name = StringField("Last Name", widget=materialize_input)
    email = StringField(
        "Email",
        widget=materialize_input,
        validators=[validators.Email(), validators.InputRequired()],
    )
    login = StringField(
        "Your Account Name", widget=materialize_input, validators=[validators.InputRequired()]
    )
    password = PasswordField(
        "Password", widget=materialize_input, validators=[validators.InputRequired()]
    )
    password2 = PasswordField(
        "Retype Password",
        widget=materialize_input,
        validators=[
            validators.InputRequired(),
            validators.EqualTo("password", message="Passwords are not identical."),
        ],
    )
    submit = SubmitField("Register", widget=materialize_submit)


class LoginForm(FlaskForm):
    """
    The login form.
    """

    login = StringField("Login", widget=materialize_input, validators=[validators.InputRequired()])
    password = PasswordField(
        "Password", widget=materialize_input, validators=[validators.InputRequired()]
    )
    submit = SubmitField("Login", widget=materialize_submit)
