"""
digiweb

Usage:
  digiweb --template=<name>
  digiweb [--config=<name>] [-d | --development | -p | --production | -t | --testing]

Options:
  --template=<name>   Name of a file to write default settings to. Defaults to 'account.yaml'
  --config=<name>     Name of the configuration file. Defaults to 'digicubes.yaml'
  -d --development  Starts the server in development mode
  -p --production   Starts the server in production mode (default)
  -t --testing      Starts the server in testing mode
"""
import logging
import os

from docopt import docopt

logger = logging.getLogger(__name__)


def run():
    """Runs the server"""
    arguments = docopt(__doc__, help=True, version="Run DigiCubes Webserver 1.0")

    # Setting up the environment
    if arguments["--development"]:
        os.environ["FLASK_ENV"] = "development"
    elif arguments["--testing"]:
        os.environ["FLASK_ENV"] = "testing"
    else:
        os.environ["FLASK_ENV"] = "production"


if __name__ == "__main__":
    run()
