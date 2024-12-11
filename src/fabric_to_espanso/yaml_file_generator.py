import yaml
from qdrant_client import QdrantClient
import logging
from parameters import YAML_OUTPUT_FOLDER

logger = logging.getLogger('fabric_to_espanso')

class BlockString(str): pass

def repr_block_string(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')

yaml.add_representer(BlockString, repr_block_string)

def generate_yaml_file(client: QdrantClient, yaml_file_path: str = YAML_OUTPUT_FOLDER):
    """
    Generate a complete YAML file from the Qdrant database.

    Args:
        client (QdrantClient): An initialized Qdrant client.
    """
    try:
        # Query all entries from the database
        results = client.scroll(
            collection_name="markdown_files",
            limit=10000  # Adjust based on your expected maximum number of files
        )[0]
        
        data = {'matches': []}

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
        yaml_output_path = f"{yaml_file_path}/fabric_patterns.yml"  
        with open(yaml_output_path, 'w') as yaml_file:
            yaml.dump(data, yaml_file, sort_keys=False, default_flow_style=False)

        logger.info(f"YAML file generated successfully at {yaml_output_path}")
    except Exception as e:
        logger.error(f"Error generating YAML file: {str(e)}", exc_info=True)