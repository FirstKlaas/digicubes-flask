"""
A minimal startscript for the server. This can be used
as a quickstart module.
"""
import logging

from importlib.resources import open_text
from typing import Optional

from flask import Flask, redirect, url_for, Response, request, Request
from flask_moment import Moment
import yaml

from .account_manager import DigicubesAccountManager

logger = logging.getLogger(__name__)

account_manager = DigicubesAccountManager()

logging.basicConfig(level=logging.DEBUG)

moment = Moment()

def create_app():
    """
    Factory function to create the flask server.
    Flask will automatically detect the method
    on `flask run`.
    """
    from logging.config import dictConfig
    from digicubes_flask.web.modules import account_blueprint, admin_blueprint

    app = Flask(__name__)
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # TODO: Set via configuration
    moment.init_app(app)

    # Load the default settings and then load the custom settings
    # THe default settings are stored in this package and have to be loaded
    # as a ressource.
    print("reading settings")
    # with open_text("digicubes_flask.cfg", "default_configuration.yaml") as f:
    #    settings = yaml.safe_load(f)
    #    print(settings)

    with open_text("digicubes_flask.cfg", "default_configuration.yaml") as f:
        settings = yaml.safe_load(f)
        app.config.update(settings)

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
    account_manager.init_app(app)

    # Now register the blueprints

    # Account blueprint
    url_prefix = app.config.get("DIGICUBES_ACCOUNT_URL_PREFIX")
    logger.debug("Register account blueprint at %s", url_prefix)
    app.register_blueprint(account_blueprint, url_prefix=url_prefix)

    # Admin blueprint
    url_prefix = app.config.get("DIGICUBES_ADMIN_URL_PREFIX", "/admin")
    logger.debug("Register admin blueprint at %s", url_prefix)
    app.register_blueprint(admin_blueprint, url_prefix=url_prefix)

    # for key, value in app.config.items():
    #    logger.debug("%s: %s", key, value)

    logger.debug("Static folder is %s", app.static_folder)
    return app
