"""
The Admin Blueprint
"""
import logging

from flask import Blueprint, abort
from flask import current_app as app
from flask import redirect, render_template, url_for

from digicubes_flask import account_manager, login_required
from digicubes_flask.exceptions import DigiCubeError
from digicubes_flask.structures import BearerTokenData

student_service = Blueprint("student", __name__)

logger = logging.getLogger(__name__)


@student_service.route("/")
@login_required
def index():
    """The home route"""
    return render_template("student/index.jinja")


@student_service.route("/home")
@login_required
def home():
    return redirect(url_for("account.home"))
