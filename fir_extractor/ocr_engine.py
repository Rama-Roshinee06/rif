import glob
import logging
import os
import threading
from typing import List

import cv2
import numpy as np
from pdf2image import convert_from_path

logger = logging.getLogger(__name__)

_rapid_ocr_instance = None
_rapid_ocr_lock = threading.Lock()


def _find_poppler_path() -> str | None:
    """
    Try to locate a local Poppler installation under:
        fir_extractor/poppler/**/bin

    Returns the path to the bin folder if found, else None.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pattern = os.path.join(base_dir, "poppler", "**", "bin")

    for candidate in glob.glob(pattern, recursive=True):
        if os.path.isdir(candidate):
            return candidate

    return None


def convert_pdf_to_images(pdf_path: str, dpi: int = 300) -> List[np.ndarray]:
    """
    Convert a PDF into a list of numpy arrays (images) at the given DPI.

    Uses pdf2image with optional Poppler path detection on Windows:
    - First tries to locate Poppler under fir_extractor/poppler/**/bin
    - If not found, assumes Poppler is available on the system PATH
    - Never raises on Poppler issues; logs a clear error and returns []
    """
    logger.info(f"Converting PDF to images: {pdf_path}")

    poppler_path = None
    if os.name == "nt":
        poppler_path = _find_poppler_path()
        if poppler_path:
            logger.info(f"Using local Poppler at: {poppler_path}")
        else:
            logger.warning(
                "Poppler not found under 'fir_extractor/poppler/**/bin'. "
                "Falling back to system PATH. If conversion fails, please install Poppler "
                "and/or place it under 'fir_extractor/poppler/'."
            )

    try:
        kwargs = {"dpi": dpi}
        if poppler_path:
            kwargs["poppler_path"] = poppler_path

        pil_images = convert_from_path(pdf_path, **kwargs)
        logger.info(f"Converted {len(pil_images)} pages")
        return [np.array(img) for img in pil_images]
    except Exception as e:
        logger.error(f"Error converting PDF '{pdf_path}': {e}")
        return []


def preprocess_image(image: np.ndarray) -> np.ndarray:
    """
    Apply OpenCV preprocessing to improve OCR accuracy.
    - Grayscale
    - Denoise
    - Contrast enhancement (CLAHE)
    """
    try:
        # pdf2image returns RGB; convert to grayscale
        if image is None:
            return image

        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image

        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)

        # Contrast enhancement using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)

        return enhanced
    except Exception as e:
        logger.error(f"Error in preprocessing: {e}")
        return image


def _get_rapid_ocr():
    """
    Lazily create and cache a singleton RapidOCR engine instance.
    """
    global _rapid_ocr_instance

    if _rapid_ocr_instance is None:
        with _rapid_ocr_lock:
            if _rapid_ocr_instance is None:
                logger.info("Loading RapidOCR model")
                from rapidocr_onnxruntime import RapidOCR

                _rapid_ocr_instance = RapidOCR()

    return _rapid_ocr_instance


def _sort_boxes_top_to_bottom(items):
    """
    Sort OCR items top-to-bottom (and then left-to-right).

    Each item is expected to be a tuple in the form:
        (top_y, left_x, text)
    """
    return sorted(
        items,
        key=lambda t: (
            t[0] if t[0] is not None else 0.0,
            t[1] if t[1] is not None else 0.0,
        ),
    )


def run_ocr_on_images(images: List[np.ndarray]) -> str:
    """
    Run RapidOCR on a list of images and return a single combined text string.

    - Loads RapidOCR lazily via a singleton
    - Sorts OCR boxes top-to-bottom for each page
    - Logs per-page statistics and overall text length
    """
    if not images:
        logger.warning("run_ocr_on_images called with empty image list")
        return ""

    engine = _get_rapid_ocr()
    all_lines: List[str] = []

    for page_idx, image in enumerate(images, start=1):
        try:
            result = engine(image)

            # rapidocr_onnxruntime typically returns (results, elapsed) or just results
            if isinstance(result, tuple):
                ocr_items = result[0]
            else:
                ocr_items = result

            positioned_lines = []

            for item in ocr_items or []:
                # Common structure: [box, text, score]
                box = None
                text = ""

                if isinstance(item, dict):
                    box = item.get("box") or item.get("bbox")
                    text = item.get("text") or item.get("label") or ""
                elif isinstance(item, (list, tuple)) and len(item) >= 2:
                    box, text = item[0], item[1]

                if not text:
                    continue

                top = None
                left = None
                if box is not None:
                    try:
                        # box can be 4 points [[x1, y1], ...]
                        ys = [pt[1] for pt in box]
                        xs = [pt[0] for pt in box]
                        top = float(min(ys))
                        left = float(min(xs))
                    except Exception:
                        top = None
                        left = None

                positioned_lines.append((top, left, text))

            positioned_lines = _sort_boxes_top_to_bottom(positioned_lines)
            page_text_lines = [t[2] for t in positioned_lines]

            logger.info(f"Page {page_idx}: {len(page_text_lines)} lines extracted")

            all_lines.extend(page_text_lines)
            # Form-feed as a sensible page separator
            all_lines.append("\f")
        except Exception as e:
            logger.error(f"Error running OCR on page {page_idx}: {e}")

    full_text = "\n".join(all_lines).strip()
    logger.info(f"OCR text length: {len(full_text)}")
    return full_text

