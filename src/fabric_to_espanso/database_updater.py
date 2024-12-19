from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, Filter, FieldCondition, MatchValue, PointIdsList
from fastembed import TextEmbedding
import logging
import uuid
from .yaml_file_generator import generate_yaml_file

from parameters import USE_FASTEMBED, EMBED_MODEL
from src.fabric_to_espanso.config import config

logger = logging.getLogger('fabric_to_espanso')


def get_embedding(text: str, embedding_model: TextEmbedding) -> list:
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
    # Initialize the FastEmbed model (done once)
    if config.embedding.use_fastembed:
        # TODO: I think it is possible to choose another model here. Make that an option
        logger.info(f"Initializing FastEmbed model.")
        embedding_model = TextEmbedding()
    else:
        logger.info(f"Initializing embbeding model: {config.model_name}")
        # TODO: testen. Weet niet of dit werkt.
        embedding_model = TextEmbedding(model_name=config.model_name)

    try:
        # Add new files
        for file in new_files:
            point = PointStruct(
                id=str(uuid.uuid4()),  # Generate a new UUID for each point
                # TODO: 'fast-bge-small-en' is de naam van de vector. Je kunt de naam vinden door: client.get_vector_field_name()
                vector={'fast-bge-small-en':
                        get_embedding(file['purpose'], embedding_model)},  # Generate vector from purpose field
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
                    # LET OP: als je 'fastembed' gebruikt, moet je de naam van de vector gebruiken.
                    # In dit geval is de naam 'fast-bge-small-en'.
                    # Gebruik je fastembed niet, maar rechtstreeks de QDRANT api, dan kun je ook gebruik maken
                    # van unnamed vectors en kun je dus schrrijven vector = get_embedding(file['purpose'], embedding_model)
                    # Zie https://github.com/qdrant/qdrant-client/discussions/598
                    # De naam die fastembed gebruikt is afhankelijk van het model dat je gebruikt.
                    # Je kunt de naam vinden door: client.get_vector_field_name()
                    vector={'fast-bge-small-en': 
                            get_embedding(file['purpose'], embedding_model)},  # Generate vector from purpose field
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
        generate_yaml_file(client, config.yaml_output_folder)

    except Exception as e:
        logger.error(f"Error updating Qdrant database: {str(e)}", exc_info=True)