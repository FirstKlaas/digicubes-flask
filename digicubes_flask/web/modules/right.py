"""
The Right Blueprint
"""
import logging

from flask import Blueprint, render_template, request
from flask_wtf import FlaskForm
from werkzeug.datastructures import Accept
from wtforms import StringField, SubmitField, validators

import digicubes_flask.web.wtforms_widgets as w
from digicubes_flask import (CurrentUser, current_user, digicubes,
                             login_required)
from digicubes_flask.client import RightService
from digicubes_flask.client.model import RightModel
from digicubes_flask.web.account_manager import DigicubesAccountManager

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
    right_list = right_service().all(digicubes.token)

    best = Accept(request.accept_mimetypes).best_match(
        ["application/json", "text/html"], "text/html"
    )
    if best == "text/html":
        return render_template("right/rights.jinja", rights=right_list)

    return RightModel.list_model(right_list).json()
