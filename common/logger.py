import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Get the project root directory (parent of common)
PROJECT_ROOT = Path(__file__).parent.parent

# Create logs directory in project root
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Create log file with timestamp
LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
LOG_FILE_PATH = LOG_DIR / LOG_FILE

# Configure logging
logging.basicConfig(
    filename=str(LOG_FILE_PATH),
    format="[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Also log to console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter(
    "[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
console_handler.setFormatter(console_formatter)

# Get root logger and add console handler
logger = logging.getLogger()
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)

# Export logger for use in other modules
__all__ = ["logger", "LOG_FILE_PATH"]

