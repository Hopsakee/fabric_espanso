from src.fabric_to_espanso.database import initialize_qdrant_database
from src.fabric_to_espanso.file_change_detector import detect_file_changes
from src.fabric_to_espanso.database_updater import update_qdrant_database
from src.fabric_to_espanso.logger import setup_logger
from parameters import QDRANT_DB_LOCATION, MARKDOWN_FOLDER, YAML_OUTPUT_FOLDER, FABRIC_PURPOSES_FILE
import logging

# Setup logger
logger = setup_logger()

def main():
    try:
        logger.info(f"Attempting to initialize Qdrant database with location: {QDRANT_DB_LOCATION}")
        # Initialize Qdrant database
        client = initialize_qdrant_database()
        logger.info(f"Qdrant database initialized successfully at {QDRANT_DB_LOCATION}")
        logger.debug(f"Qdrant client object: {client}")
        logger.info(f"Markdown folder: {MARKDOWN_FOLDER}")
        logger.info(f"YAML output folder: {YAML_OUTPUT_FOLDER}")
        logger.info(f"Fabric purposes file: {FABRIC_PURPOSES_FILE}")
        logger.info("Application started successfully")

        # Detect file changes, passing the client
        new_files, modified_files, deleted_files = detect_file_changes(client)

        # Log the results
        logger.info(f"New files: {[file['filename'] for file in new_files]}")
        logger.info(f"Modified files: {[file['filename'] for file in modified_files]}")
        logger.info(f"Deleted files: {deleted_files}")

        # Update Qdrant database
        update_qdrant_database(client, new_files, modified_files, deleted_files)

        logger.info("Fabric to Espanso conversion process completed successfully")
    except Exception as e:
        logger.error(f"An error occurred during the conversion process: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()