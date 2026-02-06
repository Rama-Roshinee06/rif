from src.section_detector import detect_section

# Define standard FIR fields
FIR_FIELDS = [
    "District",
    "Police Station",
    "FIR No",
    "Date",
    "Sections",
    "Complainant",
    "Accused",
    # Add other fields as necessary
]

def extract_fir_data(text):
    """
    Extracts FIR data using the detect_section utility.
    """
    return detect_section(text, FIR_FIELDS)
