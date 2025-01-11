import logging
from pathlib import Path
from qdrant_client import QdrantClient

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
        # Clean and format the markdown content
        content = markdown_content.strip()
        # Remove extra newlines and normalize spacing
        content = '\n'.join(line.strip() for line in content.split('\n') if line.strip())
        # Add INPUT section at the end
        content = f"{content}\n\n# INPUT\n{{clipb}}"
        
        return content
    except Exception as e:
        logger.error(f"Error generating YAML for {filename}: {str(e)}", exc_info=True)
        return None

def generate_markdown(filename: str, content: str, purpose: str) -> str:
    """
    Generate markdown content for a database entry.

    Args:
        filename (str): The name of the markdown file (without extension).
        content (str): The system content/instructions.
        purpose (str): The purpose/description of the prompt.

    Returns:
        str: The generated markdown content.
    """
    markdown_template = f"""---
PromptInfo:
  promptId: {filename}
  name: {filename}
  description: {purpose}
  required_values:
  author: fabric
  tags:
  version: 1
config:
  mode: insert
  system: {content}
---

{{{{selection}}}}
"""
    return markdown_template

def generate_markdown_files(client: QdrantClient, collection_name: str, output_folder: str) -> None:
    """Generate markdown files from the Qdrant database.

    Args:
        client: Initialized Qdrant client
        collection_name: Name of the collection to query
        output_folder: Directory where the markdown files will be created
        
    Raises:
        DatabaseError: If database query fails
        OSError: If file operations fail
        ValueError: If output folder is invalid
    """
    try:
        # Validate output folder
        output_path = Path(output_folder)
        if not output_path.exists():
            output_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created markdown output directory: {output_path}")
            
        # Query all entries from the database
        try:
            results = client.scroll(
                collection_name=collection_name,
                limit=10000  # Adjust based on expected maximum files
            )[0]  # scroll returns a tuple (points, next_page_offset)
            
            # Generate markdown files for each entry
            for point in results:
                metadata = point.metadata
                filename = metadata['filename']
                content = metadata['content']
                purpose = metadata['purpose']
                
                # Generate markdown content
                markdown_content = generate_markdown(filename, content, purpose)
                
                # Write to file
                file_path = output_path / f"{filename}.md"
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                    
            logger.info(f"Generated {len(results)} markdown files in {output_path}")
                
        except Exception as e:
            logger.error(f"Error querying database: {e}")
            raise
            
    except Exception as e:
        logger.error(f"Error generating markdown files: {e}")
        raise