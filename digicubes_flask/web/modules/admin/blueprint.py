"""
The Admin Blueprint

All routes should be only accessible by users, who have the
role 'admin'
"""
import logging

from flask import Blueprint, render_template, request, url_for, redirect

from digicubes_flask.client import proxy
from digicubes_flask import login_required, digicubes
from digicubes_flask.web.account_manager import DigicubesAccountManager

from .rfc import AdminRFC, RfcRequest

admin_blueprint = Blueprint("admin", __name__, template_folder="templates")

logger = logging.getLogger(__name__)

server: DigicubesAccountManager = digicubes


@admin_blueprint.route("/")
@login_required
def index():
    """The home/index route"""
    return render_template("admin/index.jinja")


@admin_blueprint.route("/roles/")
def roles():
    """
    Display all roles
    """
    role_list = digicubes.role.all(digicubes.token)
    return render_template("role/roles.jinja", roles=role_list)


@admin_blueprint.route("/user/<int:user_id>/addrole/<int:role_id>")
def add_user_role(user_id: int, role_id: int):
    server.user.add_role(
        server.token, proxy.UserProxy(id=user_id), proxy.RoleProxy(id=role_id, name="")
    )
    return redirect(url_for("user.update", user_id=user_id))


@admin_blueprint.route("/user/<int:user_id>/removerole/<int:role_id>")
def remove_user_role(user_id: int, role_id: int):
    server.user.remove_role(
        server.token, proxy.UserProxy(id=user_id), proxy.RoleProxy(id=role_id, name="")
    )
    return redirect(url_for("user.update", user_id=user_id))


@admin_blueprint.route("/rfc/", methods=("GET", "POST", "PUT"))
@login_required
def rfc():

    rfc_request = RfcRequest(request.headers.get("x-digicubes-rfcname", None), request.get_json())

    response = AdminRFC.call(rfc_request)
    return {"status": response.status, "text": response.text, "data": response.data}
