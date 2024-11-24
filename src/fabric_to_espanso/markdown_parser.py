import logging

logger = logging.getLogger('fabric_to_espanso')

import re
import itertools

def generate_heading_combinations(base_words):
    """
    Dynamically generate all possible heading combinations.
    
    Args:
        base_words (list): List of base words to combine
    
    Returns:
        list: All possible heading combinations, case-insensitive
    """
    # Generate all possible combination lengths
    combinations = []
    for r in range(1, len(base_words) + 1):
        # Create combinations of r length
        word_combos = list(itertools.combinations(base_words, r))
        
        # Convert combinations to human-readable headings
        heading_combos = [
            ' and '.join(combo).lower() 
            for combo in word_combos
        ]
        combinations.extend(heading_combos)
    
    return combinations
    
def parse_markdown_file(markdown_file_path, base_words=None):
    """
    Dynamically extract sections based on flexible heading combinations.
    
    Args:
        markdown_file_path (str): Path to the markdown file
        base_words (list, optional): Words to generate headings from
    
    Returns:
        dict: Extracted sections with their contents
    """
    try:
        # Default base words if not provided
        if base_words is None:
            base_words = ['Identity', 'Purpose', 'Task', 'Goal']
        
        # Generate all possible heading combinations
        VALID_HEADINGS = generate_heading_combinations(base_words)
        
        # Read file content
        with open(markdown_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        extracted_sections = ""
        
        for heading in VALID_HEADINGS:
            # Escape any potential regex special characters in the heading
            escaped_heading = re.escape(heading)
            
            # Flexible regex pattern to match headings
            pattern = rf'^#+\s*{escaped_heading}\s*$'
            
            # Find all matches (allows multiple sections with same heading type)
            matches = list(re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE))
            
            for i, match in enumerate(matches):
                start_index = match.start()
                
                # Find next heading or end of file
                next_heading_match = re.search(
                    r'^#+\s*[^\n]+', 
                    content[start_index+1:], 
                    re.MULTILINE
                )
                
                if next_heading_match:
                    # Extract content between current and next heading
                    end_index = start_index + next_heading_match.start() + 1
                    section_content = content[start_index:end_index].strip()
                else:
                    # If no next heading, take till end of file
                    section_content = content[start_index:].strip()
                
                # Add extracted section to string of already extracted sections.
                extracted_sections += f"{extracted_sections}\n\n{section_content}\n\n"
        
        return content, extracted_sections
    
    except Exception as e:
        logger.error(f"Error parsing markdown file {markdown_file_path}: {str(e)}", exc_info=True)
        return None

def main():
    # Example usage with default base words
    try:
        sections = parse_markdown_file('document.md')
        
        # Optional: Add custom base words
        # sections = extract_sections('document.md', ['Identity', 'Purpose', 'Context', 'Goal'])
        
        for heading, content in sections.items():
            print(f"--- {heading.upper()} ---")
            print(content)
            print("\n")
    
    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()