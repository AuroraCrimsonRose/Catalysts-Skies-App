from cat_logger import logger

# App config
DEBUG_MODE = False # Set to True for debug mode
LOG_TEST = False # Set to True to enable test logging
API_BASE_URL = "http://localhost:8000/api" # Base URL for the API

# Internal variable for debug output, do not modify
DEBUG_OUTPUT = True

# Function to enable debugging mode
def debugging_mode():
    if DEBUG_MODE:
        DEBUG_OUTPUT = True
        logger.warning("Running in DEBUG mode! This is not suitable for production use.")