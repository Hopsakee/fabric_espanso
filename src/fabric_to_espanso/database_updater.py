from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
import logging
import uuid

logger = logging.getLogger('fabric_to_espanso')

def update_qdrant_database(client: QdrantClient, new_files: list, modified_files: list, deleted_files: list):
    """
    Update the Qdrant database based on detected file changes.

    Args:
        client (QdrantClient): An initialized Qdrant client.
        new_files (list): List of new files to be added to the database.
        modified_files (list): List of modified files to be updated in the database.
        deleted_files (list): List of deleted files to be removed from the database.
    """
    try:
        # Add new files
        for file in new_files:
            point = PointStruct(
                id=str(uuid.uuid4()),  # Generate a new UUID for each point
                vector=[0.0] * 384,  # Placeholder vector, replace with actual embedding
                payload={
                    "filename": file['filename'],
                    "content": file['content'],
                    "date": file['last_modified']
                }
            )
            client.upsert(collection_name="markdown_files", points=[point])
            logger.info(f"Added new file to database: {file['filename']}")

        # Update modified files
        for file in modified_files:
            point = PointStruct(
                id=str(uuid.uuid4()),  # Generate a new UUID for each point
                vector=[0.0] * 384,  # Placeholder vector, replace with actual embedding
                payload={
                    "filename": file['filename'],
                    "content": file['content'],
                    "date": file['last_modified']
                }
            )
            client.upsert(collection_name="markdown_files", points=[point])
            logger.info(f"Updated modified file in database: {file['filename']}")

        # Delete removed files
        for filename in deleted_files:
            # Query the database to find the point with the matching filename
            search_result = client.search(
                collection_name="markdown_files",
                query_vector=[0.0] * 384,  # Placeholder vector
                query_filter={"filename": filename},
                limit=1
            )
            if search_result:
                point_id = search_result[0].id
                client.delete(
                    collection_name="markdown_files",
                    points_selector={"ids": [point_id]}
                )
                logger.info(f"Deleted file from database: {filename}")
            else:
                logger.warning(f"File not found in database for deletion: {filename}")

        logger.info("Database update completed successfully")
    except Exception as e:
        logger.error(f"Error updating Qdrant database: {str(e)}", exc_info=True)