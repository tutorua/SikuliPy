"""
SikuliPy Testing Helpers
========================
Provides ImageAssertion and TextAssertion classes for use in generated POM-based tests.

Usage in page objects:
    from sikulipy.testing import ImageAssertion, TextAssertion

    ImageAssertion.assert_present(page, "assets/Buttons/Submit_123_0.png")
    TextAssertion.assert_text(page, "assets/Links/Home_123_1.png", expected="Home")
"""

import os
import cv2
import numpy as np
import pytesseract
import warnings

# ---------------------------------------------------------------------------
# Config defaults — overridden by sikulipy_config.py values at call site
# ---------------------------------------------------------------------------
_DEFAULT_IMAGE_THRESHOLD = 0.02   # cv2.TM_SQDIFF_NORMED: 0.0 = perfect, lower = better
_DEFAULT_OCR_DISTANCE = 2
_DEFAULT_OCR_BREAK = True


def _load_config():
    """Lazily import sikulipy_config so this module works without it."""
    try:
        import sikulipy_config as cfg
        return cfg
    except ImportError:
        return None


def _levenshtein(s1: str, s2: str) -> int:
    """Compute Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return _levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    prev = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        curr = [i + 1]
        for j, c2 in enumerate(s2):
            curr.append(min(prev[j + 1] + 1, curr[j] + 1, prev[j] + (c1 != c2)))
        prev = curr
    return prev[-1]


def _page_screenshot_np(page) -> np.ndarray:
    """Take a full-page screenshot via Playwright and return as BGR numpy array."""
    png_bytes = page.screenshot(full_page=True)
    arr = np.frombuffer(png_bytes, dtype=np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)


class ImageAssertion:
    """Assertions based on OpenCV template matching (cv2.TM_SQDIFF_NORMED)."""

    @staticmethod
    def assert_present(page, asset_path: str, threshold: float = None):
        """
        Assert that the baseline image is present somewhere on the current page.

        Parameters
        ----------
        page       : Playwright Page object
        asset_path : path to the baseline PNG (relative to project root)
        threshold  : max allowed TM_SQDIFF_NORMED score (lower = stricter).
                     Defaults to sikulipy_config.IMAGE_MATCH_THRESHOLD or 0.02.
        """
        cfg = _load_config()
        if threshold is None:
            threshold = getattr(cfg, 'IMAGE_MATCH_THRESHOLD', _DEFAULT_IMAGE_THRESHOLD)

        if not os.path.exists(asset_path):
            raise FileNotFoundError(f"[ImageAssertion] Baseline image not found: {asset_path}")

        template = cv2.imread(asset_path, cv2.IMREAD_COLOR)
        if template is None:
            raise ValueError(f"[ImageAssertion] Could not load baseline image: {asset_path}")

        screenshot = _page_screenshot_np(page)

        result = cv2.matchTemplate(screenshot, template, cv2.TM_SQDIFF_NORMED)
        min_val, _, _, _ = cv2.minMaxLoc(result)

        assert min_val <= threshold, (
            f"[ImageAssertion] Element not found on page.\n"
            f"  Baseline : {asset_path}\n"
            f"  Score    : {min_val:.4f} (threshold: {threshold})\n"
            f"  Hint     : Lower score = better match. Score > threshold means no match."
        )

    @staticmethod
    def get_match_score(page, asset_path: str) -> float:
        """
        Return the best TM_SQDIFF_NORMED score without asserting.
        Useful for debugging threshold values.
        """
        if not os.path.exists(asset_path):
            raise FileNotFoundError(f"[ImageAssertion] Baseline image not found: {asset_path}")
        template = cv2.imread(asset_path, cv2.IMREAD_COLOR)
        screenshot = _page_screenshot_np(page)
        result = cv2.matchTemplate(screenshot, template, cv2.TM_SQDIFF_NORMED)
        min_val, _, _, _ = cv2.minMaxLoc(result)
        return min_val


class TextAssertion:
    """Assertions combining Tesseract OCR and Levenshtein distance."""

    @staticmethod
    def assert_text(page, asset_path: str, expected: str,
                    max_distance: int = None, break_on_mismatch: bool = None):
        """
        Crop the element region from the live page, run Tesseract OCR, and compare
        the extracted text to ``expected`` using Levenshtein distance.

        Parameters
        ----------
        page             : Playwright Page object
        asset_path       : baseline PNG used to locate the element region
        expected         : expected string (e.g. "Sign In")
        max_distance     : maximum allowed Levenshtein distance.
                           Defaults to sikulipy_config.OCR_DISTANCE_THRESHOLD or 2.
        break_on_mismatch: if True, raises AssertionError on mismatch.
                           if False, emits a warning. Defaults to OCR_BREAK_ON_MISMATCH.
        """
        cfg = _load_config()
        if max_distance is None:
            max_distance = getattr(cfg, 'OCR_DISTANCE_THRESHOLD', _DEFAULT_OCR_DISTANCE)
        if break_on_mismatch is None:
            break_on_mismatch = getattr(cfg, 'OCR_BREAK_ON_MISMATCH', _DEFAULT_OCR_BREAK)

        if not os.path.exists(asset_path):
            raise FileNotFoundError(f"[TextAssertion] Baseline image not found: {asset_path}")

        template = cv2.imread(asset_path, cv2.IMREAD_COLOR)
        if template is None:
            raise ValueError(f"[TextAssertion] Could not load baseline image: {asset_path}")

        # Locate the element on the live page using matchTemplate
        screenshot = _page_screenshot_np(page)
        result = cv2.matchTemplate(screenshot, template, cv2.TM_SQDIFF_NORMED)
        _, _, min_loc, _ = cv2.minMaxLoc(result)

        h, w = template.shape[:2]
        x, y = min_loc
        region = screenshot[y:y + h, x:x + w]

        # Run OCR on the cropped region
        region_rgb = cv2.cvtColor(region, cv2.COLOR_BGR2RGB)
        extracted = pytesseract.image_to_string(region_rgb, config='--psm 7').strip()

        distance = _levenshtein(extracted.lower(), expected.lower())

        message = (
            f"[TextAssertion] OCR mismatch.\n"
            f"  Baseline  : {asset_path}\n"
            f"  Expected  : '{expected}'\n"
            f"  Extracted : '{extracted}'\n"
            f"  Distance  : {distance} (max allowed: {max_distance})"
        )

        if distance > max_distance:
            if break_on_mismatch:
                raise AssertionError(message)
            else:
                warnings.warn(message, stacklevel=2)

    @staticmethod
    def extract_text(asset_path: str) -> str:
        """Run OCR on a saved image file and return extracted text (utility)."""
        img = cv2.imread(asset_path)
        if img is None:
            raise FileNotFoundError(f"[TextAssertion] Image not found: {asset_path}")
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return pytesseract.image_to_string(img_rgb, config='--psm 7').strip()
