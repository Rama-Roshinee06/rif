import re


def clean_text(text: str) -> str:
    if not text:
        return ""

    # Remove CID artifacts
    text = re.sub(r"\(cid:\d+\)", "", text)

    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # Fix hyphenated line breaks (word-
    text = re.sub(r"-\n", "", text)

    # Remove spurious multiple newlines but keep paragraph breaks
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Trim trailing/leading whitespace on each line
    lines = [ln.strip() for ln in text.splitlines()]
    # Remove empty lines at top/bottom
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()

    return "\n".join(lines)


def parse_fir_fields(text: str) -> dict:
    txt = clean_text(text)

    fields = {
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

    # Helpful small helpers
    def first_search(patterns, text=txt):
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE | re.MULTILINE)
            if m:
                return m
        return None

    # FIR number (many formats)
    m = first_search([
        r"F\s*I\s*R\s*[#:]*\s*No\.?\s*[:\-\s]*([A-Za-z0-9\-/]+)",
        r"FIR\s*No\.?\s*[:\-\s]*([A-Za-z0-9\-/]+)",
        r"F\.I\.R\.\s*No\.?\s*[:\-\s]*([A-Za-z0-9\-/]+)",
        r"^No\.\s*[:\-\s]*([A-Za-z0-9\-/]+)"
    ])
    if m:
        fields["FIR_Number"] = m.group(1).strip()

    # Dates (DD/MM/YYYY or DD-MM-YYYY or YYYY-MM-DD)
    date_m = re.search(r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", txt)
    if date_m:
        fields["FIR_Date"] = date_m.group(1)

    # Time
    time_m = re.search(r"(\d{1,2}[:\.]\d{2}(?:\s?(?:AM|PM|am|pm|hrs)?)?)", txt)
    if time_m:
        fields["FIR_Time"] = time_m.group(1)

    # Police Station
    ps_m = first_search([
        r"(?:Police\s*Station|P\.?S\.?|Station)\s*[:\-\s]+([A-Za-z0-9\s\-/&.,]+)",
        r"^Station\s*[:\-\s]+([A-Za-z0-9\s\-/&.,]+)"
    ])
    if ps_m:
        fields["Police_Station"] = ps_m.group(1).strip()

    # District
    dist_m = re.search(r"District\s*[:\-\s]+([A-Za-z\s]+)", txt, re.IGNORECASE)
    if dist_m:
        fields["District"] = dist_m.group(1).strip()

    # Year
    yr_m = re.search(r"\b(20\d{2}|19\d{2})\b", txt)
    if yr_m:
        fields["Year"] = yr_m.group(1)

    # GD Entry No
    gd_m = first_search([
        r"G\.?D\.?\s*Entry\s*No\.?\s*[:\-\s]*([A-Za-z0-9\-/]+)",
        r"GD\s*No\.?\s*[:\-\s]*([A-Za-z0-9\-/]+)"
    ])
    if gd_m:
        fields["GD_Entry_No"] = gd_m.group(1).strip()

    # Mobile number (India) - simple patterns
    mob_m = re.search(r"(\+?91[\-\s]?\d{10}|\b\d{10}\b)", txt)
    if mob_m:
        fields["Mobile_Number"] = mob_m.group(1)

    # Sections and Acts
    acts_m = re.search(r"Acts?\s*[:\-\s]+([A-Za-z0-9,\s/&-]+)", txt, re.IGNORECASE)
    if acts_m:
        fields["Acts"] = acts_m.group(1).strip()

    secs_m = re.search(r"Sections?\s*[:\-\s]+([A-Za-z0-9,\s/\-]+)", txt, re.IGNORECASE)
    if secs_m:
        fields["Sections"] = secs_m.group(1).strip()

    # Complainant and Father
    comp_m = first_search([
        r"Complainant\s*(?:Name)?\s*[:\-\s]+([A-Za-z\s.]+)",
        r"Informant\s*(?:Name)?\s*[:\-\s]+([A-Za-z\s.]+)"
    ])
    if comp_m:
        fields["Complainant_Name"] = comp_m.group(1).strip()

    father_m = re.search(r"Father(?:'s)?\s*Name\s*[:\-\s]+([A-Za-z\s.]+)", txt, re.IGNORECASE)
    if father_m:
        fields["Father_Name"] = father_m.group(1).strip()

    # Addresses - look for keywords
    present_m = re.search(r"Present\s+Address\s*[:\-\s]+(.{10,300})", txt, re.IGNORECASE | re.DOTALL)
    if present_m:
        fields["Present_Address"] = present_m.group(1).split('\n')[0].strip()

    perm_m = re.search(r"Permanent\s+Address\s*[:\-\s]+(.{10,300})", txt, re.IGNORECASE | re.DOTALL)
    if perm_m:
        fields["Permanent_Address"] = perm_m.group(1).split('\n')[0].strip()

    # Place of occurrence
    place_m = re.search(r"Place\s+of\s+Occurrence\s*[:\-\s]+(.{5,200})", txt, re.IGNORECASE | re.DOTALL)
    if place_m:
        fields["Place_of_Occurrence"] = place_m.group(1).split('\n')[0].strip()

    # FIR Contents - try to capture block after 'Details' or 'Complaint'
    contents_m = first_search([
        r"Complaint\s*Details\s*[:\-\s]+(.{20,4000})$",
        r"Complaint\s*[:\-\s]+(.{20,4000})$",
        r"Details\s*[:\-\s]+(.{20,4000})$",
        r"First\s*Information\s*Report\s*[:\-\s]+(.{20,4000})$"
    ],)
    if contents_m:
        fields["FIR_Contents"] = contents_m.group(1).strip()[:5000]
    else:
        # fallback: take a long chunk from the middle of document as contents
        lines = txt.splitlines()
        if len(lines) > 10:
            mid = "\n".join(lines[3: min(30, len(lines))])
            fields["FIR_Contents"] = mid[:5000]

    # Investigating officer & rank
    io_m = re.search(r"Investigating\s+Officer\s*[:\-\s]+([A-Za-z\s.]+)", txt, re.IGNORECASE)
    if io_m:
        fields["Investigating_Officer"] = io_m.group(1).strip()

    rank_m = re.search(r"(SI|ASI|Inspector|Sub\-Inspector|Sub Inspector|Constable)\b", txt, re.IGNORECASE)
    if rank_m:
        fields["Rank"] = rank_m.group(1)

    # Direction/Distance from PS (heuristic)
    dd_m = re.search(r"(km|m)\s*(?:from|from the)\s*(?:PS|police station)\b(.{0,80})", txt, re.IGNORECASE)
    if dd_m:
        fields["Direction_Distance_from_PS"] = dd_m.group(0)

    # Accused count heuristic
    ac_m = re.search(r"(\d+)\s+accused", txt, re.IGNORECASE)
    if ac_m:
        fields["Accused_Count"] = ac_m.group(1)

    return fields
