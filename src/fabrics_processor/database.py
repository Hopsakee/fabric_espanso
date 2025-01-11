"""Database management for fabric-to-espanso."""
from typing import Optional, List, Dict
import logging
import time

from qdrant_client import QdrantClient
from qdrant_client.http import models, exceptions
from qdrant_client.http.models import Distance, VectorParams, PointStruct

from .config import config
from .exceptions import DatabaseConnectionError, CollectionError, DatabaseInitializationError, ConfigurationError

logger = logging.getLogger('fabric_to_espanso')

def create_database_connection(url: Optional[str] = None) -> QdrantClient:
    """Create a database connection.
    
    Args:
        url: Optional database URL. If not provided, uses configuration.
        
    Returns:
        QdrantClient: Connected database client
        
    Raises:
        DatabaseConnectionError: If connection fails after retries
    """
    url = url or config.database.url
    for attempt in range(config.database.max_retries + 1):
        try:
            client = QdrantClient(
                url=url,
                timeout=config.database.timeout
            )
            # Test connection
            client.get_collections()
            return client
        except Exception as e:
            if attempt == config.database.max_retries:
                raise DatabaseConnectionError(
                    f"Failed to connect to database at {url} after "
                    f"{config.database.max_retries} attempts: {str(e)}"
                ) from e
            logger.warning(
                f"Connection attempt {attempt + 1} failed, retrying in "
                f"{config.database.retry_delay} seconds..."
            )
            time.sleep(config.database.retry_delay)

def initialize_qdrant_database(
    collection_name: str = config.embedding.collection_name,
    use_fastembed: bool = config.embedding.use_fastembed,
    embed_model: str = config.embedding.model_name
) -> QdrantClient:
    """Initialize the Qdrant database for storing markdown file information.
    
    Args:
        collection_name: Name of the collection to initialize
        use_fastembed: Whether to use FastEmbed for embeddings
        embed_model: Name of the embedding model to use
        
    Returns:
        QdrantClient: Initialized database client
        
    Raises:
        DatabaseInitializationError: If initialization fails
        CollectionError: If collection creation fails
        ConfigurationError: If configuration is invalid
    """
    try:
        # Validate configuration
        config.validate()
        
        # Create database connection
        client = create_database_connection()
        
        # Check if collection exists
        collections = client.get_collections()
        collection_names = [c.name for c in collections.collections]
        
        if collection_name not in collection_names:
            logger.info(f"Creating new collection: {collection_name}")
            
            # Create collection with appropriate vector configuration
            if use_fastembed:
                vector_config = client.get_fastembed_vector_params()
            else:
                vector_config = {
                    embed_model: VectorParams(
                        size=config.embedding.vector_size,
                        distance=Distance.COSINE
                    )
                }
            
            try:
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=vector_config,
                    on_disk_payload=True
                )
            except exceptions.UnexpectedResponse as e:
                raise CollectionError(
                    f"Failed to create collection {collection_name}: {str(e)}"
                ) from e
            
            # Create indexes for efficient searching
            for field_name, field_type in [
                ("filename", models.PayloadSchemaType.KEYWORD),
                ("date", models.PayloadSchemaType.DATETIME)
            ]:
                client.create_payload_index(
                    collection_name=collection_name,
                    field_name=field_name,
                    field_schema=field_type
                )
            logger.info(f"Created indexes for collection {collection_name}")
        
        # Log collection status
        collection_info = client.get_collection(collection_name)
        logger.info(
            f"Collection {collection_name} ready with "
            f"{collection_info.points_count} points"
        )
        
        return client
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}", exc_info=True)
        if isinstance(e, (DatabaseConnectionError, CollectionError)):
            raise
        raise DatabaseInitializationError(str(e)) from e

def validate_database_payload(
    client: QdrantClient,
    collection_name: str,
    ) -> Dict:
    """Validate the payload of all points in the Qdrant database.
    
    Args:
        client: Initialized Qdrant client
        collection_name: Name of the collection to validate
    """

    # First validate existing points in database
    logger.info("Validating existing database points...")
    offset = None
    
    while True:
        scroll_result = client.scroll(
            collection_name=collection_name,
            limit=5, # Process in batches of 5
            offset=offset
        )
        
        points, offset = scroll_result
        
        for point in points:
            try:
                fixed_payload = validate_point_payload(point.payload, point.id)
                if fixed_payload != point.payload:
                    # Update point with fixed payload
                    point_struct = PointStruct(
                        id=point.id,
                        vector=point.vector,
                        payload=fixed_payload
                    )
                    client.upsert(collection_name=collection_name, points=[point_struct])
                    logger.info(f"Fixed and updated point {point.id} in database")
            except ConfigurationError as e:
                logger.error(str(e))
        
        if not offset:  # No more points to process
            break
    
    logger.info("Database validation completed")

def validate_point_payload(payload: dict, point_id: Optional[str] = None) -> dict:
    """Validate and fix point payload fields.
    Only use if somehow many points have become corrupted.
    
    Args:
        payload (dict): Point payload to validate
        point_id (str, optional): ID of the point for logging purposes
        
    Returns:
        dict: Validated and potentially fixed payload
        
    Raises:
        ConfigurationError: If required fields are missing and cannot be fixed
    """
    print(f"Validating point {point_id if point_id else ''}")
    from .exceptions import ConfigurationError
    
    # Check for critical fields
    if 'filename' not in payload or 'content' not in payload:
        error_msg = f"Point {point_id if point_id else ''} is missing critical fields: "
        error_msg += "'filename' and/or 'content' are required and cannot be defaulted"
        raise ConfigurationError(error_msg)
        
    # Copy payload to avoid modifying the original
    fixed_payload = payload.copy()
    
    # Apply defaults and fixes for non-critical fields
    if 'purpose' not in fixed_payload or not fixed_payload['purpose']:
        fixed_payload['purpose'] = fixed_payload['content']
        logger.warning(f"Point {point_id if point_id else ''}: 'purpose' was missing, set to content value")
        
    if 'filesize' not in fixed_payload:
        fixed_payload['filesize'] = self.required_fields_defaults['filesize']
        logger.warning(f"Point {point_id if point_id else ''}: 'filesize' was missing, set to {self.required_fields_defaults['filesize']}")
        
    if 'trigger' not in fixed_payload:
        fixed_payload['trigger'] = self.required_fields_defaults['trigger']
        logger.warning(f"Point {point_id if point_id else ''}: 'trigger' was missing, set to {self.required_fields_defaults['trigger']}")
        
    return fixed_payload