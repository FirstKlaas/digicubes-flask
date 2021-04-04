"""
The Admin Blueprint
"""
import logging

from flask import Blueprint, redirect, render_template, url_for

from digicubes_flask import login_required

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
