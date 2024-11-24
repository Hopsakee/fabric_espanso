import logging

logger = logging.getLogger('fabric_to_espanso')

import re

def parse_markdown_file(markdown_file_path, keywords=None):
    """
    Extract sections with specified keywords from markdown file.
    
    Args:
        markdown_file_path (str): Path to the markdown file
        keywords (list, optional): List of keywords to match in headings
    
    Returns:
        str: Extracted sections or full file content
    """
    # Default keywords if not provided
    if keywords is None:
        keywords = ['Identity', 'Purpose', 'Goal', 'Goals', 'Task', 'Tasks']
    
    # Prepare case-insensitive regex pattern for keywords
    keyword_pattern = r'|'.join(re.escape(kw) for kw in keywords)
    
    # Read file content
    try:
        with open(markdown_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        print(f"File not found: {markdown_file_path}")
        return ""
    
    # Find all headings in the document
    heading_matches = list(re.finditer(r'^#+\s*.*$', content, re.MULTILINE))
    
    # If no headings or no keyword matches, return full content
    if not heading_matches or not re.search(keyword_pattern, content, re.IGNORECASE):
        return content, content
    
    # Extract sections
    extracted_sections = [] # To prevent shuffling of the extracted sections
    extracted_content = set()  # To prevent duplicate text
    
    for i, match in enumerate(heading_matches):
        # Check if current heading matches keywords
        if re.search(keyword_pattern, match.group(0), re.IGNORECASE):
            # Determine the start of this section
            start = match.start()
            
            # Find the start of the next section or end of file
            if i + 1 < len(heading_matches):
                end = heading_matches[i+1].start()
                section = content[start:end].strip()
            else:
                # Last section
                section = content[start:].strip()
            
            # Prevent duplicate content
            if section not in extracted_content:
                extracted_sections.append(section)
                extracted_content.add(section)
    
    extracted_content_str = '\n\n'.join(extracted_sections)
    
    # Join extracted sections
    return content, extracted_content_str

def main():
    # Example usage
    try:
        # Custom keywords can be passed as second argument
        result = parse_markdown_file('document.md')
        # result = extract_sections('document.md', ['Identity', 'Purpose', 'Scope'])
        
        print(result)
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()    