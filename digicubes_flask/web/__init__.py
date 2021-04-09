"""
A minimal startscript for the server. This can be used
as a quickstart module.
"""
import datetime
import logging
import os

from dotenv import load_dotenv
from flask import Flask, g, redirect, request, url_for
from flask_babel import Babel
from libgravatar import Gravatar
from markdown import markdown

from digicubes_flask import account_manager as accm
from digicubes_flask import current_user
from digicubes_flask.email import MailCube
from digicubes_flask.exceptions import DigiCubeError, TokenExpired
from digicubes_flask.web.modules import (account_blueprint, admin_blueprint,
                                         blockly_blueprint,
                                         headmaster_blueprint,
                                         register_blueprints,
                                         student_blueprint, teacher_blueprint)

from .account_manager import DigicubesAccountManager

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

digicubes: DigicubesAccountManager = accm

mail_cube = MailCube()
the_account_manager = DigicubesAccountManager()
babel = Babel()


def create_app(cfg_file_name=None):
    """
    Factory function to create the flask server.
    Flask will automatically detect the method
    on `flask run`.
    """

    # First, load the .env file, wich adds environment variables to the
    # the program.
    load_dotenv(verbose=False)

    app = Flask(__name__)
    app.secret_key = os.getenv("DIGICUBES_SECRET", '_5#y2L"F4Q8z\n\xec]/')
    app.config["DC_COOKIE_NAME"] = "digitoken"
    app.config["secret"] = app.secret_key

    @app.errorhandler(DigiCubeError)
    def handle_digicube_error(error):  # pylint: disable=unused-variable
        logger.exception("Error occurred. Going back to login page.")
        digicubes.logout()
        return redirect(url_for("account.login"))

    @app.errorhandler(404)
    def page_not_found(error):  # pylint: disable=unused-variable
        return redirect(url_for("account.login"))

    @app.template_filter()
    def gravatar(email: str) -> str:  # pylint: disable=unused-variable

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

        # return f"Converting not possible. Illegal type:{type(dtstr)}"
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
            # So we have a token. Now lets refresh it
            try:
                data = accm.refresh_token(token)

                # current_user.token = token
                current_user.set_data(data)
                g.digitoken_received = True
            except TokenExpired:
                current_user.reset()
                logger.warning("Token was send by the client, but it is expired on the server.")

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # C O N F I G U R A T I O N
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    # Loading the logging configuration. If no logging configuration
    # is found, it will fall back to logging.basicConfiguration
    logging.basicConfig(level=logging.DEBUG)

    # Initalizes the account manager extension, wich is responsible for the the
    # login and logout procedure.
    the_account_manager.init_app(app)
    mail_cube.init_app(app)
    babel.init_app(app)

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
    url_prefix = "/admin"
    logger.debug("Register admin blueprint at %s", url_prefix)
    app.register_blueprint(admin_blueprint, url_prefix=url_prefix)

    # Headmaster blueprint
    url_prefix = "/headmaster"
    logger.debug("Register headmaster blueprint at %s", url_prefix)
    app.register_blueprint(headmaster_blueprint, url_prefix=url_prefix)

    # Teacher blueprint
    url_prefix = "/teacher"
    logger.debug("Register teacher blueprint at %s", url_prefix)
    app.register_blueprint(teacher_blueprint, url_prefix=url_prefix)

    url_prefix = "/student"
    logger.debug("Register student blueprint at %s", url_prefix)
    app.register_blueprint(student_blueprint, url_prefix=url_prefix)

    # Register all known blueprints
    register_blueprints(app)

    logger.info("Static folder is %s", app.static_folder)
    return app
