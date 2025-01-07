"""File change detection for fabric-to-espanso."""
from typing import List, Tuple, Dict, Any
from datetime import datetime
import logging

from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from qdrant_client.http.exceptions import UnexpectedResponse

from .file_processor import process_markdown_files
from .config import config
from .exceptions import DatabaseError

logger = logging.getLogger('fabric_to_espanso')

def get_stored_files(client: QdrantClient, collection_name: str = "markdown_files") -> Dict[str, Any]:
    """Get all files stored in the database.
    
    Args:
        client: Initialized Qdrant client
        collection_name: Name of the collection to query
        
    Returns:
        Dict mapping filenames to their database records
        
    Raises:
        DatabaseError: If query fails
    """
    try:
        stored_files = client.scroll(
            collection_name=collection_name,
            limit=10000  # Adjust based on expected file count
        )[0]
        return {
            file.payload['filename']: {
                'payload': file.payload,
                'id': file.id,
                'vector': file.vector
            }
            for file in stored_files
        }
    except UnexpectedResponse as e:
        raise DatabaseError(f"Failed to query stored files: {str(e)}") from e

def compare_file_dates(
    current_date: datetime,
    stored_date_str: str
) -> bool:
    """Compare file modification dates.
    
    Args:
        current_date: Current file's modification date
        stored_date_str: Stored file's modification date string
        
    Returns:
        True if file is modified, False otherwise
    """
    stored_date = datetime.strptime(stored_date_str, '%Y-%m-%dT%H:%M:%S.%f')
    return current_date > stored_date

def detect_file_changes(
    client: QdrantClient,
    markdown_folder: str = config.markdown_folder
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[str]]:
    """Detect changes in markdown files by comparing with database.
    
    Args:
        client: Initialized Qdrant client
        markdown_folder: Folder containing markdown files
        
    Returns:
        Tuple containing:
            - List of new files
            - List of modified files
            - List of deleted files
            
    Raises:
        DatabaseError: If database query fails
        OSError: If file system operations fail
    """
    try:
        # Get current files
        current_files = process_markdown_files(markdown_folder)
        logger.debug(f"Found {len(current_files)} files in {markdown_folder}")
        
        # Get stored files from database
        stored_files = get_stored_files(client)
        logger.debug(f"Found {len(stored_files)} files in database")
        
        # Initialize change lists
        new_files: List[Dict[str, Any]] = []
        modified_files: List[Dict[str, Any]] = []
        deleted_files: List[str] = []
        
        # Check for new and modified files
        for file in current_files:
            filename = file['filename']
            if filename not in stored_files:
                logger.debug(f"New file detected: {filename}")
                new_files.append(file)
            elif compare_file_dates(
                file['last_modified'],
                stored_files[filename]['payload']['date']
            ):
                logger.debug(f"Modified file detected: {filename}")
                modified_files.append(file)
        
        # Check for deleted files
        current_filenames = {file['filename'] for file in current_files}
        deleted_files = [
            filename for filename in stored_files
            if filename not in current_filenames
        ]
        
        if deleted_files:
            logger.debug(f"Deleted files detected: {deleted_files}")
        
        # Log summary
        logger.info(
            f"Changes detected:"
            f" {len(new_files)} new,"
            f" {len(modified_files)} modified,"
            f" {len(deleted_files)} deleted"
        )
        
        return new_files, modified_files, deleted_files
        
    except Exception as e:
        logger.error(f"Error detecting file changes: {str(e)}", exc_info=True)
        if isinstance(e, (DatabaseError, OSError)):
            raise
        raise RuntimeError(f"Unexpected error detecting changes: {str(e)}") from e