"""
The Admin Blueprint
"""
import logging
from flask import Blueprint, render_template, redirect, url_for

from digicubes_flask import login_required, digicubes
from digicubes_flask.client.service import UserService

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

@headmaster_service.route("/myschools")
@login_required
def get_my_schools():
    """
    Gets alls schools related to this user. The user must be
    a headmaster. If no schools are associated with this user,
    a info message will be displayed.
    """
    #schools = digicubes.school.get_headmaster_schools()
    return redirect(url_for("account.home"))
