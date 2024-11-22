from src.fabric_to_espanso.database import initialize_qdrant_database
from src.fabric_to_espanso.logger import setup_logger
from parameters import QDRANT_DB_LOCATION, MARKDOWN_FOLDER, YAML_OUTPUT_FOLDER, FABRIC_PURPOSES_FILE
from src.fabric_to_espanso.file_processor import process_markdown_files

# Setup logger
logger = setup_logger()

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
except Exception as e:
    logger.critical(f"Failed to start the application: {str(e)}", exc_info=True)

try:
    markdown_files = process_markdown_files()
    logger.info(f"Processed {len(markdown_files)} markdown files")
except Exception as e:
    logger.error(f"Error processing markdown files: {str(e)}", exc_info=True)