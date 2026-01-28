######################################################################
# Copyright 2016, 2022 John J. Rofrano. All Rights Reserved.
######################################################################

"""
Package: service
Package for the application models and service routes
This module creates and configures the Flask app and sets up the logging
and SQL database
"""
import sys
from flask import Flask
from service import config
from service.common import log_handlers

# NOTE: Do not change the order of this code
# The Flask app must be created BEFORE you import modules that depend on it !!!

# Create the Flask app
app = Flask(__name__)  # pylint: disable=invalid-name

# Load Configurations
app.config.from_object(config)

# Import dependencies AFTER app creation
from service import routes, models        # noqa: F401, E402
from service.common import error_handlers, cli_commands  # noqa: F401, E402

# Set up logging for production
log_handlers.init_logging(app, "gunicorn.error")

app.logger.info(70 * "*")
app.logger.info(
    "  P R O D U C T   D E M O   S E R V I C E   R U N N I N G  ".center(70, "*")
)
app.logger.info(70 * "*")

try:
    models.init_db(app)
except Exception as error:  # pylint: disable=broad-except
    app.logger.critical("%s: Cannot continue", error)
    sys.exit(4)

app.logger.info("Service initialized!")
