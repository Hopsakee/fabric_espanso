from parameters import QDRANT_DB_LOCATION
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams
import logging
import os

logger = logging.getLogger('fabric_to_espanso')

def initialize_qdrant_database():
    """
    Initialize the Qdrant database with the required schema for storing markdown file information.

    Returns:
        QdrantClient: An instance of the Qdrant client.
    """
    try:
        logger.info(f"Attempting to initialize Qdrant database at location: {QDRANT_DB_LOCATION}")
        logger.debug(f"Current working directory: {os.getcwd()}")

        # Create a Qdrant client
        client = QdrantClient(path=QDRANT_DB_LOCATION)
        logger.info(f"QdrantClient created with path: {QDRANT_DB_LOCATION}")
        logger.debug(f"QdrantClient object: {client}")
        logger.info(f"Connected to Qdrant database at {QDRANT_DB_LOCATION}")

        # Define the collection name
        collection_name = "markdown_files"

        # Check if the collection already exists
        collections = client.get_collections()
        logger.debug(f"Existing collections: {[c.name for c in collections.collections]}")
        if collection_name not in [c.name for c in collections.collections]:
            # Create the collection with the required schema
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
                on_disk_payload=True
            )
            logger.info(f"Created new collection: {collection_name}")

            # Create payload indexes for efficient searching
            client.create_payload_index(
                collection_name=collection_name,
                field_name="filename",
                field_schema=models.PayloadSchemaType.KEYWORD
            )
            client.create_payload_index(
                collection_name=collection_name,
                field_name="date",
                field_schema=models.PayloadSchemaType.DATETIME
            )
            logger.info("Created payload indexes for 'filename' and 'date'")

        # Add this log to check the number of points in the collection
        collection_info = client.get_collection(collection_name)
        logger.debug(f"Number of points in the collection: {collection_info.points_count}")

        logger.info(f"Qdrant database initialized successfully at {QDRANT_DB_LOCATION}")
        return client
    except Exception as e:
        logger.error(f"Error initializing Qdrant database: {str(e)}", exc_info=True)
        raise