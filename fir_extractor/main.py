import os
import glob
import multiprocessing
import traceback
from tqdm import tqdm
from functools import partial

# Import local modules - assuming run from parent directory or package installed
# We will use relative imports assuming this is run as a script from 'fir_extractor' folder or parent
# Ideally, run from project root as 'python fir_extractor/main.py' adds fir_extractor to path if using -m
# OR simpler: append sys.path
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ocr_engine import convert_pdf_to_images, preprocess_image, run_ocr_on_images
from parser import parse_fir_fields
from excel_writer import save_to_excel

INPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'input_pdfs')
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output', 'FIR_Extracted.xlsx')

def process_pdf(pdf_path):
    """
    Worker function to process a single PDF.
    """
    filename = os.path.basename(pdf_path)
    result = {"Filename": filename, "Status": "Success", "Error": ""}
    
    try:
        # Step 1: Convert to Images
        images = convert_pdf_to_images(pdf_path)
        if not images:
            raise ValueError("No images converted from PDF. Corrupt or empty?")
            
        # Step 2: Preprocess
        processed_images = [preprocess_image(img) for img in images]
        
        # Step 3: OCR
        full_text = run_ocr_on_images(processed_images)
        if not full_text:
             raise ValueError("OCR returned empty text.")
             
        # Step 4: Parse
        field_data = parse_fir_fields(full_text)
        
        # Merge field data into result
        result.update(field_data)
        
    except Exception as e:
        result["Status"] = "Failed"
        result["Error"] = str(e)
        # trace = traceback.format_exc() # detailed trace logging if needed
        
    return result

def main():
    print("Starting FIR Extraction Pipeline...")
    print(f"Input Directory: {INPUT_DIR}")
    
    # Get List of PDFs
    pdf_files = glob.glob(os.path.join(INPUT_DIR, "*.pdf"))
    if not pdf_files:
        print("No PDF files found in input_pdfs folder. Please add files.")
        # Ensure directory exists though
        os.makedirs(INPUT_DIR, exist_ok=True)
        return

    print(f"Found {len(pdf_files)} PDFs. Processing...")

    # CPU Count for multiprocessing
    # DocTR uses Deep Learning which might compete for resources if using CPU. 
    # If using GPU, multiprocessing might need care (spawn method).
    # For safety on Windows, we stick to safe concurrent defaults.
    # If 100s of PDFs, parallel is good. BUT heavy models might OOM if too many parallel.
    # Let's be conservative with processes=2 or 4.
    num_processes = min(multiprocessing.cpu_count(), 4) # cap at 4 to avoid OOM

    results = []
    
    # Use multiprocessing
    with multiprocessing.Pool(processes=num_processes) as pool:
        # tqdm for progress bar
        # imap_unordered is good for progress bars
        for res in tqdm(pool.imap(process_pdf, pdf_files), total=len(pdf_files)):
            results.append(res)
            
    # Save to Excel
    print("Saving results...")
    save_to_excel(results, OUTPUT_FILE)
    print("Done!")

if __name__ == "__main__":
    multiprocessing.freeze_support() # Windows requirement
    main()
