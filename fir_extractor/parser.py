import re

def clean_text(text):
    """
    Cleans OCR output by removing garbage characters and normalizing whitespace.
    """
    if not text:
        return ""
    
    # Remove CID font artifacts (e.g., (cid:172))
    text = re.sub(r'\(cid:\d+\)', '', text)
    
    # Normalize whitespace: replace multiple spaces/newlines with single space/appropriate breaks
    # However, sometimes keeping newlines helps with structure. 
    # Let's just remove excessive recurring spaces.
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def parse_fir_fields(text):
    """
    Extracts specific FIR fields from the full OCR text using Regex.
    Returns a dictionary satisfying the user's requested schema.
    """
    
    # Pre-clean the text slightly for consistent regex matching
    cleaned_text = clean_text(text)
    
    data = {
        "Police_Station": "",
        "FIR_Number": "",
        "FIR_Date": "",
        "FIR_Time": "",
        "District": "",
        "Year": "",
        "Acts": "",
        "Sections": "",
        "Occurrence_Date": "",
        "Occurrence_Time": "",
        "GD_Entry_No": "",
        "Info_Type": "",
        "Place_of_Occurrence": "",
        "Direction_Distance_from_PS": "",
        "Address_of_Occurrence": "",
        "Complainant_Name": "",
        "Father_Name": "",
        "DOB": "",
        "Nationality": "",
        "Mobile_Number": "",
        "Present_Address": "",
        "Permanent_Address": "",
        "Accused_Count": "",
        "FIR_Contents": "",
        "Investigating_Officer": "",
        "Rank": ""
    }

    # Define Regex Patterns
    # Note: These are heuristic patterns. Real FIRs vary wildly.
    # We try to be flexible with labels (e.g., 'Police Station', 'P.S.', 'Station')
    # and capture the following text.
    
    patterns = {
        "Police_Station": r"(?:Police\s*Station|P\.S\.|Station)\s*[:\-\.]+\s*([a-zA-Z\s]+?)(?=\s+District|\s+Year|$)",
        "District": r"(?:District)\s*[:\-\.]+\s*([a-zA-Z\s]+?)(?=\s+Police|\s+Year|$)",
        "FIR_Number": r"(?:FIR\s*No|F\.I\.R\s*No)\.?\s*[:\-\.]+\s*([0-9A-Za-z\-/]+)",
        "Year": r"(?:Year)\s*[:\-\.]+\s*(\d{4})",
        "FIR_Date": r"(?:Date\s*of\s*Occurrence|Occurrence\s*Date).*?(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})", # Fallback, often specific field exists
        "Acts": r"(?:Acts)\s*[:\-\.]+\s*(.*?)(?=\s+Sections|\s+Occurrence|$)",
        "Sections": r"(?:Sections)\s*[:\-\.]+\s*(.*?)(?=\s+Occurrence|\s+Date|$)",
        "Complainant_Name": r"(?:Complainant(?:\s*Name)?|Informant(?:\s*Name)?)\s*[:\-\.]+\s*([a-zA-Z\s\.]+)(?=\s+Father|\s+Date|$)",
        "GD_Entry_No": r"(?:G\.D\.?|General\s*Diary)\s*Entry\s*No\.?\s*[:\-\.]+\s*([0-9a-zA-Z\s]+)",
        # Adding more specific patterns logic if simple regex fails
    }
    
    # Generic extraction loop
    for key, pattern in patterns.items():
        match = re.search(pattern, cleaned_text, re.IGNORECASE)
        if match:
            # group(1) usually contains the value
            data[key] = match.group(1).strip()
            
    # Specialized logic for Date/Time if they appear in specific blocks
    # E.g. Date : 22/03/2023
    date_match = re.search(r"Date\s*[:\-\.]+\s*(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})", cleaned_text, re.IGNORECASE)
    if date_match and not data["FIR_Date"]:
        data["FIR_Date"] = date_match.group(1)

    time_match = re.search(r"Time\s*[:\-\.]+\s*(\d{1,2}[:\.]\d{2}\s*(?:hrs|am|pm)?)", cleaned_text, re.IGNORECASE)
    if time_match:
        data["FIR_Time"] = time_match.group(1)
        
    # FIR Contents - simplistic grab of everything after "Contents" header or large block
    # This is often the hardest part. Let's look for "First Information contents"
    content_match = re.search(r"(?:First\s*Information\s*contents|Complaint\s*Details)\s*[:\-\.]+\s*(.*)", cleaned_text, re.IGNORECASE | re.DOTALL)
    if content_match:
        # Take a chunk, maybe limited length to avoid grabbing footer
        data["FIR_Contents"] = content_match.group(1).strip()[:5000] # clamp size

    # Investigating Officer
    io_match = re.search(r"(?:Investigating\s*Officer|I\.O\.|Signature)\s*[:\-\.]+\s*([a-zA-Z\s\.]+)", cleaned_text, re.IGNORECASE)
    if io_match:
        data["Investigating_Officer"] = io_match.group(1).strip()

    return data
