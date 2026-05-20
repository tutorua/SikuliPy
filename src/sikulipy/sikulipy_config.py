"""
Default SikuliPy capture configuration
This file contains default settings used by the capture tools. Projects can copy or override
these values by creating a `sikulipy_config.py` in the project root (the app copies a template
when generating POM/tests).
"""

ASSETS_DIR = "assets/screenshots"
INCLUDE_CURSOR = False
CAPTURE_SCREEN_DIM_TARGET = True
DEFAULT_FILENAME_TEMPLATE = "{app}_{ts}.png"
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"
AUTO_INSERT_PATH = True

# Hotkey mapping (None = not assigned). Fill with strings like 'Ctrl+Shift+S'
HOTKEYS = {
    "capture_screen": "Ctrl+Shift+S",
    "capture_region": "Ctrl+Shift+R",
}

# Platform-specific options
PLATFORM = {
    "use_native_window_lookup": True,  # Windows: use GetForegroundWindow + psutil if available
    "attempt_browser_fullpage": True,  # Try Playwright/browser APIs to capture full page when active
}

# Delay (seconds) before capturing to allow user to interact with target window.
# When a capture is initiated the application should lower itself; the delay gives
# the user time to bring the target application to front before the actual capture.
CAPTURE_DELAY_SECONDS = 2
