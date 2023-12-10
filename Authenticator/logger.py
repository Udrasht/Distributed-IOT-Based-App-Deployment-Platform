import logging

# Create a logger object
logger = logging.getLogger(__name__)

# Set the logging level to DEBUG
logger.setLevel(logging.DEBUG)

# Create a file handler and add it to the logger
file_handler = logging.FileHandler('/logs/auth_logs.log')
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

# Define the logging format & Set the formatter for the file handler
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
file_handler.setFormatter(formatter)
