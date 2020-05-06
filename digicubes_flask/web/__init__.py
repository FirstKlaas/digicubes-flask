"""
A minimal startscript for the server. This can be used
as a quickstart module.
"""
import datetime
import logging
import os
import re
from logging.config import dictConfig  # pylint: disable=import-outside-toplevel

from importlib.resources import open_text
from typing import Optional
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, redirect, url_for, Response, request, Request, g

import yaml
from libgravatar import Gravatar
from markdown import markdown

from digicubes_common.exceptions import DigiCubeError, TokenExpired
from digicubes_client.client.proxy import RightProxy, RoleProxy
from digicubes_flask import account_manager as accm, current_user
from digicubes_flask.email import MailCube
from digicubes_flask.web.modules import (
    account_blueprint,
    admin_blueprint,
    headmaster_blueprint,
    teacher_blueprint,
    student_blueprint,
    blockly_blueprint,
)

from .account_manager import DigicubesAccountManager


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

digicubes: DigicubesAccountManager = accm

mail_cube = MailCube()
the_account_manager = DigicubesAccountManager()


def create_app():
    """
    Factory function to create the flask server.
    Flask will automatically detect the method
    on `flask run`.
    """

    app = Flask(__name__)
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # TODO: Set via configuration
    app.config["DC_COOKIE_NAME"] = "digitoken"

    @app.errorhandler(DigiCubeError)
    def handle_digicube_error(error):  # pylint: disable=unused-variable
        logger.exception("Error occurred. Going back to login page.")
        digicubes.logout()
        return redirect(url_for("account.login"))

    @app.errorhandler(404)
    def page_not_found(error):
        return redirect(url_for("account.login"))

    @app.template_filter()
    def gravatar(email: str) -> str:

        default = url_for("static", filename="image/digibot_profile_40.png", _external=True)
        if not email:
            return default

        gravatar: Gravatar = Gravatar(email)
        return gravatar.get_image(size=40, default="retro")

    @app.template_filter()
    def digidate(dtstr):  # pylint: disable=unused-variable
        if dtstr is None:
            return ""

        if isinstance(dtstr, (datetime.date, datetime.datetime)):
            date = datetime.datetime.fromisoformat(str(dtstr))
            return date.strftime("%d.%m.%Y")

        if isinstance(dtstr, str):
            date = datetime.datetime.fromisoformat(str(dtstr))
            return date.strftime("%d.%m.%Y")

        raise ValueError(f"Cannot convert given value. Unsupported type {type(dtstr)}")

    @app.template_filter()
    def md(txt: str) -> str:  # pylint: disable=unused-variable
        return markdown(txt)

    @app.template_filter()
    def digitime(dtstr):  # pylint: disable=unused-variable
        if dtstr is None:
            return ""

        if isinstance(dtstr, str):
            date = datetime.datetime.fromisoformat(str(dtstr))
            return date.strftime("%H:%M")

        if isinstance(dtstr, (datetime.date, datetime.datetime)):
            return date.strftime("%H:%M")

        raise ValueError(f"Cannot convert given value. Unsupported type {type(dtstr)}")

    @app.template_filter()
    def nonefilter(value):  # pylint: disable=unused-variable
        return value if value is not None else "-"

    @app.after_request
    def after_request_func(response):  # pylint: disable=unused-variable

        if not g.digitoken_received:
            # No token in request found
            if current_user.token is not None:
                # We have a token, so a user must have logged in successfully
                # We write the token to the response
                response.set_cookie(
                    "digicubes", current_user.token, samesite="Lax", expires=current_user.expires_at
                )
            else:
                # No token received and non created. So do nothing
                logger.debug("Not sending a token. (No Token)")
        else:
            if current_user.token is not None:
                # We reveived a token and it still exists.
                # So we just send it
                # We do this because a new token is created at the
                # beginnig of the request
                response.set_cookie(
                    "digicubes", current_user.token, samesite="Lax", expires=current_user.expires_at
                )
                logger.debug("Updating digicubes cookie")
            else:
                # We received a cookie, but user has been logged out.
                # (Or the token has expired)
                # So we send an cookie which immediately exires. The browser
                # deletes the cookie.
                response.set_cookie("digicubes", "", samesite="Lax", expires=0)
                logger.debug("Deleting digicubes cookie")

        return response

    @app.before_request
    def check_digitoken():  # pylint: disable=unused-variable
        token = request.cookies.get("digicubes", None)
        g.digitoken_received = False

        if token is not None:
            # So we have a token. Not lets refresh it
            try:
                data = accm.refresh_token(token)
                # current_user.token = token
                current_user.set_data(data)
                g.digitoken_received = True
            except TokenExpired:
                current_user.reset()
                logger.warning("Token was send by the client, but it is expired on the server.")

    def parse_config(data=None, tag="!ENV"):
        """
        Add a new token to the yaml parser. If we have an !ENV ${xyz} string in the yaml file,
        xyz will be replaced by the corresonding environment variable if availabe or by the string
        xyz else.
        """
        pattern = re.compile(".*?\${(\w+)}.*?")  # pylint: disable=anomalous-backslash-in-string
        loader = yaml.SafeLoader
        loader.add_implicit_resolver(tag, pattern, None)

        def constructor_env_variables(loader, node):
            """
            Extracts the environment variable from the node's value
            :param yaml.Loader loader: the yaml loader
            :param node: the current node in the yaml
            :return: the parsed string that contains the value of the environment
            variable
            """
            value = loader.construct_scalar(node)
            match = pattern.findall(value)  # to find all env variables in line
            if match:
                full_value = value
                for g in match:
                    full_value = full_value.replace(f"${{{g}}}", os.environ.get(g, g))
                return full_value
            return value

        loader.add_constructor(tag, constructor_env_variables)
        return yaml.load(data, Loader=loader)

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # C O N F I G U R A T I O N
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    # First, load the .env file, wich adds environment variables to the
    # the program. Together with the pyaml parser extension these variables
    # can be used in the yaml configuration
    load_dotenv(verbose=False)

    # Load the default settings and then load the custom settings
    # The default settings are stored in this package and have to be loaded
    # as a ressource.
    with open_text("digicubes_flask.cfg", "default_configuration.yaml") as f:
        settings = parse_config(f)
        app.config.update(settings)

    # Loading the logging configuration. If no logging configuration
    # is found, it will fall back to logging.basicConfiguration
    logging.basicConfig(level=logging.DEBUG)
    """
    try:
        with open_text("digicubes_flask.cfg", "logging.yaml") as f:
            settings = yaml.safe_load(f)
            try:
                dictConfig(settings)
                logger.info("Configured logging")
            except ValueError:
                logging.basicConfig(level=logging.DEBUG)
                logger.fatal("Could not configure logging.", exc_info=True)
    except:
    """

    # Initalizes the account manager extension, wich is responsible for the the
    # login and logout procedure.
    the_account_manager.init_app(app)

    mail_cube.init_app(app)

    # ---------------------------
    # Now register the blueprints
    # ---------------------------

    # Account blueprint
    url_prefix = "/account"
    logger.debug("Register account blueprint at %s", url_prefix)
    app.register_blueprint(account_blueprint, url_prefix=url_prefix)

    @app.route("/")
    def home():
        # pylint: disable=unused-variable
        return redirect(url_for("account.login"))

    # Blockly Blueprint
    app.register_blueprint(blockly_blueprint, url_prefix="/blockly")

    # Admin blueprint
    url_prefix = "/dcad"
    logger.debug("Register admin blueprint at %s", url_prefix)
    app.register_blueprint(admin_blueprint, url_prefix=url_prefix)

    # Headmaster blueprint
    url_prefix = "/dchm"
    logger.debug("Register headmaster blueprint at %s", url_prefix)
    app.register_blueprint(headmaster_blueprint, url_prefix=url_prefix)

    # Teacher blueprint
    url_prefix = "/dcte"
    logger.debug("Register teacher blueprint at %s", url_prefix)
    app.register_blueprint(teacher_blueprint, url_prefix=url_prefix)

    url_prefix = "/dcst"
    logger.debug("Register student blueprint at %s", url_prefix)
    app.register_blueprint(student_blueprint, url_prefix=url_prefix)

    logger.info("Static folder is %s", app.static_folder)
    return app
