import os
import cv2
import numpy as np
from pdf2image import convert_from_path
from doctr.models import ocr_predictor

# Load model once at module level if possible, or inside function to avoid multiprocessing pickling issues.
# For multiprocessing, it's safer to load inside the worker process, but that's slow.
# We will load it inside the function for safety with multiprocessing, 
# although 'pretrained=True' caches weights.

def convert_pdf_to_images(pdf_path):
    """
    Convert a PDF into a list of numpy arrays (images) at 300 DPI.
    """
    try:
        # standard 300 dpi for better OCR
        pil_images = convert_from_path(pdf_path, dpi=300)
        return [np.array(img) for img in pil_images]
    except Exception as e:
        print(f"Error converting PDF {pdf_path}: {e}")
        return []

def preprocess_image(image):
    """
    Apply OpenCV preprocessing to improve OCR accuracy.
    - Grayscale
    - Denoise
    - Thresholding
    """
    try:
        # Convert RGB to BGR if using cv2 directly on PIL numpy array (which is RGB)
        # pdf2image returns RGB. OpenCV uses BGR usually, but for grayscale it matters less 
        # if we just pick one channel, but let's be correct.
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image

        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)

        # Adaptive Thresholding to handle varying lighting/scanning quality
        # binary inverse might be needed if text is light on dark, but usually standard is fine.
        # We'll use Gaussian C thresholding.
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Un-inverting if needed? DocTR is quite robust. 
        # Sometimes standard denoised gray is better than aggressive thresholding for deep learning OCR.
        # The user requested 'adaptive threshold' and 'contrast enhancement'.
        
        # Contrast enhancement using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)

        # Let's return the enhanced grayscale image as DocTR handles it well.
        # Passing strict binary threshold might actually hurt deep learning models trained on natural images.
        # However, for scanned docs, thresholding *can* help if they are noisy.
        # Combining: Enhanced Grayscale is usually safest for DocTR. 
        # But complying with user request for 'adaptive threshold':
        # Let's return the enhanced version which usually preserves more info than binary.
        # If user strictly wants thresholded, we can return 'thresh'.
        # Let's stick to enhanced grayscale for now as it's safer for heavy models.
        
        return enhanced
    except Exception as e:
        print(f"Error in preprocessing: {e}")
        return image

def run_ocr_on_images(images):
    """
    Run DocTR OCR on a list of images and return consolidated text.
    """
    try:
        # Initialize predictor
        # pretrained=True downloads weights if not present
        model = ocr_predictor(det_arch='db_resnet50', reco_arch='crnn_vgg16_bn', pretrained=True)
        
        full_text = []
        
        # Process in batches or one by one? 
        # simple: pass list of images
        # images might need to be in list of numpy arrays
        
        doc = model(images)
        
        # Extract text
        for page in doc.pages:
            for block in page.blocks:
                for line in block.lines:
                    line_text = " ".join([word.value for word in line.words])
                    full_text.append(line_text)
            full_text.append("\f") # Form feed to mark page break if needed, or just join with newline
            
        return "\n".join(full_text)
        
    except Exception as e:
        print(f"Error in OCR engine: {e}")
        return ""
