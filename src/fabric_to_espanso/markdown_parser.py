"""Markdown parsing module for fabric-to-espanso."""
from typing import Tuple, List, Optional, Set
from pathlib import Path
import re
import logging

from .exceptions import ParsingError
from .config import config

logger = logging.getLogger('fabric_to_espanso')

def create_heading_pattern(keywords: Set[str]) -> re.Pattern:
    """Create regex pattern for matching markdown headings with keywords.
    
    Args:
        keywords: Set of keywords to match in headings
        
    Returns:
        Compiled regex pattern
    """
    # Escape special characters and join with OR
    keyword_pattern = '|'.join(re.escape(kw) for kw in keywords)
    # Match any level heading with our keywords
    return re.compile(
        rf'^(#+)\s*(?:{keyword_pattern}).*$',
        re.MULTILINE | re.IGNORECASE
    )

def find_section_boundaries(
    content: str,
    heading_matches: List[re.Match]
) -> List[Tuple[int, int]]:
    """Find start and end positions of markdown sections.
    
    Args:
        content: Full markdown content
        heading_matches: List of regex matches for headings
        
    Returns:
        List of (start, end) positions for each section
    """
    boundaries = []
    for i, match in enumerate(heading_matches):
        start = match.start()
        # If this is the last heading, section ends at EOF
        if i + 1 < len(heading_matches):
            end = heading_matches[i + 1].start()
        else:
            end = len(content)
        boundaries.append((start, end))
    return boundaries

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
        
        # Create regex pattern for headings
        heading_pattern = create_heading_pattern(keywords)
        
        # Read file content
        path = Path(file_path)
        try:
            content = path.read_text(encoding='utf-8')
        except Exception as e:
            raise ParsingError(f"Failed to read {path}: {str(e)}") from e
            
        # Find all matching headings
        heading_matches = list(heading_pattern.finditer(content))
        
        # If no matches found, return full content
        if not heading_matches:
            logger.debug(f"No matching sections found in {path.name}")
            return content, None
            
        # Get section boundaries
        boundaries = find_section_boundaries(content, heading_matches)
        
        # Extract unique sections
        sections: Set[str] = set()
        for start, end in boundaries:
            section = content[start:end].strip()
            if section:  # Skip empty sections
                sections.add(section)
                
        if not sections:
            logger.debug(f"No non-empty sections found in {path.name}")
            return content, None
            
        # Join sections with double newline
        extracted = '\n\n'.join(sorted(sections))
        logger.debug(f"Extracted {len(sections)} sections from {path.name}")
        
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