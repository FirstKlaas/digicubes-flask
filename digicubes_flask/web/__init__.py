"""
A minimal startscript for the server. This can be used
as a quickstart module.
"""
import datetime
import logging

from importlib.resources import open_text
from typing import Optional

from flask import Flask, redirect, url_for, Response, request, Request
from flask_moment import Moment
import yaml

from digicubes_client.client.proxy import RightProxy, RoleProxy
from digicubes_flask import account_manager as accm, current_user

from .account_manager import DigicubesAccountManager

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)

from markdown import markdown

# moment = Moment()


def create_app():
    """
    Factory function to create the flask server.
    Flask will automatically detect the method
    on `flask run`.
    """
    from logging.config import dictConfig  # pylint: disable=import-outside-toplevel
    from digicubes_flask.web.modules import (
        account_blueprint,
        admin_blueprint,
    )  # pylint: disable=import-outside-toplevel

    app = Flask(__name__)
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # TODO: Set via configuration
    # moment.init_app(app)

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
    def md(txt: str) -> str: # pylint: disable=unused-variable
        return markdown(txt)

    @app.template_filter()
    def digitime(dtstr): # pylint: disable=unused-variable
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
        """
        Nach jedem Request das Token aktualisieren, damit das Zeitfenster
        der Gültigkeit des Tokens beu beginnt.

        Das wird somit eigentlich viel zu oft gemacht und frisst unnötig
        Ressourccen, ist aber der einfachste weg. Alternativ müsste der
        Client umgebaut werden, da er bereits in jedem Response ein
        neues Token sendet.
        """
        if accm is not None:
            if not accm.token:
                logger.debug("No token. Igoring response.")
            else:
                # TODO: Den call könnte man asynchron machen, weil die
                # Aktuslisierung des Tokens für den aktuellen Request
                # nicht wichtig ist und der zusätzliche Call einen
                # minimalen Performance Verlust bedeutet.
                logger.debug("Refreshing token in 'at the end oth the request.")
                new_token = accm.refresh_token()
                current_user.token = new_token
        else:
            logger.info("No account manager in request scope found. Maybe not an issue.")

        return response

    # Load the default settings and then load the custom settings
    # THe default settings are stored in this package and have to be loaded
    # as a ressource.
    with open_text("digicubes_flask.cfg", "default_configuration.yaml") as f:
        settings = yaml.safe_load(f)
        app.config.update(settings)

    # Loading the logging configuration. If no logging configuration
    # is found, it will fall back to logging.basicConfiguration
    with open_text("digicubes_flask.cfg", "logging.yaml") as f:
        settings = yaml.safe_load(f)
        try:
            dictConfig(settings)
            logger.info("Configured logging")
        except ValueError:
            logging.basicConfig(level=logging.DEBUG)
            logger.fatal("Could not configure logging.", exc_info=True)

    # Initalizes the account manager extension, wich is responsible for the the
    # login and logout procedure.
    the_account_manager = DigicubesAccountManager()
    the_account_manager.init_app(app)

    # ----------------------------------------
    # Now check, if we have the basic entities
    # ----------------------------------------
    core_roles = app.config["DIGICUBES_SYS_ROLES"]

    # Create a list of unique right_names
    rights = []
    for role in core_roles:
        for right in role["rights"]:
            if right not in rights:
                rights.append(right)

    # ---------------------------
    # Now register the blueprints
    # ---------------------------

    # Account blueprint
    url_prefix = app.config.get("DIGICUBES_ACCOUNT_URL_PREFIX")
    logger.debug("Register account blueprint at %s", url_prefix)
    app.register_blueprint(account_blueprint, url_prefix=url_prefix)

    # Admin blueprint
    url_prefix = app.config.get("DIGICUBES_ADMIN_URL_PREFIX", "/admin")
    logger.debug("Register admin blueprint at %s", url_prefix)
    app.register_blueprint(admin_blueprint, url_prefix=url_prefix)

    logger.info("Static folder is %s", app.static_folder)
    return app
