import yaml
from qdrant_client import QdrantClient
import logging
from parameters import YAML_OUTPUT_FOLDER

logger = logging.getLogger('fabric_to_espanso')

def generate_yaml_file(client: QdrantClient):
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

        yaml_content = "matches:\n"

        for result in results:
            yaml_entry = f"""
              - trigger: {result.payload['trigger']}
                replace: >
                  {result.payload['espanso_yaml']}
                label: {result.payload['label']}
                vars:
                    - name: "clipb"
                      type: "clipboard"
            """
            yaml_content += yaml_entry

        # Write the YAML file
        yaml_output_path = f"{YAML_OUTPUT_FOLDER}/fabric_patterns.yml"  
        with open(yaml_output_path, 'w') as yaml_file:
            yaml_file.write(yaml_content)

        logger.info(f"YAML file generated successfully at {yaml_output_path}")
    except Exception as e:
        logger.error(f"Error generating YAML file: {str(e)}", exc_info=True)