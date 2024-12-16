"""File processing module for fabric-to-espanso."""
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from .markdown_parser import parse_markdown_file
from .exceptions import ProcessingError

logger = logging.getLogger('fabric_to_espanso')

def find_markdown_files(
    root_dir: Path,
    max_depth: int = 1,
    pattern: str = "*.md"
) -> List[Path]:
    """Find markdown files in directory up to specified depth.
    
    Args:
        root_dir: Root directory to search in
        max_depth: Maximum directory depth to search
        pattern: Glob pattern for files to find
        
    Returns:
        List of paths to markdown files
        
    Raises:
        ValueError: If root_dir doesn't exist or isn't a directory
    """
    if not root_dir.exists():
        raise ValueError(f"Directory does not exist: {root_dir}")
    if not root_dir.is_dir():
        raise ValueError(f"Path is not a directory: {root_dir}")
        
    files: List[Path] = []
    
    try:
        # Convert depth to parts for comparison
        root_parts = len(root_dir.parts)
        
        # Use rglob to find all markdown files
        for file_path in root_dir.rglob(pattern):
            # Skip if too deep
            if len(file_path.parts) - root_parts > max_depth:
                continue
            if file_path.is_file():
                files.append(file_path)
                
        logger.debug(f"Found {len(files)} markdown files in {root_dir}")
        return files
        
    except Exception as e:
        logger.error(f"Error finding markdown files: {str(e)}", exc_info=True)
        raise ProcessingError(f"Failed to find markdown files: {str(e)}") from e

def process_markdown_file(
    file_path: Path,
    trigger_prefix: str = "/:"
) -> Optional[Dict[str, Any]]:
    """Process a single markdown file.
    
    Args:
        file_path: Path to markdown file
        trigger_prefix: Prefix for espanso triggers
        
    Returns:
        Dictionary with file information or None if processing fails
        
    Raises:
        ProcessingError: If file processing fails
    """
    try:
        content, extracted_sections = parse_markdown_file(str(file_path))
        if extracted_sections is None:
            logger.warning(f"No sections extracted from {file_path}")
            return None
            
        return {
            'filename': file_path.name,
            'content': content,
            'purpose': extracted_sections,
            'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime),
            'trigger': trigger_prefix,
            'label': file_path.stem  # filename without extension
        }
        
    except Exception as e:
        logger.error(f"Error processing {file_path}: {str(e)}", exc_info=True)
        raise ProcessingError(f"Failed to process {file_path}: {str(e)}") from e

def process_markdown_files(
    markdown_folder: Path | str,
    max_depth: int = 1,
    trigger_prefix: str = "/:"
) -> List[Dict[str, Any]]:
    """Process all markdown files in directory.
    
    Args:
        markdown_folder: Directory containing markdown files
        max_depth: Maximum directory depth to search
        trigger_prefix: Prefix for espanso triggers
        
    Returns:
        List of processed file information
        
    Raises:
        ProcessingError: If processing fails
        ValueError: If markdown_folder is invalid
    """
    root_dir = Path(markdown_folder)
    processed_files: List[Dict[str, Any]] = []
    
    try:
        # Find all markdown files
        markdown_files = find_markdown_files(root_dir, max_depth)
        
        # Process each file
        for file_path in markdown_files:
            try:
                if result := process_markdown_file(file_path, trigger_prefix):
                    processed_files.append(result)
                    logger.info(f"Processed: {file_path.name}")
            except ProcessingError as e:
                logger.error(str(e))
                continue
                
        logger.info(f"Successfully processed {len(processed_files)} files")
        return processed_files
        
    except Exception as e:
        logger.error(f"Error processing markdown files: {str(e)}", exc_info=True)
        if isinstance(e, (ProcessingError, ValueError)):
            raise
        raise ProcessingError(f"Unexpected error processing files: {str(e)}") from e