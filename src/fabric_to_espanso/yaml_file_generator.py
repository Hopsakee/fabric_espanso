"""YAML file generation for fabric-to-espanso."""
from pathlib import Path
from typing import Dict, Any, List
import yaml
import logging

from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse

from .exceptions import DatabaseError

logger = logging.getLogger('fabric_to_espanso')

class BlockString(str):
    """String subclass for YAML block-style string representation."""
    pass

def repr_block_string(dumper: yaml.Dumper, data: BlockString) -> yaml.ScalarNode:
    """Custom YAML representer for block strings."""
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')

yaml.add_representer(BlockString, repr_block_string)

def generate_yaml_file(client: QdrantClient, yaml_output_folder: str) -> None:
    """Generate a complete YAML file from the Qdrant database.

    Args:
        client: Initialized Qdrant client
        yaml_output_folder: Directory where the YAML file will be created
        
    Raises:
        DatabaseError: If database query fails
        OSError: If file operations fail
        ValueError: If output folder is invalid
    """
    try:
        # Validate output folder
        output_path = Path(yaml_output_folder)
        if not output_path.exists():
            logger.info(f"YAML output path doesn't exist. Check the Espanso matches directory with `espanso path` in PowerShell: {output_path}")
            raise ValueError(f"YAML output path doesn't exist. Check the Espanso matches directory with `espanso path` in PowerShell: {output_path}")
            
        # Query all entries from the database
        try:
            # TODO: make 'collection_name' a parameter
            results = client.scroll(
                collection_name="markdown_files",
                limit=10000  # Adjust based on expected maximum files
            )[0]
        except UnexpectedResponse as e:
            raise DatabaseError(f"Failed to query database: {str(e)}") from e
            
        # Prepare YAML data
        data: Dict[str, List[Dict[str, Any]]] = {'matches': []}
        
        for result in results:
            entry = {
                'trigger': result.payload['trigger'],
                'replace': BlockString(result.payload['content'] + '\n{{clipb}}'),
                'label': result.payload['label'],
                'vars': [
                    {'name': 'clipb', 'type': 'clipboard'}
                ]
            }
            data['matches'].append(entry)
            
        # Write the YAML file
        yaml_output_path = output_path / "fabric_patterns.yml"  
        with open(yaml_output_path, 'w') as yaml_file:
            yaml.dump(data, yaml_file, sort_keys=False, default_flow_style=False)
        
        logger.info(f"YAML file generated successfully at {yaml_output_path}")
    except Exception as e:
        logger.error(f"Error generating YAML file: {str(e)}", exc_info=True)
        if isinstance(e, (DatabaseError, OSError, ValueError)):
            raise
        raise RuntimeError(f"Unexpected error generating YAML: {str(e)}") from e