from src.fabric_to_espanso.database import initialize_qdrant_database
from src.fabric_to_espanso.file_change_detector import detect_file_changes
from src.fabric_to_espanso.database_updater import update_qdrant_database
from src.fabric_to_espanso.yaml_file_generator import generate_yaml_file
from src.fabric_to_espanso.logger import setup_logger
from parameters import MARKDOWN_FOLDER, YAML_OUTPUT_FOLDER
import logging

# Reload the imports if necessary
# import importlib
# importlib.reload(parameters)
# MARKkDOWN_FOLDER = parameters.MARKDOWN_FOLDER
# YAML_OUTPUT_FOLDER = parameters.YAML_OUTPUT_FOLDER

# Setup logger
logger = setup_logger()

def main():
    try:
        print("Fabric to Espanso conversion process started")
        logger.info(f"Attempting to initialize Qdrant database with location: http://localhost:6333/")
        # Initialize Qdrant database
        client = initialize_qdrant_database()
        logger.debug(f"Qdrant client object: {client}")
        logger.info(f"Markdown folder: {MARKDOWN_FOLDER}")
        logger.info(f"YAML output folder: {YAML_OUTPUT_FOLDER}")
        logger.info("Application started successfully")

        # Detect file changes, passing the client
        new_files, modified_files, deleted_files = detect_file_changes(client)

        # Log the results
        logger.info(f"New files: {[file['filename'] for file in new_files]}")
        logger.info(f"Modified files: {[file['filename'] for file in modified_files]}")
        logger.info(f"Deleted files: {deleted_files}")

        # Update Qdrant database
        update_qdrant_database(client, new_files, modified_files, deleted_files)

        # Generate YAML file from current database state
        if new_files or modified_files or deleted_files:
            logger.info("Changes detected. Updating YAML file.")
            generate_yaml_file(client)
        else:
            logger.info("No changes detected. Generating YAML file from current database state.")
            generate_yaml_file(client)

        logger.info("Fabric to Espanso conversion process completed successfully")
    except Exception as e:
        logger.error(f"An error occurred during the conversion process: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()