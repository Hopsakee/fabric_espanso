import os
from datetime import datetime
from parameters import MARKDOWN_FOLDER
import logging

logger = logging.getLogger('fabric_to_espanso')

def process_markdown_files():
    """
    Process all markdown files in the specified folder and its first-level subfolders.

    Returns:
        list: A list of dictionaries containing information about each markdown file.
    """
    markdown_files = []

    try:
        for root, dirs, files in os.walk(MARKDOWN_FOLDER):
            # Limit to first-level subfolders
            if root != MARKDOWN_FOLDER and os.path.dirname(root) != MARKDOWN_FOLDER:
                continue

            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        last_modified = datetime.fromtimestamp(os.path.getmtime(file_path))

                        markdown_files.append({
                            'filename': file,
                            'content': content,
                            'last_modified': last_modified
                        })

                        logger.info(f"Processed file: {file}")
                    except Exception as e:
                        logger.error(f"Error processing file {file}: {str(e)}", exc_info=True)

        logger.info(f"Total markdown files processed: {len(markdown_files)}")
        return markdown_files
    except Exception as e:
        logger.error(f"Error walking through markdown folder: {str(e)}", exc_info=True)
        return []