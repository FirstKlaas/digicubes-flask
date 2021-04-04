import logging

from flask import (Blueprint, abort, current_app, redirect, render_template,
                   request, url_for)

__ALL__ = ["blueprint"]

blueprint = Blueprint("blockly", __name__, template_folder="templates")

logger = logging.getLogger(__name__)


@blueprint.route("/")
def index():
    """The home/index route"""
    return render_template("blockly/playground.jinja")
