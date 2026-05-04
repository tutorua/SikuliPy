import cv2
import pytesseract
import numpy as np

class VisionEngine:
    @staticmethod
    def extract_text(image_source):
        """
        Extract text from an image using PyTesseract.
        :param image_source: Either a string (path to image) or a numpy array (image buffer).
        :return: Extracted string.
        """
        if isinstance(image_source, str):
            img = cv2.imread(image_source)
            if img is None:
                raise ValueError(f"Could not load image from {image_source}")
        elif isinstance(image_source, np.ndarray):
            img = image_source
        else:
            raise TypeError("image_source must be a file path string or a numpy array")

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding to improve OCR accuracy
        # Using Otsu's thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        
        # Extract text
        text = pytesseract.image_to_string(thresh)
        return text.strip()

    @staticmethod
    def match_template(source_image, template_image, threshold=0.8):
        """
        Find a template within a source image.
        :param source_image: Path or numpy array
        :param template_image: Path or numpy array
        :param threshold: Confidence threshold
        :return: (x, y, w, h) of the best match, or None
        """
        def load_image(img_src):
            if isinstance(img_src, str):
                return cv2.imread(img_src)
            return img_src

        src = load_image(source_image)
        tpl = load_image(template_image)

        if src is None or tpl is None:
            return None

        # Convert to grayscale
        src_gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        tpl_gray = cv2.cvtColor(tpl, cv2.COLOR_BGR2GRAY)

        h, w = tpl_gray.shape

        res = cv2.matchTemplate(src_gray, tpl_gray, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        if max_val >= threshold:
            return (max_loc[0], max_loc[1], w, h)
        return None
