"""
The Right Blueprint
"""
import logging
from flask import Blueprint, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    validators,
    TextAreaField,
)

from wtforms.validators import ValidationError

from digicubes_flask.client import proxy, service as srv, RightService
from digicubes_flask import (
    login_required,
    current_user,
    digicubes,
    CurrentUser,
)

import digicubes_flask.exceptions as ex
from digicubes_flask.web.account_manager import DigicubesAccountManager

import digicubes_flask.web.wtforms_widgets as w

blueprint = Blueprint("right", __name__, url_prefix="/right")

logger = logging.getLogger(__name__)

server: DigicubesAccountManager = digicubes
user: CurrentUser = current_user

# =========================================================================
# THE FORMS
# =========================================================================


class RightForm(FlaskForm):
    """
    Create or update right form
    """

    name = StringField(
        "Name",
        widget=w.materialize_input,
        validators=[validators.InputRequired("A name is required.")],
    )
    submit = SubmitField("Ok", widget=w.materialize_submit)


# =========================================================================
# THE ROUTES
# =========================================================================


def right_service() -> RightService:
    return digicubes.right


@blueprint.route("/all/")
@login_required
def all():
    """
    Display all rights
    """

    return render_template("right/rights.jinja", rights=right_service().all(digicubes.token))
