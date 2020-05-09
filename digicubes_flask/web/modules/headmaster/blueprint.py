"""
The Admin Blueprint
"""
import logging
from flask import Blueprint, render_template, abort, current_app as app, redirect, url_for

from digicubes_client.client import UserProxy
from digicubes_common.exceptions import DigiCubeError
from digicubes_common.structures import BearerTokenData
from digicubes_flask import login_required, account_manager

headmaster_service = Blueprint("headmaster", __name__)

logger = logging.getLogger(__name__)


@headmaster_service.route("/")
@login_required
def index():
    """Homepage of the Headmaster space"""
    return render_template("headmaster/index.jinja")


@headmaster_service.route("/home")
@login_required
def home():
    return redirect(url_for("account.home"))
