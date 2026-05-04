# Roadmap: Action Recorder UI

This roadmap outlines the architecture and tasks required to build the Interactive Action Recorder popup as requested in the backlog.

## Phase 1: UI Construction
- **Goal:** Build the visual interface of the Recorder Dialog.
- **Tasks:**
  - Create `src/sikulipy/gui/recorder.py`.
  - Implement `QTabWidget` with the 5 distinct tabs (Web Auto, Application, Image, Text, Keyboard).
  - Lay out all the required buttons within each tab.
  - Connect the `⏺ Record` button in the main window to open this dialog.

## Phase 2: Workflow & Code Generation Hookup
- **Goal:** Make the buttons functional so they insert code into the editor.
- **Tasks:**
  - Implement dynamic code string generation for each action.
  - Connect actions that require parameters (like `Type`, `Launch App`) to secondary input prompts.
  - Connect Image-based actions (like `Click`) to the region capture workflow so the user can select an image to click on.
  - Safely insert the generated code at the user's current cursor position in the editor.

## Phase 3: Refinement & Error Handling
- **Goal:** Ensure smooth UX and robust edge-case handling.
- **Tasks:**
  - Handle cases where user cancels an input prompt or region capture.
  - Ensure the dialog remains on top but doesn't block interactions with the editor if it's non-modal.

---

# Phase 4: POM-Style Test Generation from Web Inspector Captures

## Overview

This phase introduces automated generation of **pytest-based Page Object Model (POM)** test suites directly from elements captured in the Web Inspector. Tests use Playwright for browser navigation and interaction, and employ OpenCV `matchTemplate` (with `cv2.TM_SQDIFF_NORMED`) for visual assertions and Tesseract OCR + Levenshtein distance for text-based assertions.

The goal is to support both **conventional selector-based** interactions and **image-based** visual verification, enabling detection of layout shifts, element overlapping, and visual regressions.

---

## Key Design Decisions

| Decision | Choice |
|---|---|
| Test framework | `pytest` (run externally, CI-compatible) |
| Browser automation | `playwright` (Python sync API) |
| Image comparison | `cv2.matchTemplate` with `cv2.TM_SQDIFF_NORMED` |
| Text comparison | Tesseract OCR + Levenshtein distance |
| Configuration | Central `sikulipy_config.py` with per-test overrides |
| Missing values | Placeholder prefix `TBD_` for manual completion |
| Baseline management | Radiobutton in Web Inspector: `Generate Tests` / `Update Baseline` |
| Test failure on OCR mismatch | Configurable boolean `OCR_BREAK_ON_MISMATCH` |

---

## Architecture

```
project/
├── assets/
│   ├── Links/          # Baseline images, captured by Web Inspector
│   ├── Buttons/
│   └── Inputs/
├── pages/
│   └── <page_name>_page.py    # Generated Page Object class
├── tests/
│   └── test_<page_name>.py    # Generated pytest test file
└── sikulipy_config.py         # Global configuration constants
```

### `sikulipy_config.py` (generated once, user-editable)
```python
# SikuliPy Test Configuration
BASE_URL = "TBD_BASE_URL"

# OpenCV matchTemplate threshold (cv2.TM_SQDIFF_NORMED — lower is better match)
# 0.0 = perfect match, 1.0 = no match. Typical useful range: 0.0 – 0.05
IMAGE_MATCH_THRESHOLD = 0.02

# OCR: Levenshtein distance tolerance (0 = exact match)
OCR_DISTANCE_THRESHOLD = 2

# If True, test fails immediately on OCR mismatch. If False, logs a warning and continues.
OCR_BREAK_ON_MISMATCH = True
```

### `pages/<page_name>_page.py` (generated Page Object)
```python
from playwright.sync_api import Page
from sikulipy.testing import ImageAssertion, TextAssertion

class HomePage:
    def __init__(self, page: Page):
        self.page = page

    def navigate(self):
        self.page.goto("TBD_PAGE_URL")

    # --- Buttons ---
    def click_submit_button(self):
        # Option 1: conventional selector (fill in manually)
        self.page.click("TBD_SELECTOR_submit")
        # Option 2: image-based (auto-generated)
        # ImageAssertion.click(self.page, "assets/Buttons/Submit_1234_0.png")

    def assert_submit_button_visible(self):
        ImageAssertion.assert_present(
            self.page,
            "assets/Buttons/Submit_1234_0.png"
        )

    # --- Inputs ---
    def fill_search_input(self, text: str):
        self.page.fill("TBD_SELECTOR_search", text)

    # --- Links ---
    def assert_home_link_visible(self):
        ImageAssertion.assert_present(
            self.page,
            "assets/Links/Home_1234_1.png"
        )

    def assert_home_link_text(self):
        TextAssertion.assert_text(
            self.page,
            "assets/Links/Home_1234_1.png",
            expected="TBD_EXPECTED_TEXT"
        )
```

