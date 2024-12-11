from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, Filter, FieldCondition, MatchValue, PointIdsList
from fastembed import TextEmbedding
import logging
import uuid
from .yaml_file_generator import generate_yaml_file

logger = logging.getLogger('fabric_to_espanso')

# Initialize the FastEmbed model (done once)
embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

def get_embedding(text: str) -> list:
    """
    Generate embedding vector for the given text using FastEmbed.
    
    Args:
        text (str): Text to generate embedding for
        
    Returns:
        list: Embedding vector
    """
    embeddings = list(embedding_model.embed([text]))
    return embeddings[0].tolist()

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
                vector=get_embedding(file['purpose']),  # Generate vector from purpose field
                payload={
                    "filename": file['filename'],
                    "content": file['content'],
                    "purpose": file['purpose'],
                    "date": file['last_modified'],
                    "trigger": file['trigger'],
                    "label": file['label']
                }
            )
            client.upsert(collection_name="markdown_files", points=[point])
            logger.info(f"Added new file to database: {file['filename']}")

        # Update modified files
        for file in modified_files:
            # Query the database to find the point with the matching filename
            scroll_result = client.scroll(
                collection_name="markdown_files",
                scroll_filter=Filter(
                    must=[FieldCondition(key="filename", match=MatchValue(value=file['filename']))]
                ),
                limit=1
            )[0]
            # TODO: Add handling of cases of multiple entries with the same filename
            if scroll_result:
                point_id = scroll_result[0].id
                # Update the existing point with the new file data
                point = PointStruct(
                    id=point_id,
                    vector=get_embedding(file['purpose']),  # Generate vector from purpose field
                    payload={
                        "filename": file['filename'],
                        "content": file['content'],
                        "purpose": file['purpose'],
                        "date": file['last_modified']
                    }
                )
                client.upsert(collection_name="markdown_files", points=[point])
                logger.info(f"Updated modified file in database: {file['filename']}")
            else:
                logger.warning(f"File not found in database for update: {file['filename']}")

        # Delete removed files
        for filename in deleted_files:
            # Query the database to find the point with the matching filename
            scroll_result = client.scroll(
                collection_name="markdown_files",
                scroll_filter=Filter(
                    must=[FieldCondition(key="filename", match=MatchValue(value=filename))]
                ),
                limit=1
            )[0]
            # TODO: Add handling of cases of multiple entries with the same filename
            if scroll_result:
                point_id = scroll_result[0].id
                client.delete(
                    collection_name="markdown_files",
                    points_selector=PointIdsList(points=[point_id])
                )
                logger.info(f"Deleted file from database: {filename}")
            else:
                logger.warning(f"File not found in database for deletion: {filename}")

        logger.info("Database update completed successfully")

        # Generate new YAML file after database update
        generate_yaml_file(client)

    except Exception as e:
        logger.error(f"Error updating Qdrant database: {str(e)}", exc_info=True)