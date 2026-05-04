"""
SikuliPy Test Configuration
============================
Global defaults for image matching and OCR thresholds.
Generated automatically — safe to edit manually.

TBD_ prefixes mark values that require manual completion.
"""

# ---------------------------------------------------------------------------
# Target Application
# ---------------------------------------------------------------------------
BASE_URL = "TBD_BASE_URL"

# ---------------------------------------------------------------------------
# Image Matching (cv2.matchTemplate with cv2.TM_SQDIFF_NORMED)
# Lower score = better match. 0.0 = perfect match, 1.0 = no match.
# Useful range: 0.0 – 0.05 for strict checks, up to 0.1 for loose checks.
# ---------------------------------------------------------------------------
IMAGE_MATCH_THRESHOLD = 0.02

# ---------------------------------------------------------------------------
# OCR Text Comparison (Levenshtein distance)
# 0 = exact match required; increase to allow minor OCR noise.
# ---------------------------------------------------------------------------
OCR_DISTANCE_THRESHOLD = 2

# ---------------------------------------------------------------------------
# OCR Mismatch Behaviour
# True  → test fails immediately (assert) on OCR mismatch
# False → warning is logged and test execution continues
# ---------------------------------------------------------------------------
OCR_BREAK_ON_MISMATCH = True
