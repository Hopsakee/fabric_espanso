"""Main entry point for the Fabric to Espanso conversion process."""
from typing import Optional
import sys
import signal
import logging
from contextlib import contextmanager

from src.fabrics_processor.database import initialize_qdrant_database
from src.fabrics_processor.file_change_detector import detect_file_changes
from src.fabrics_processor.database_updater import update_qdrant_database
from src.fabrics_processor.yaml_file_generator import generate_yaml_file
from src.fabrics_processor.logger import setup_logger
from src.fabrics_processor.config import config
from src.fabrics_processor.exceptions import (
    DatabaseConnectionError,
    DatabaseInitializationError
)

# Setup logger
logger = setup_logger()

class GracefulExit(SystemExit):
    """Custom exception for graceful shutdown."""
    pass

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info(f"Received signal {signum}. Initiating graceful shutdown...")
    raise GracefulExit()

@contextmanager
def managed_qdrant_client():
    """Context manager for handling Qdrant client lifecycle."""
    client = None
    try:
        client = initialize_qdrant_database()
        yield client
    finally:
        if client:
            logger.info("Closing Qdrant client connection...")
            client.close()
            logger.info("Qdrant client connection closed")

def process_changes(client) -> bool:
    """Process file changes and update database and YAML files.
    
    Args:
        client: Initialized Qdrant client
        
    Returns:
        bool: True if processing was successful, False otherwise
    """
    try:
        # Detect file changes
        new_files, modified_files, deleted_files = detect_file_changes(client, config.fabric_patterns_folder)

        # Log the results
        if new_files:
            logger.info(f"New files: {[file['filename'] for file in new_files]}")
        if modified_files:
            logger.info(f"Modified files: {[file['filename'] for file in modified_files]}")
        if deleted_files:
            logger.info(f"Deleted files: {deleted_files}")
            
        # Update database if there are changes
        if any([new_files, modified_files, deleted_files]):
            logger.info("Changes detected. Updating database...")
            update_qdrant_database(client, new_files, modified_files, deleted_files)
            
        # Always generate output files to ensure consistency
        generate_yaml_file(client, config.yaml_output_folder)

        return True
        
    except Exception as e:
        logger.error(f"Error processing changes: {str(e)}", exc_info=True)
        return False

def main() -> Optional[int]:
    """Main application entry point.
    
    Returns:
        Optional[int]: Exit code, None if successful, 1 if error
    """
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        logger.info("Fabric to Espanso conversion process started")
        
        # Log configuration
        logger.info(f"Using configuration:")
        logger.info(f"  Database URL: {config.database.url}")
        logger.info(f"  Fabric patterns folder: {config.fabric_patterns_folder}")
        logger.info(f"  YAML output folder: {config.yaml_output_folder}")
        logger.info(f"  Obsidian textgenerator markdown output folder: {config.markdown_output_folder}")
        logger.info(f"  Obsidian personal prompts input folder: {config.obsidian_input_folder}") 
        
        # Process changes with managed client
        with managed_qdrant_client() as client:
            if process_changes(client):
                logger.info("Fabric to Espanso conversion completed successfully")
                return None
            else:
                logger.error("Fabric to Espanso conversion completed with errors")
                return 1
                
    except GracefulExit:
        logger.info("Gracefully shutting down...")
        return None
    except (DatabaseConnectionError, DatabaseInitializationError) as e:
        logger.error(f"Database error: {str(e)}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main() or 0)