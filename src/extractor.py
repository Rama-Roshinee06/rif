import pdfplumber
from pathlib import Path
from src.section_detector import detect_section
from src.fir_fields import extract_fir_fields
def extract_pdf(pdf_path):
    records = []
    seq = 0
    global_fields = {}

    with pdfplumber.open(pdf_path) as pdf:
        for page_no, page in enumerate(pdf.pages, 1):
            text = page.extract_text() or ""
            lines = text.split("\n")

            for line in lines:
                seq += 1
                section = detect_section(line)
                fields = extract_fir_fields(line)
                for k, v in fields.items():
                    if v and not global_fields.get(k):
                        global_fields[k] = v

                records.append({
                    "pdf_name": Path(pdf_path).name,
                    "page_no": page_no,
                    "sequence_no": seq,
                    "section_name": section,
                    "section_text": line.strip(),
                    "fir_no": global_fields.get("fir_no", ""),
                    "date": global_fields.get("date", ""),
                    "police_station": global_fields.get("police_station", ""),
                    "act": global_fields.get("act", ""),
                    "section": global_fields.get("section", "")
                })

    return records
