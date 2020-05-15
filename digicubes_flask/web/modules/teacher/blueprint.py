"""
The Admin Blueprint
"""
import logging
from flask import Blueprint, render_template, redirect, url_for

from digicubes_flask import login_required

teacher_service = Blueprint("teacher", __name__)

logger = logging.getLogger(__name__)


@teacher_service.route("/")
@login_required
def index():
    """The home route"""
    return render_template("teacher/index.jinja")


@teacher_service.route("/home")
@login_required
def home():
    return redirect(url_for("account.home"))
