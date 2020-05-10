"""
Some forms to be used with the wtforms package.
"""
import logging

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, validators

from digicubes_flask.web import wtforms_widgets as w

logger = logging.getLogger(__name__)


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


class RegisterForm(FlaskForm):
    """
    The registration form
    """

    first_name = StringField("First Name", widget=w.materialize_input)
    last_name = StringField("Last Name", widget=w.materialize_input)
    email = StringField(
        "Email",
        widget=w.materialize_input,
        validators=[validators.Email(), validators.InputRequired()],
    )
    login = StringField(
        "Your Account Name", widget=w.materialize_input, validators=[validators.InputRequired()]
    )
    password = PasswordField(
        "Password", widget=w.materialize_input, validators=[validators.InputRequired()]
    )
    password2 = PasswordField(
        "Retype Password",
        widget=w.materialize_input,
        validators=[
            validators.InputRequired(),
            validators.EqualTo("password", message="Passwords are not identical."),
        ],
    )
    submit = SubmitField("Register", widget=w.materialize_submit)


class LoginForm(FlaskForm):
    """
    The login form.
    """

    login = StringField(
        "Login", widget=w.materialize_input, validators=[validators.InputRequired()]
    )
    password = PasswordField(
        "Password", widget=w.materialize_input, validators=[validators.InputRequired()]
    )
    submit = SubmitField("Login", widget=w.materialize_submit)
