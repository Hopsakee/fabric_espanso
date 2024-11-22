from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from .file_processor import process_markdown_files
from parameters import MARKDOWN_FOLDER
import logging

logger = logging.getLogger('fabric_to_espanso')

def detect_file_changes(client):
    """
    Detect changes in markdown files by comparing with the Qdrant database.

    Args:
        client (QdrantClient): An initialized Qdrant client.

    Returns:
        tuple: Lists of new, modified, and deleted files.
    """
    try:
        # Get all markdown files from the specified folder
        current_files = process_markdown_files()
        logger.debug(f"Current files: {[file['filename'] for file in current_files]}")

        # Query Qdrant for all stored file information
        stored_files = client.scroll(
            collection_name="markdown_files",
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="filename",
                        match=MatchValue(value="")
                    )
                ]
            ),
            limit=10000  # Adjust this value based on your expected number of files
        )[0]
        logger.debug(f"Stored files in Qdrant: {[file.payload['filename'] for file in stored_files]}")

        # Convert stored files to a dictionary for easy comparison
        stored_files_dict = {file.payload['filename']: file for file in stored_files}

        new_files = []
        modified_files = []
        deleted_files = []

        # Check for new and modified files
        for file in current_files:
            if file['filename'] not in stored_files_dict:
                new_files.append(file)
            elif file['last_modified'] > stored_files_dict[file['filename']].payload['date']:
                modified_files.append(file)

        # Check for deleted files
        current_filenames = set(file['filename'] for file in current_files)
        deleted_files = [
            filename for filename in stored_files_dict.keys()
            if filename not in current_filenames
        ]

        logger.debug(f"New files: {[file['filename'] for file in new_files]}")
        logger.debug(f"Modified files: {[file['filename'] for file in modified_files]}")
        logger.debug(f"Deleted files: {deleted_files}")

        logger.info(f"Detected {len(new_files)} new files, {len(modified_files)} modified files, and {len(deleted_files)} deleted files.")

        return new_files, modified_files, deleted_files

    except Exception as e:
        logger.error(f"Error detecting file changes: {str(e)}", exc_info=True)
        return [], [], []