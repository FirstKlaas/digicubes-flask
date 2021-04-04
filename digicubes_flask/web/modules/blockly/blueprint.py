import logging

from flask import Blueprint, render_template

__ALL__ = ["blueprint"]

blueprint = Blueprint("blockly", __name__, template_folder="templates")

logger = logging.getLogger(__name__)


@blueprint.route("/")
def index():
    """The home/index route"""
    return render_template("blockly/playground.jinja")
