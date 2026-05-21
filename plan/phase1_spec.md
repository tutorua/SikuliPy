Phase 1 — Capture Screen / Capture Region (confirmed specifications)

Overview

Implement two complementary capture tools:
- Capture Screen: when selected, the full screen under the cursor is dimmed and the target application window is dimmed as requested; clicking saves the full-screen image (for browsers, capture whole-page if possible) into `assets/screenshots/` with a filename prefixed by the application name.
- Capture Region: the overlay dims all screens; on mouse press the top-left corner is fixed at the press position and the dimmed region spreads from that top-left to the current mouse position while dragging; on release the selected rectangle is captured and saved after the user provides a filename.

Confirmed Details

- Save path: `assets/screenshots/`.
- When Capture Screen is selected: dim the target application window under the mouse pointer; if it's a browser, attempt whole-page capture.
- Cursor shall not be included in captures.
- Filename popup: only allow filename (no path), append `.png` if missing; default name: `<sanitized-app-name>_<YYYYmmdd_HHMMSS>.png`.
- After save, insert relative path into editor at cursor position (default: enabled).
- Create `src/sikulipy/sikulipy_config.py` for defaults; UI to edit settings planned later.

Filename rules

- Sanitize app name: lowercase, replace non-alnum with `_`, trim.
- Timestamp format: `YYYYmmdd_HHMMSS`.
- If file exists, append `_1`, `_2`, etc.

Popup behavior

- Modal dialog with input field (pre-filled with default filename) and `Cancel`/`OK` buttons.
- `Cancel` aborts and discards the capture; `OK` writes the PNG to `assets/screenshots/`.

Overlay behavior

- Full-screen, always-on-top transparent overlay covering virtual desktop or per-screen overlays.
- For Capture Region: on mouse press record top-left, draw selection rect to mouse, on release capture.
- For Capture Screen: highlight/dim target app window; left-click saves full screen image.

Window stacking & delay

- When a capture is initiated, the SikuliPy application window will be lowered (sent behind other windows) so the user can target another application for capture. After the capture completes (and after the filename popup is closed or the capture is cancelled), the SikuliPy window will be restored to the top.
- A configurable delay is provided so the user has time to interact with the target application after the SikuliPy window is lowered. The default delay is 2 seconds and is controlled by `CAPTURE_DELAY_SECONDS` in `src/sikulipy/sikulipy_config.py`.

Platform notes

- Use `QGuiApplication.screenAt()` and `QScreen.grabWindow(0)`; on Windows may use native APIs for process name lookup and better full-page capture integration for browsers.

Next steps

- Implement `OverlayWidget`, wire toolbar actions, implement saving, and insert path into editor. Push increments for testing.

