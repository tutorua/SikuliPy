# SikuliPy

SikuliPy is a powerful, pure Python-based Visual Testing IDE inspired by the original SikuliX. It provides a full-featured development environment to create, edit, and run visual automation scripts. By leveraging the power of OpenCV for image matching and PyTesseract for Optical Character Recognition (OCR), SikuliPy allows you to automate desktop applications based on what you see on the screen.

## ✨ Main Features

- **Integrated Development Environment (IDE)**: A modern, dark-themed UI built with PyQt6.
  - **Project Explorer**: Easily navigate your project directories.
  - **Python Editor**: Write automation scripts with live synchronization.
  - **Live Image Preview**: Automatically detects image references in your script and provides a visual preview on the fly.
  - **Console Output**: Live streaming of standard output and errors during script execution.
- **Vision Engine**: Robust template matching powered by OpenCV to find graphical elements on the screen.
- **OCR Engine**: Extract text from images or specific screen regions using PyTesseract.
- **Interactive Region Capture**: Built-in frameless overlay to visually select and capture specific regions of your screen for testing and instant text extraction.
- **Pure Python**: No Java dependencies. Fully scriptable and extensible in Python.

## ⚙️ Project Setup

### Prerequisites

1. **Python 3.10+**
2. **Tesseract OCR**: You must install Tesseract on your system for the OCR features to work.
   - **Windows**: Download the installer from the [UB-Mannheim repository](https://github.com/UB-Mannheim/tesseract/wiki).
   - **macOS**: `brew install tesseract`
   - **Linux**: `sudo apt install tesseract-ocr`
   - *Note: Ensure the `tesseract` executable is added to your system's `PATH`.*

### Installation

SikuliPy uses `uv` (or standard `pip`) for dependency management. 

Clone the repository and install the dependencies:

```bash
# Clone the repository
git clone <your-repo-url>
cd graphify

# Install dependencies using uv
uv sync
```

*(Alternatively, you can use standard pip: `pip install pyqt6 opencv-python pytesseract pyautogui`)*

## 🚀 Usage

### Running the IDE

To start the SikuliPy visual testing IDE, run:

```bash
uv run python src/sikulipy/main.py
```

Once the IDE opens, you can:
1. Open a project folder using the **File > Open** menu or the toolbar.
2. Create or load a `.py` script.
3. Click the **✂ Capture Region** button in the toolbar to grab a section of your screen and test the OCR extraction capabilities immediately.
4. Click **▶ Run** to execute your script. The output will stream directly to the integrated console pane.

### Running Examples

The `examples` directory contains standalone scripts demonstrating core functionalities. For example, to test the text extraction engine programmatically without opening the IDE:

```bash
uv run python examples/extract_text.py
```

This will generate a test image containing text, save it to disk, and run it through the VisionEngine to verify the OCR output.
