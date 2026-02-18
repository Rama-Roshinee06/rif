import glob
import logging
import multiprocessing
import os
import sys
import traceback

from tqdm import tqdm

# Ensure local imports work when running as a script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from excel_writer import save_to_excel
from ocr_engine import convert_pdf_to_images, preprocess_image, run_ocr_on_images
from parser import parse_fir_fields

logger = logging.getLogger(__name__)

INPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "input_pdfs")
OUTPUT_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "output", "FIR_Extracted.xlsx"
)


def process_pdf(pdf_path: str) -> dict:
    """
    Worker function to process a single PDF.

    Pipeline:
        PDF -> images -> preprocess -> OCR -> parse -> result dict
    """
    filename = os.path.basename(pdf_path)
    result = {"Filename": filename, "Status": "FAILED", "Error": ""}

    try:
        logger.info(f"Processing PDF: {filename}")

        # Step 1: Convert PDF -> images
        images = convert_pdf_to_images(pdf_path)
        if not images:
            msg = "No images converted from PDF. Possible corrupt/empty file or Poppler issue."
            logger.error(msg)
            result["Error"] = msg
            return result

        # Step 2: Preprocess each image
        processed_images = [preprocess_image(img) for img in images]

        # Step 3: OCR on images
        text = run_ocr_on_images(processed_images)
        logger.info(f"OCR text length: {len(text)}")

        if not text or not text.strip():
            msg = "OCR returned empty text."
            logger.error(msg)
            result["Error"] = msg
            return result

        # Step 4: Parse FIR fields
        field_data = parse_fir_fields(text)

        # Merge field data into result
        result.update(field_data)
        result["Status"] = "SUCCESS"

    except Exception as e:
        logger.error(f"Unexpected error while processing '{filename}': {e}")
        logger.debug("Stack trace:\n%s", traceback.format_exc())
        result["Error"] = str(e)

    return result


def main() -> None:
    # Basic logging setup; user will see progress and debug information in terminal
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    logger.info("Starting FIR Extraction Pipeline...")
    logger.info(f"Input Directory: {INPUT_DIR}")

    # Get list of PDFs
    pdf_files = glob.glob(os.path.join(INPUT_DIR, "*.pdf"))
    if not pdf_files:
        logger.warning("No PDF files found in 'input_pdfs' folder. Please add files.")
        os.makedirs(INPUT_DIR, exist_ok=True)
        return

    logger.info(f"Found {len(pdf_files)} PDFs. Processing...")

    # CPU Count for multiprocessing (keep conservative for heavy OCR models)
    num_processes = min(multiprocessing.cpu_count(), 4)
    logger.info(f"Using up to {num_processes} worker processes")

    results = []

    # Use multiprocessing with progress bar
    with multiprocessing.Pool(processes=num_processes) as pool:
        for res in tqdm(pool.imap(process_pdf, pdf_files), total=len(pdf_files)):
            results.append(res)

    # Save to Excel
    logger.info("Saving results to Excel...")
    save_to_excel(results, OUTPUT_FILE)
    logger.info("Pipeline completed.")


if __name__ == "__main__":
    multiprocessing.freeze_support()  # Windows requirement
    main()

