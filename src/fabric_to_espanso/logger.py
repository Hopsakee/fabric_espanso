import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(log_file='fabric_to_espanso.log'):
    """
    Set up and configure the logger for the application.

    Args:
        log_file (str): Name of the log file. Defaults to 'fabric_to_espanso.log'.

    Returns:
        logging.Logger: Configured logger object.
    """
    logger = logging.getLogger('fabric_to_espanso')
    logger.setLevel(logging.DEBUG)

    # Create logs directory if it doesn't exist
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create handlers
    file_handler = RotatingFileHandler(os.path.join(log_dir, log_file), maxBytes=1024*1024, backupCount=5)
    console_handler = logging.StreamHandler()

    # Create formatters and add it to handlers
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)
    console_handler.setFormatter(console_format)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger