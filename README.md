# FIR PDF Processing Pipeline 📄➡️📊

A production-ready Python application that processes scanned/digital FIR (First Information Report) PDFs using DocTR OCR, automatically detects section headings, and exports structured data to Excel.

## 🎯 Features

✅ **DocTR OCR Extraction** - Reads text from scanned and digital PDFs  
✅ **Section Detection** - Automatically identifies FIR headings (Police Station, Accused, etc.)  
✅ **Structured Output** - Creates Excel with one column per FIR heading  
✅ **Batch Processing** - Process multiple PDFs in one run  
✅ **Error Handling** - Graceful fallback to pdfplumber if OCR fails  
✅ **Beginner Friendly** - Well-commented code with clear logging  

## 📁 Project Structure

```
bulk_fir/
├── main.py                    # Main pipeline orchestrator
├── fir_processor.py           # OCR extraction & heading detection
├── utils.py                   # Helper functions & utilities
├── requirements.txt           # Python dependencies
├── input_pdfs/                # Place FIR PDFs here
├── output/                    # Excel files saved here
└── README.md                  # This file
```

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Add Your PDFs

Copy your FIR PDF files to `input_pdfs/` folder:
```
input_pdfs/
├── fir_001.pdf
├── fir_002.pdf
└── fir_003.pdf
```

### Step 3: Run the Pipeline

```bash
python main.py
```

That's it! Your Excel file will be created in `output/fir_extracted.xlsx`

---

## 📋 Advanced Usage

### Use Faster Fallback Method (for Digital PDFs)

If DocTR is too slow or you only have digital PDFs (not scanned images):

```bash
python main.py --fallback
```

### Specify Custom Input/Output Folders

```bash
python main.py --input ./your_pdfs --output ./your_output
```

### Save JSON Backup

```bash
python main.py --backup-json
```

### Combined Example

```bash
python main.py --input ./pdfs --output ./results --fallback --backup-json
```

---

## 📊 Output Format

The generated Excel file (`fir_extracted.xlsx`) contains one row per PDF with these columns:

### Metadata Columns
- `pdf_name` - Original PDF filename
- `pages` - Number of pages extracted
- `total_lines` - Total text lines recognized
- `extraction_status` - SUCCESS or ERROR

### FIR Section Columns (Auto-detected)
- `District` - District name
- `Police Station` - Police station name
- `FIR No` / `FIR Number` - Case number
- `FIR Date` - Date filed
- `Complainant Name` - Person making complaint
- `Complainant Rank_Number` - Officer rank (if applicable)
- `Accused` - Accused person details
- `Accused Age_DOB` - Age and date of birth
- `Father Name` - Father's name
- `Address` - Address details
- `Phone Number` - Contact information
- `Occurrence Date` - When incident occurred
- `Place of Occurrence` - Location of incident
- `Act` - Applicable law
- `Section` - Legal section
- `Investigation Officer` - Officer conducting investigation
- ... and more

---

## 🔧 How It Works

### Pipeline Flow

```
1. Load OCR Model (DocTR)
   ↓
2. Read PDF Files
   ↓
3. Extract Text Using OCR
   ↓
4. Clean & Split into Lines
   ↓
5. Detect FIR Section Headings
   ↓
6. Group Text Under Headings
   ↓
7. Create DataFrame
   ↓
8. Save to Excel with Formatting
   ↓
9. Done! ✓
```

### Key Functions

**`fir_processor.py`**
- `load_ocr_model()` - Initialize DocTR model
- `extract_text_from_pdf()` - Extract text using OCR
- `group_lines_by_headings()` - Group lines by FIR section
- `process_single_pdf()` - Process one PDF file
- `process_all_pdfs()` - Batch process PDFs

**`utils.py`**
- `FIR_HEADINGS` - List of 30+ expected FIR field names
- `detect_heading()` - Identify if text is a heading
- `clean_text()` - Remove extra whitespace
- `get_pdf_files()` - List PDFs in folder
- `log_progress()` - Pretty console logging

**`main.py`**
- `main()` - Orchestrate the entire pipeline
- `save_to_excel()` - Export DataFrame to Excel with formatting

---

## 🛠️ Configuration

### Modify FIR Headings

Edit `FIR_HEADINGS` list in `utils.py` to add/remove expected section names:

```python
FIR_HEADINGS = [
    "Police Station",
    "FIR No",
    "Your Custom Heading",
    # ... more headings
]
```

### Change OCR Model

In `fir_processor.py`, modify `load_ocr_model()`:

```python
# Default: uses 'pretrained=True' (best accuracy)
_ocr_model = ocr_predictor(pretrained=True)

# For faster processing with less accuracy:
_ocr_model = ocr_predictor(pretrained=False)
```

---

## 📖 Usage Examples

### Example 1: Process Single Folder

```bash
# Process all PDFs in input_pdfs/ → output/fir_extracted.xlsx
python main.py
```

### Example 2: Process Custom Folders

```bash
# Read from ./my_firs/, save to ./my_output/
python main.py --input ./my_firs --output ./my_output
```

### Example 3: Faster Processing (Digital PDFs Only)

```bash
# Skip OCR, use simple PDF text extraction
python main.py --fallback
```

### Example 4: With Backup

```bash
# Save both Excel and JSON backup
python main.py --backup-json
```

---

## ⚠️ Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'doctr'"

**Solution:** Install DocTR
```bash
pip install python-doctr
pip install torch torchvision  # Might be needed on Windows
```

### Issue: Slow Processing on First Run

**Reason:** DocTR model is being downloaded (~500MB) and loaded to GPU  
**Solution:** Wait 2-3 minutes, or use fallback: `python main.py --fallback`

### Issue: Empty Excel Output

**Cause:** PDFs might be scanned images with text not recognized  
**Solution:** 
1. Check `extraction_status` column - if ERROR, review error logs
2. Try using fallback: `python main.py --fallback`
3. Ensure PDFs are readable and not corrupted

### Issue: Only Getting Page 1 Text

**Cause:** OCR terminated early or PDF has mixed digital/scanned pages  
**Solution:** Check logs for errors, try fallback method

---

## 💡 Tips & Best Practices

✅ **For Scanned FIRs:** Use default `python main.py` (uses DocTR OCR)  
✅ **For Digital PDFs:** Use `python main.py --fallback` (faster)  
✅ **First Time:** Run on 1-2 test PDFs to verify output format  
✅ **Large Batches:** Process 50-100 PDFs at a time  
✅ **GPU Processing:** DocTR automatically uses GPU if available (faster)  
✅ **Monitor Memory:** Large batches may require 8GB+ RAM  

---

## 📝 Input Requirements

### PDF Format
- ✓ Scanned FIR documents (images)
- ✓ Digital PDFs with embedded text
- ✓ Mixed format PDFs
- ✓ Multi-page documents (any number of pages)

### File Size
- Recommended: 100KB - 50MB per file
- Maximum tested: 100+ page PDFs

### Naming
- Use descriptive names: `fir_2024_001.pdf`
- Avoid special characters in filename

---

## 🔍 Output Inspection

### View Generated Excel
1. Open `output/fir_extracted.xlsx` in Excel/LibreOffice
2. First row is frozen for easy scrolling
3. Column widths auto-adjusted
4. Each row represents one FIR PDF

### Inspect Processing Logs
Console output shows:
- How many PDFs found
- OCR model loading status
- Extraction progress `[1/10]`, `[2/10]`, etc.
- Any errors or warnings
- Final summary with file path

### Debug with JSON

If something goes wrong, save JSON backup:
```bash
python main.py --backup-json
```

Opens `output/fir_extracted_backup.json` with raw extracted data for inspection.

---

## 🧪 Testing Your Setup

### Quick Test: 1 PDF
1. Place one test PDF in `input_pdfs/`
2. Run: `python main.py`
3. Check `output/fir_extracted.xlsx` - should have 1 row
4. Verify columns are populated

### Test Fallback
```bash
python main.py --fallback
```
Should complete in 10-30 seconds without OCR.

### Test Custom Folder
```bash
python main.py --input input_pdfs --output output
```

---

## 📦 Dependencies & Versions

| Package | Version | Purpose |
|---------|---------|---------|
| python-doctr | 0.7.0 | OCR extraction |
| pdf2image | 1.16.3 | PDF to image conversion |
| pandas | 2.0.3 | Data processing |
| openpyxl | 3.1.2 | Excel export |
| Pillow | 10.0.0 | Image handling |
| numpy | 1.24.3 | Numerical operations |
| pdfplumber | 0.9.0 | Fallback PDF reading |

---

## 🎓 Code Structure for Beginners

### main.py
- Entry point of the program
- Calls other functions in order
- Good place to understand the flow

### fir_processor.py
- Most complex file
- Contains OCR logic and heading detection
- Safe to modify heading list

### utils.py
- Simple helper functions
- Update `FIR_HEADINGS` here to recognize new sections
- Modify `FIR_HEADINGS` list (lines 12-50)

---

## 🚨 Error Handling

The pipeline has multiple safety features:

1. **Missing PDFs** → Skip and log warning
2. **OCR Fails** → Automatically fallback to pdfplumber
3. **Empty Text** → Create row with empty fields
4. **Excel Write Error** → Detailed error message
5. **Corrupted PDF** → Log error and continue with next file

All errors are logged with helpful messages pointing to the issue.

---

## 📞 Support Tips

**If something breaks:**
1. Check console output for error messages
2. Try: `python main.py --fallback` first
3. Verify PDFs are not corrupted: Try opening in Adobe Reader
4. Check Python version: `python --version` (requires 3.8+)
5. Verify all files are in correct folders

**Debug Mode:**
```python
# Add to main.py for debugging:
from fir_processor import extract_and_inspect_sample
extract_and_inspect_sample("input_pdfs/test.pdf", max_lines=30)
```

---

## 🎉 What's Next?

✅ Generated Excel - ready for analysis  
✅ Import into database or CRM  
✅ Create dashboards with Power BI/Tableau  
✅ Build custom reporting  
✅ Train ML models on FIR data  

---

## 📄 License

Open source - feel free to modify and distribute.

---

**Happy PDF Processing! 🚀**

For questions or issues, check the error messages in the console - they're designed to be helpful!

Last Updated: February 6, 2026
