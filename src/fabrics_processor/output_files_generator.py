"""YAML file generation for fabric-to-espanso and
markdown file generation for Obsidian TextGenerator plugin."""
from pathlib import Path
from shutil import rmtree
from typing import Dict, Any, List
import yaml
import logging

from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from src.fabrics_processor.config import config

from .exceptions import DatabaseError

logger = logging.getLogger('fabric_to_espanso')

class BlockString(str):
    """String subclass for YAML block-style string representation."""
    pass

def repr_block_string(dumper: yaml.Dumper, data: BlockString) -> yaml.ScalarNode:
    """Custom YAML representer for block strings."""
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')

yaml.add_representer(BlockString, repr_block_string)

def generate_yaml_file(client: QdrantClient, collection_name: str, yaml_output_folder: str) -> None:
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
            results = client.scroll(
                collection_name=collection_name,
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
                'label': result.payload['filename'],
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

def generate_markdown_files(client: QdrantClient, collection_name: str, markdown_output_folder: str) -> None:
    """Generate markdown files from the Qdrant database.

    Args:
        client: Initialized Qdrant client
        collection_name: Name of the collection to query
        markdown_output_folder: Directory where the markdown files will be created
        
    Raises:
        DatabaseError: If database query fails
        OSError: If file operations fail
        ValueError: If output folder is invalid
    """
    try:
        # Validate output folder
        output_path = Path(markdown_output_folder)
        if not output_path.exists():
            logger.info(f"Markdown output path doesn't exist. Check if this folder in parameters.py matches the Textgenerator folder in you Obsidian vault. {output_path}")
            raise ValueError(f"Markdown output path doesn't exist. Check if this folder in parameters.py matches the Textgenerator folder in you Obsidian vault. {output_path}")
            
        # Query all entries from the database
        try:
            # Simply first remove all existing markdown files in Obisdian Textgenerator folder
            rmtree(output_path)
            output_path.mkdir(mode=0o755)

            results = client.scroll(
                collection_name=collection_name,
                limit=10000  # Adjust based on expected maximum files
            )[0]

            # Generate markdown files for each entry
            for result in results:
                metadata = result.payload
                filename = metadata['filename']
                purpose = metadata['purpose']
                content = metadata['content']
                markdown_path = output_path / f"{filename}.md"
                with open(markdown_path, 'w', encoding='utf-8') as markdown_file:
                    markdown_file.write(apply_markdown_template(filename, purpose, content))
            
            logger.info(f"Generated {len(results)} Markdown files generated successfully at {markdown_output_folder}")

        except UnexpectedResponse as e:
            raise DatabaseError(f"Failed to query database: {str(e)}") from e
            
    except Exception as e:
        logger.error(f"Error generating Markdown files: {str(e)}")


def apply_markdown_template(filename: str, purpose: str, content: str) -> str:
    """Apply the markdown template to the given content.
    To generate markdown files that can be used in Obsidian by
    the TextGenerator plugin."""

    # Ensure proper indentation
    purpose_indented = purpose.replace('\n', '\n    ')
    content_indented = content.replace('\n', '\n    ')
    
    return f"""---
PromptInfo:
  promptId: {filename}
  name: {filename}
  description: |
    {purpose_indented}
  required_values:
  author: fabric
  tags:
  version: 1
config:
  mode: insert
  system: |
    {content_indented}
---

{{{{selection}}}}
"""