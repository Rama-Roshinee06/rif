import re

def detect_section(text, headings):
    """
    Detects sections in the validation text based on provided headings.
    
    Args:
        text (str): The text to scan.
        headings (list): A list of section headings to look for.
        
    Returns:
        dict: A dictionary mapping headings to their extracted content.
    """
    sections = {}
    if not text or not headings:
        return sections

    # Simple logic to find headings and extract text between them
    # This is a placeholder logic based on typical efficient section detection
    sorted_headings = sorted(headings, key=len, reverse=True)
    
    # Create a regex pattern to match any of the headings
    pattern = '|'.join(map(re.escape, sorted_headings))
    
    # Split text by headings
    parts = re.split(f'({pattern})', text)
    
    current_heading = None
    for part in parts:
        part = part.strip()
        if part in headings:
            current_heading = part
            sections[current_heading] = ""
        elif current_heading:
            sections[current_heading] += part + " "
            
    return sections
