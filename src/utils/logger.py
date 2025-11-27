from loguru import logger
import sys
import os

# Ensure the logs directory exists
os.makedirs("storage/logs", exist_ok=True)

# Configure logger
logger.remove() # Remove default handler
logger.add(sys.stderr, level="INFO") # Add console handler
logger.add("storage/logs/hyperspin.log", rotation="10 MB", retention="10 days", level="DEBUG")

def get_logger():
    return logger
