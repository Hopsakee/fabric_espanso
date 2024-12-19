"""Markdown parsing module for fabric-to-espanso."""
from typing import Tuple, List, Optional, Set
from pathlib import Path
import re
import regex
import logging

from .exceptions import ParsingError
from .config import config

logger = logging.getLogger('fabric_to_espanso')

def create_section_pattern(keywords: Set[str]) -> regex.Pattern:
    keyword_pattern = '|'.join(regex.escape(kw) for kw in keywords)
    return regex.compile(
        rf'^#\s+.*(?:{keyword_pattern}).*$\n?(?:(?!^#).*\n?)*',
        regex.MULTILINE | regex.IGNORECASE
    )

def parse_markdown_file(
    file_path: str | Path,
    keywords: Optional[Set[str]] = None
) -> Tuple[str, Optional[str]]:
    """Extract sections with specified keywords from markdown file.
    
    Args:
        file_path: Path to markdown file
        keywords: Set of keywords to match in headings. If None, uses defaults from config
        
    Returns:
        Tuple of (full_content, extracted_sections)
        If no sections match, returns (full_content, None)
        
    Raises:
        ParsingError: If file reading or parsing fails
    """
    try:
        # Use provided keywords or defaults from config
        keywords = keywords or set(config.base_words)
        
        # Create regex pattern for keywords in headings and text
        section_pattern = create_section_pattern(keywords)
        
        # Read file content
        path = Path(file_path)
        try:
            content = path.read_text(encoding='utf-8')
        except Exception as e:
            raise ParsingError(f"Failed to read {path}: {str(e)}") from e
            
        # Find all matching headings
        section_matches = list(section_pattern.findall(content))
        
        # If no matches found, return full content
        if not section_matches:
            logger.debug(f"No matching sections found in {path.name}")
            return content, None
            
        # Join sections with double newline
        extracted = '\n\n'.join(section_matches)
        logger.debug(f"Extracted {len(section_matches)} sections from {path.name}")
        
        return content, extracted
        
    except Exception as e:
        logger.error(f"Error parsing {file_path}: {str(e)}", exc_info=True)
        if isinstance(e, ParsingError):
            raise
        raise ParsingError(f"Unexpected error parsing {file_path}: {str(e)}") from e

def main():
    # Example usage
    try:
        # Custom keywords can be passed as second argument
        result = parse_markdown_file('document.md')
        # result = extract_sections('document.md', {'Identity', 'Purpose', 'Scope'})
        
        print(result)
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()