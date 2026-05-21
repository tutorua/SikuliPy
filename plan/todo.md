Phase 1 — Capture Screen / Capture Region

Overview

Implement two complementary capture tools:
- Capture Screen: user moves mouse to a screen, that screen is dimmed; click saves full-screen image to assets with filename prefixed by the application name under the cursor.
- Capture Region: user presses mouse to set top-left corner; while dragging, a dimmed overlay shows the expanding selection; on release, capture the selected rectangle and prompt for filename.

Specifications

1) General
- Support multiple monitors: user can move mouse to any screen; functions operate on the screen under the cursor.
- Use device pixel ratio to ensure captured image has correct resolution on HiDPI displays.
- Save images under project `assets/screenshots/` (or `assets/<category>/`) by default; filenames start with the application/process name (sanitized), an optional timestamp, and suffix index when needed.
- Optionally include or exclude mouse cursor in saved images (ask below).

2) Capture Screen
- When activated, show a full-screen, always-on-top overlay across all screens with a dim (semi-transparent black) layer.
- Highlight the top-level application window under the mouse pointer (or dim it differently) — requirement needs confirmation (see questions).
- When the user clicks the left mouse button, capture the entire screen containing the cursor and save the image.
- Show a small toast or dialog after save with the saved path and an option to open the containing folder.

3) Capture Region
- On activation, show the same dimming overlay across all screens.
- On left mouse press: record the press position as the top-left corner of the selection and freeze it.
- While dragging, update the selection rectangle from that fixed top-left to the current cursor position; render the dimmed overlay with the selection area either undimmed or highlighted (inverted transparency) so selection contents are visible clearly.
- On mouse release: finalize bottom-right corner, capture the rectangle region from the underlying screen buffer (accounting for device pixel ratio), and prompt the user with a modal popup to enter filename, with `Cancel` and `OK` buttons. `Cancel` aborts and discards the capture; `OK` saves.
- Default filename: `<sanitized-app-name>_<YYYYmmdd_HHMMSS>.png` (user-editable in popup). If file exists, append `_1`, `_2`, etc.

Implementation Steps (high level)

A. UI & wiring
- Add two QAction toolbar items: `Capture Screen` and `Capture Region` (icons and tooltip). Wire to `on_capture_screen()` and `on_capture_region()` handlers in `src/sikulipy/gui/main_window.py`.

B. Overlay widget
- Implement a frameless, transparent `OverlayWidget(QWidget)` placed at top-level of the application that can cover each screen (one Overlay per QScreen or a single overlay spanning virtual geometry). Use `Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool` and set `setAttribute(Qt.WA_TransparentForMouseEvents, False)` to receive mouse events.
- Draw the dim layer in `paintEvent()` using semi-transparent black. During region selection, clear or draw a border for the selection rect so the user sees the area.
- Capture mouse events: `mousePressEvent`, `mouseMoveEvent`, `mouseReleaseEvent` to implement region selection. For `Capture Screen` mode, `mousePressEvent` should immediately capture full screen and close overlay.

C. Screen capture logic
- Determine the `QScreen` under the cursor using `QGuiApplication.screenAt(QCursor.pos())`.
- Grab the screen using `screen.grabWindow(0)` (or for platform-specific improvements, use native APIs). For region capture, crop the QPixmap using QRect (account for `devicePixelRatio()` on HiDPI).
- Determine the application/process name under cursor for filename prefix: attempt `QWindowFromPoint` or use OS APIs (Windows: `GetForegroundWindow` + `GetWindowThreadProcessId` + `psutil` to map PID→exe name). If OS-level lookup fails or is unavailable, fall back to screen name (e.g., `screen1`).

D. Filename & saving
- Show filename entry `QInputDialog` or a custom modal widget with `OK/Cancel`. On `OK`, write the PNG into `assets/screenshots/` ensuring directories exist and name is sanitized.
- After save, insert a relative path into the editor at cursor position (optional — ask) and update the image list index.

E. Edge cases & behavior
- Escape key cancels overlay and selection.
- Right-click cancels.
- If overlay loses focus or app is minimized, cancel cleanly.
- Respect multi-monitor coordinates and scaling.

Testing Plan

- Manual tests across 2+ monitors with different scaling factors (100%, 150%, 200%).
- Confirm filename sanitization and uniqueness.
- Confirm cancel behavior on Escape and right-click.
- Confirm saved image can be opened and asset path inserted into editor.
- Test inclusion/exclusion of mouse cursor (if requested).

Questions (confirm these before implementation)

1. Where do you want to save screenshots exactly? Default `assets/screenshots/` is proposed; confirm.
2. When you say "the application under the mouse pointer shall be dimmed" — do you mean the target application should be highlighted (undimmed) and the rest dimmed, or the inverse (application dimmed distinctly)? Clarify desired visual.
3. Should the saved filename include a timestamp by default? Proposed: yes, `_YYYYmmdd_HHMMSS`.
4. Include mouse cursor in the capture? (Yes/No) — default: No.
5. After saving, should the image path be automatically inserted into the current editor location? (Yes/No) — default: Yes.
6. Do you want hotkeys for these actions (e.g., `Ctrl+Shift+S` for screen, `Ctrl+Shift+R` for region)?

Suggested Improvements

- Add a small capture toolbar on the overlay for quick choices (include cursor, copy to clipboard, save without prompt).
- Add a brief preview thumbnail before final save with crop adjust handles.
- Add an auto-baseline update mode to overwrite an existing named baseline image.
- Add an undo/restore for last capture.

Next steps

- Confirm the questions above, then I'll implement Phase 1 according to the plan and push incremental commits.

