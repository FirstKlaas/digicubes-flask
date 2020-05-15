"""
The Admin Blueprint
"""
import logging
from flask import Blueprint, render_template, redirect, url_for

from digicubes_flask import login_required

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
