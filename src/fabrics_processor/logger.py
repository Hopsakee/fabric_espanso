import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Module level logger instance
_logger = None

def setup_logger(log_file='fabric_to_espanso.log'):
    """
    Set up and configure the logger for the application.

    Args:
        log_file (str): Name of the log file. Defaults to 'fabric_to_espanso.log'.

    Returns:
        logging.Logger: Configured logger object.
    """
    global _logger
    if _logger is not None:
        return _logger
        
    logger = logging.getLogger('fabric_to_espanso')
    
    # Clean up any existing handlers
    logger.handlers.clear()
    
    # Set log level and prevent propagation
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # Get the project root directory (2 levels up from logger.py)
    project_root = Path(__file__).parent.parent.parent

    # Create logs directory if it doesn't exist - use absolute path
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)

    # Create file handlers with absolute path
    log_file_path = log_dir / f"{log_file}"
    file_handler = RotatingFileHandler(log_file_path, maxBytes=1024*1024, backupCount=5)
    console_handler = logging.StreamHandler()

    # Set log levels
    file_handler.setLevel(logging.INFO)
    console_handler.setLevel(logging.INFO)

    # Create formatters and add it to handlers
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    
    file_handler.setFormatter(file_format)
    console_handler.setFormatter(console_format)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    _logger = logger
    return logger