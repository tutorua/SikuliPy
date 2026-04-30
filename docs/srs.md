# System Requirements Specification (SRS): SikuliPy

## 1. Introduction
### 1.1 Purpose
The purpose of this document is to define the technical and system-level requirements for **SikuliPy**, a cross-platform desktop application designed for visual testing of applications (Web, Android, iOS). This document serves as a blueprint for developers and architects for the software's design and implementation.

### 1.2 Scope
SikuliPy provides an Integrated Development Environment (IDE) to write, debug, and execute Python scripts that interact directly with the graphical user interface of the host operating system or a connected mobile device (via ADB). It replaces the legacy Java-based SikuliX/OculiX toolset with a pure Python architecture.

### 1.3 Definitions, Acronyms, and Abbreviations
- **IDE:** Integrated Development Environment
- **OCR:** Optical Character Recognition
- **ADB:** Android Debug Bridge
- **OpenCV:** Open Source Computer Vision Library
- **UI:** User Interface

## 2. Overall Description
### 2.1 Product Perspective
SikuliPy is a standalone desktop application. It operates by capturing image buffers directly from the host operating system's display manager or via device bridge tools like ADB. It processes these images using Python libraries and sends mouse/keyboard events back to the OS or mobile device.

### 2.2 System Modules & Architecture
SikuliPy will consist of the following core modules:
1. **GUI Module:** The front-end interface built with PyQt or PySide. Manages the layout, editor, image previews, and user interactions.
2. **Editor & Execution Module:** A Python code editor component with syntax highlighting (e.g., using QScintilla or similar). It spawns isolated Python execution environments to run user scripts safely.
3. **Vision & OCR Module:** The backend engine wrapper around `OpenCV` (for template matching, thresholding, edge detection) and `pytesseract` (for OCR). 
4. **Interaction Module:** Interfaces with OS-level APIs (like `pyautogui` or `pynput`) to simulate mouse clicks and keyboard strokes on desktop, and wraps ADB commands for Android interaction.

### 2.3 Operating Environment
- **Host OS:** Windows 10/11, Linux (Ubuntu/Debian-based), macOS (11+).
- **Target OS (for Mobile Testing):** Android (via ADB).
- **Runtime:** Python 3.10+

## 3. Specific System Features

### 3.1 Python Scripting IDE
- **3.1.1** The system must provide a multi-tabbed code editor supporting standard Python syntax highlighting.
- **3.1.2** The editor must support basic linting (e.g., via integration with `flake8` or `pylint`).
- **3.1.3** The IDE must provide a file explorer to browse workspace directories, scripts, and baseline image directories.

### 3.2 Visual Element Processing (Vision Module)
- **3.2.1 Template Matching:** The system shall use OpenCV's `matchTemplate` functions to locate a smaller target image within a larger screen capture.
- **3.2.2 Thresholding & Diffing:** The system shall provide functions to compute the absolute difference between two image matrices and highlight differing regions.
- **3.2.3 Semi-Automatic Detection:** The system shall utilize contour detection techniques to automatically draw bounding boxes around visually distinct UI elements (buttons, text fields).

### 3.3 Text Recognition (OCR Module)
- **3.3.1 Text Extraction:** The system shall integrate Tesseract to convert specified image regions into string data.
- **3.3.2 Fuzzy Matching:** The system shall provide built-in utility functions to calculate the Levenshtein distance for fuzzy text assertions in test scripts.

### 3.4 Interaction & Capture (Input/Output Module)
- **3.4.1 Desktop Capture:** The system shall capture partial or full screenshots of the host desktop natively. It shall support multiscreen configuration of the host OS.
- **3.4.2 ADB Capture & Control:** The system shall execute ADB shell commands (`screencap`, `input tap`, `input text`, `swipe`, `drag`, `dragTo`, etc.) to capture Android screens and send events over USB/Wi-Fi.
- **3.4.3 Desktop Control:** The system shall simulate keyboard and mouse events natively on the host OS. It shall support multiscreen configuration of the host OS. 

## 4. External Interface Requirements

### 4.1 User Interfaces
The application interface will follow a "VS Code-like" dark/light theme paradigm:
- **Header:** Action buttons (Run, Stop, Capture Screen, Capture Region).
- **Left Sidebar:** Project file tree and image asset browser.
- **Center Area:** Code editor.
- **Right Sidebar:** Image preview pane showing the currently selected baseline image or the latest test output diff.
- **Bottom Panel:** Terminal/Console output for standard out/error from the executing script.

### 4.2 Software Interfaces
- **OpenCV Python Bindings:** `opencv-python` for core image mathematics.
- **Tesseract Engine:** Must interface with a locally installed Tesseract executable.
- **ADB Executable:** Must interface with a locally available `adb` binary or include it via a standalone package.

## 5. Non-Functional Requirements

### 5.1 Performance Requirements
- **Response Time:** Template matching over a 1080p screen capture should execute in under 500ms on a standard modern CPU and might be bigger for higher resolution screens and interactions with Android devices by Wifi.
- **Memory Management:** Image buffers must be explicitly released or garbage-collected promptly to prevent memory leaks during long test suites.

### 5.2 Reliability & Stability
- Script execution must be sandboxed or run in a separate subprocess so that an infinite loop or fatal error in a user script does not crash the main SikuliPy IDE.

## 6. Future System Considerations
- **Plugin Architecture:** The system architecture should be modular enough to allow third-party plugins (e.g., a Playwright connector module) in future updates.
