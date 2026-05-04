import sys
from pathlib import Path
import cv2
import numpy as np

# Ensure the 'src' directory is in the Python path
project_root = Path(__file__).resolve().parent.parent
src_dir = str(project_root / 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from sikulipy.vision.engine import VisionEngine

def main():
    # 1. Create a blank white image
    img = np.ones((200, 600, 3), dtype=np.uint8) * 255
    
    # 2. Add some clear text to the image
    text_to_write = "Hello SikuliPy OCR!"
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, text_to_write, (50, 100), font, 1.5, (0, 0, 0), 3, cv2.LINE_AA)
    
    # 3. Save the generated image for reference
    test_image_path = "test_ocr_image.png"
    cv2.imwrite(test_image_path, img)
    print(f"Created a test image with text at: {test_image_path}")
    
    print("\nRunning OCR extraction...")
    try:
        # You can pass a numpy array directly to the engine:
        # extracted_text = VisionEngine.extract_text(img)
        
        # Or you can pass a file path:
        extracted_text = VisionEngine.extract_text(test_image_path)
        
        print("-" * 30)
        print("Expected Text :", text_to_write)
        print("Extracted Text:", extracted_text)
        print("-" * 30)
        
        if text_to_write in extracted_text:
            print("OCR extraction successful!")
        else:
            print("OCR extraction completed, but might have minor inaccuracies.")
            
    except Exception as e:
        print(f"Error during OCR extraction: {e}")
        print("\nPlease ensure that Tesseract OCR is installed on your system.")
        print("If it is installed in a custom location, ensure it's in your system PATH.")

if __name__ == "__main__":
    main()
