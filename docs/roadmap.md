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