### `tests/test_<page_name>.py` (generated pytest file)
```python
import pytest
from playwright.sync_api import sync_playwright
from pages.home_page import HomePage

@pytest.fixture
def page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        yield page
        browser.close()

class TestHomePage:
    def test_submit_button_visible(self, page):
        home = HomePage(page)
        home.navigate()
        home.assert_submit_button_visible()

    def test_home_link_text(self, page):
        home = HomePage(page)
        home.navigate()
        home.assert_home_link_text()
```

### `src/sikulipy/testing.py` (assertion helpers library)
```python
import cv2, numpy as np
from sikulipy_config import IMAGE_MATCH_THRESHOLD, OCR_DISTANCE_THRESHOLD, OCR_BREAK_ON_MISMATCH

class ImageAssertion:
    @staticmethod
    def assert_present(page, asset_path, threshold=None):
        threshold = threshold or IMAGE_MATCH_THRESHOLD
        screenshot = page.screenshot()
        # ... cv2.TM_SQDIFF_NORMED matching logic ...

class TextAssertion:
    @staticmethod
    def assert_text(page, asset_path, expected, max_distance=None):
        max_distance = max_distance or OCR_DISTANCE_THRESHOLD
        # ... Tesseract OCR + Levenshtein distance comparison ...
```

---

## Phase 4 Tasks

### Step 1 — Web Inspector Baseline Mode UI
- Add two radio buttons to `WebInspectorPane`:
  - 🔵 **Generate Tests** *(default)*: captures images AND generates POM files.
  - 🔄 **Update Baseline**: replaces existing baseline images only; no test code is generated.
- In "Update Baseline" mode, filenames omit the timestamp suffix so they overwrite existing baselines cleanly.

### Step 2 — Testing Helpers Library
- Create `src/sikulipy/testing.py` with:
  - `ImageAssertion.assert_present(page, asset_path, threshold)` — takes a fresh screenshot, crops the region via Playwright bounding box, runs `cv2.matchTemplate` with `cv2.TM_SQDIFF_NORMED`.
  - `TextAssertion.assert_text(page, asset_path, expected, max_distance)` — crops the region, runs Tesseract OCR, computes Levenshtein distance against `expected`.

### Step 3 — Configuration File Generator
- On first test generation for a project, create `sikulipy_config.py` at the project root if it doesn't exist (never overwrite).
- Populate with global defaults and `TBD_` placeholders.

### Step 4 — Page Object Generator
- Create `src/sikulipy/codegen/pom_generator.py`.
- Input: list of captured elements (from Web Inspector), page URL, page name.
- Output: `pages/<page_name>_page.py`.
- Each element gets:
  - A `click_<name>()` method with both a Playwright selector stub (`TBD_SELECTOR_<name>`) and a commented image-based alternative.
  - An `assert_<name>_visible()` method using `ImageAssertion`.
  - An `assert_<name>_text()` method using `TextAssertion` for elements that had recognizable text/aria-label.

### Step 5 — pytest File Generator
- Create `src/sikulipy/codegen/test_generator.py`.
- Input: page object module path, list of elements.
- Output: `tests/test_<page_name>.py` with a `pytest.fixture` for Playwright and one test method per assertion method in the page object.

### Step 6 — IDE Integration (Generate Tests Button)
- Wire the **Take ElsScrht** button (in "Generate Tests" mode) to:
  1. Save baseline images as before.
  2. Call `pom_generator.py` → write/overwrite `pages/<name>_page.py`.
  3. Call `test_generator.py` → write/overwrite `tests/test_<name>.py`.
  4. Generate `sikulipy_config.py` if absent.
  5. Log all generated file paths in the console.

---

## Verification Plan
- Manually run generated tests against the live site with `pytest tests/`.
- Verify `TM_SQDIFF_NORMED` thresholds catch intentional visual regressions (e.g., moved button).
- Verify Levenshtein logic flags text changes and respects `OCR_BREAK_ON_MISMATCH`.
- Verify "Update Baseline" mode replaces images without re-generating test files.

