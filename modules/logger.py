import os
import logging
import logging.handlers
import datetime
from modules.paths_internal import script_path

logger = logging.getLogger("fastapi")
log_file = os.path.join(script_path, "logs/sd-api.log")
error_log_file = os.path.join(script_path, "logs/sd-error.log")

# create directory if it doesn't exist
os.makedirs(os.path.dirname(log_file), exist_ok=True)

# Set up the rotating file handler
log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
rotate_handler = logging.handlers.TimedRotatingFileHandler(log_file, when='midnight', interval=1, backupCount=7, atTime=datetime.time(0, 0, 0, 0))
rotate_handler.setFormatter(log_formatter)
logger.addHandler(rotate_handler)

# Set up the rotating file handler for errors
error_rotate_handler = logging.handlers.TimedRotatingFileHandler(error_log_file, when='midnight', interval=1, backupCount=30, atTime=datetime.time(0, 0, 0, 0))
error_rotate_handler.setFormatter(log_formatter)
error_rotate_handler.setLevel(logging.WARNING)
logger.addHandler(error_rotate_handler)

# Set up the console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)
