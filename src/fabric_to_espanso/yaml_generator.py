import yaml
import logging

logger = logging.getLogger('fabric_to_espanso')

def generate_yaml(markdown_content, filename, trigger="/:", label=None):
    """
    Generate YAML content from parsed markdown.

    Args:
        markdown_content (str): The content of the markdown file.
        filename (str): The name of the markdown file (without extension).
        trigger (str, optional): The trigger for the YAML entry. Defaults to "/:".
        label (str, optional): The label for the YAML entry. If None, uses the filename.

    Returns:
        str: The generated YAML content.
    """
    try:
        yaml_content = {
            "trigger": trigger,
            "replace": f">\n{markdown_content.strip()}\n\n{{{{clipb}}}}",
            "label": label if label else filename,
            "vars": [
                {
                    "name": "clipb",
                    "type": "clipboard"
                }
            ]
        }

        return yaml.dump([yaml_content], default_flow_style=False)
    except Exception as e:
        logger.error(f"Error generating YAML for {filename}: {str(e)}", exc_info=True)
        return None