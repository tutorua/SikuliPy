# Product Requirements Document: SikuliPy

## 1. Overview
The goal of this project is to build a cross-platform desktop application designed for **visual testing of web, Android, and potentially iOS applications**. By interacting directly with visual elements on the screen, it enables testing mobile platforms without requiring source code access or specialized commercial testing tools. It allows users to create, edit, and execute Python test scripts that interact with images and text displayed on the screen. The application modernizes an existing Java/Jython tool by moving to a pure Python architecture.

## 2. Core Purpose & Functionality
The application acts as a comprehensive visual testing IDE. Users can execute scripts that perform the following:
- **Screen Capture:** Capture the full screen or specific, user-defined areas.
- **Baseline Comparison:** Compare newly captured screenshots against predefined baseline images to detect differences.
- **Baseline Management:** Define an area on the screen and save it as a new baseline image.
- **Dynamic Element Detection:** Automatically find actionable elements on dynamic web pages or mobile application interfaces, capture them, and calculate differences.
- **Text Verification (OCR):** Recognize text on the screen and compare it to expected values using Levenshtein distance.
- **Automation & Data Saving:** Use extracted text and image comparison results for test automation and data logging.

## 3. Input Methods
- **Automatic Screen Capture:** Built-in tools for taking screenshots and defining capture areas.
- **Manual Upload:** The ability to manually load and preview existing image files.
- **Semi-Automatic Element Detection:** The application can automatically scan a screen or image to detect and isolate text blocks and visual elements. Users can then manually review, refine, or update these detected regions for their scripts.

## 4. Technology Stack
- **Language & GUI:** Python (likely using PyQt or PySide to achieve the required IDE layout).
- **Image Processing:** OpenCV (used for template matching, object detection, image diffing, and filtering).
- **OCR Engine:** Tesseract.
- **License Requirement:** All underlying software and dependencies must be open-source.

## 5. Supported Platforms
- **Windows** (Target)
- **Linux** (Target)
- **macOS** (Target / Optional)

## 6. User Interface Requirements
The UI will closely resemble modern IDEs like VS Code, featuring a modular, resizable interface:
- **Theme Support:** Ability to switch between light and dark themes.
- **Layout Structure (Resizable Panels):**
  - **Top:** Main Menu & Toolbars (for execution controls, capture tools, etc.).
  - **Left:** Code/File Explorer (for managing Python test scripts, project files, and baseline images).
  - **Center:** Code Editor dedicated to Python, featuring Python syntax highlighting and linting.
  - **Right:** Image Preview panel. Features include:
    - **Dynamic Image List:** Automatically scans the active code editor for image references and displays them in a list.
    - **Image Display:** Renders the selected baseline image, current screenshot, or visual diff.
    - **Cursor Synchronization:** Clicking or moving the cursor over an image name in the editor automatically highlights it in the list and displays the image.
  - **Bottom:** Console Outputs (for displaying script execution logs, test results, and system messages).

## 7. Future Considerations (Post v1)
- **Playwright Integration:** Future versions may integrate directly with Playwright to control web browsers and execute tests more seamlessly.

## 8. References & Inspiration
SikuliPy is heavily inspired by and aims to modernize the functionality of the following legacy Java/Jython projects into a pure Python ecosystem:
- **SikuliX Repository:** [RaiMan/SikuliX1](https://github.com/RaiMan/SikuliX1)
- **OculiX Repository (Modern SikuliX Fork):** [oculix-org/Oculix](https://github.com/oculix-org/Oculix)
- **Feature Reference (SikuliX Documentation):** [SikuliX 2014 Docs](https://sikulix-2014.readthedocs.io/en/latest/)
