import sys
from loguru import logger
from pathlib import Path
from config import LOG_TEST
import time 

# Adjustable variables for trace truncation
TRACE_MAX = 30  # max length of trace before truncation
TRACE_TCT = 27  # length of trace to keep before truncation

LOG_PATH = Path("logs") / "app.log"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

# Clear previous handlers
logger.remove()

MSG_MAX = 46  # max length of message before truncation
MSG_TRUNCATE = 43  # length of message to keep before truncation

# Custom function to truncate message, but not for error or critical
def truncate_message(record):
    msg = record["message"]
    level = record["level"].name
    if level in ("ERROR", "CRITICAL"):
        return msg
    if len(msg) > MSG_MAX:
        return msg[:MSG_TRUNCATE] + "..."
    return msg

# Custom function to truncate or pad trace (centered)
def truncate_trace(record):
    trace = f"{record['name']}:{record['function']}:{record['line']}"
    if len(trace) > TRACE_MAX:
        return "..." + trace[-TRACE_TCT:]
    # Center the trace string within TRACE_MAX width
    return trace.center(TRACE_MAX)

# Standardized formatting with color blocks for levels
format_str = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<magenta>{extra[short_trace]}</magenta> |: "
    "<level>{extra[short_message]}</level>"
)

# Add a processor to inject the truncated message and trace
def add_short_fields(record):
    record["extra"]["short_message"] = truncate_message(record)
    record["extra"]["short_trace"] = truncate_trace(record)

logger = logger.patch(add_short_fields)

# Console handler
logger.add(sys.stdout, format=format_str, colorize=True, enqueue=True, backtrace=True, diagnose=True)

# Optional file logging with rotation
logger.add(LOG_PATH, format=format_str, rotation="1 MB", enqueue=True, backtrace=True, diagnose=True)

# Example usage
def setup_logger():
    logger.debug("Logger initialized")
    if LOG_TEST:
        logger.warning("###---Test logging is enabled.---###")
        logger.info("This is an info message for testing.")
        logger.debug("This is a debug message for testing.")
        logger.trace("This is a trace message for testing.")
        logger.warning("This is a warning message for testing.")
        logger.error("This is an error message for testing.")
        logger.critical("This is a critical message for testing.")
        logger.warning("###---  End of test logging.  ---###")
        pass