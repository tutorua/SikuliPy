# Business Requirements Document (BRD): SikuliPy

## 1. Executive Summary
SikuliPy is a cross-platform desktop application designed to modernize and simplify the visual testing of web, Android, and iOS applications. By transitioning from a legacy SikuliX and OculiX Java/Jython architecture to a pure Python stack, SikuliPy provides QA engineers and developers with a powerful, open-source IDE to write test scripts, capture screen areas, perform image comparisons, and extract text via OCR. It uniquely allows testing on mobile and web platforms strictly through visual interaction, completely bypassing the need for source code access or expensive commercial tools.

## 2. Business Objectives & Goals
- **Cost Reduction:** Eliminate the need for expensive, proprietary commercial tools for visual and mobile testing.
- **Universal Testing Capability:** Enable testing across any platform (Web, Android, iOS) by interacting with the visual layer rather than the underlying DOM or view hierarchy.
- **Modernization:** Replace legacy Java/Jython dependencies with a modern, widely-supported Python ecosystem.
- **Productivity Boost:** Provide an intuitive, IDE-like interface (similar to VS Code) to accelerate test creation and execution.

## 3. Target Audience (User Personas)
- **QA Automation Engineers:** Users writing automated visual test scripts to validate UI changes across different platforms.
- **Manual Testers:** Users leveraging the semi-automatic element detection to easily capture and define baseline images for visual verification.
- **Software Developers:** Developers needing a quick way to write assertions for visual components without diving into complex framework setups (like Appium).

## 4. Project Scope
### 4.1 In-Scope
- Development of a desktop GUI using Python (e.g., PyQt/PySide).
- Implementation of a Python-centric code editor with syntax highlighting and linting.
- Integration of OpenCV for image processing, template matching, and diffing.
- Integration of Tesseract for OCR text extraction and Levenshtein distance comparisons.
- Manual, automatic, and semi-automatic screen capture and element detection functionalities, including capturing screens and elements directly from desktop PCs and Android devices via ADB (Android Debug Bridge).
- Execution environment for running user-defined Python test scripts.

### 4.2 Out-of-Scope (for Version 1.0)
- Deep integration with Playwright or Selenium for DOM-based browser manipulation.
- Mobile device emulation (the tool interacts with what is visible on the host screen, e.g., an emulator window or mirrored device screen).
- CI/CD pipeline plugins (though scripts can be run headlessly if supported in the future, the primary focus is the desktop IDE).

## 5. Detailed Functional Requirements

### 5.1 Scripting Environment
- **REQ-01:** The system shall provide a built-in code editor specifically tailored for Python.
- **REQ-02:** The editor shall support standard IDE features, including syntax highlighting, code completion, and linting.
- **REQ-03:** The system shall include a File Explorer panel to manage test script files and baseline image assets.

### 5.2 Visual Detection & Processing
- **REQ-04:** The system shall utilize OpenCV to perform image template matching, allowing the script to find a baseline image within a larger screen capture.
- **REQ-05:** The system shall detect and highlight differences between a captured image and a baseline image.
- **REQ-06:** The system shall support Tesseract OCR to extract text from defined screen areas.
- **REQ-07:** The system shall calculate the Levenshtein distance between extracted text and expected text strings for validation.

### 5.3 Input and Interaction Methods
- **REQ-08:** The system shall allow users to manually upload existing images for testing and comparison.
- **REQ-09:** The system shall provide an automatic screen capture tool to take screenshots of the entire screen or user-defined bounding boxes.
- **REQ-10:** The system shall feature "Semi-Automatic Element Detection," scanning a screen/image to isolate distinct text blocks and visual elements, allowing the user to select and refine these regions for test scripts.

### 5.4 Execution and Reporting
- **REQ-11:** The system shall be able to execute the Python test scripts directly from the IDE.
- **REQ-12:** The system shall display execution logs, standard output, and standard error in a dedicated Console Output panel.
- **REQ-13:** The system shall save test results, generated diff images, and extracted text to the local file system.

## 6. Non-Functional Requirements

### 6.1 Usability
- **NFR-01:** The UI shall feature a modern, dark/light theme switchable interface, closely resembling VS Code.
- **NFR-02:** The UI shall consist of modular, resizable panels (Top Menu, Left Explorer, Center Editor, Right Image Preview, Bottom Console).

### 6.2 Portability & Compatibility
- **NFR-03:** The application must run natively on Windows and Linux. macOS support is highly desirable but secondary.
- **NFR-04:** All dependencies and core libraries must be fully open-source.

### 6.3 Performance
- **NFR-05:** Image processing tasks (diffing, template matching) should execute with minimal latency to provide real-time or near real-time feedback to the tester.

## 7. Assumptions & Dependencies
- It is assumed the user has a Python environment installed or the application is packaged with a standalone Python runtime.
- The system depends on the open-source community for updates to OpenCV and Tesseract.

## 8. Future Enhancements
- Native Playwright integration to allow hybrid testing (visual validation combined with DOM interaction).

## 9. References & Inspiration
SikuliPy is heavily inspired by and aims to modernize the functionality of the following legacy Java/Jython projects into a pure Python ecosystem:
- **SikuliX Repository:** [RaiMan/SikuliX1](https://github.com/RaiMan/SikuliX1)
- **OculiX Repository (Modern SikuliX Fork):** [oculix-org/Oculix](https://github.com/oculix-org/Oculix)
- **Feature Reference (SikuliX Documentation):** [SikuliX 2014 Docs](https://sikulix-2014.readthedocs.io/en/latest/)
