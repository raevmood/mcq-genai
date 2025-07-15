import logging
import os
from datetime import datetime

# Define the log file name with a timestamp
LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"

# Define the path for the logs directory
# os.path.join is used for cross-platform compatibility
log_path = os.path.join(os.getcwd(), "logs")

# Create the logs directory if it doesn't exist
os.makedirs(log_path, exist_ok=True)

# Define the full log file path
LOG_FILEPATH = os.path.join(log_path, LOG_FILE)

# Configure the basic logging settings
logging.basicConfig(
    level=logging.INFO,
    filename=LOG_FILEPATH,
    # A detailed format for log messages
    format="[%(asctime)s] line:%(lineno)d %(name)s - %(levelname)s - %(message)s"
)
