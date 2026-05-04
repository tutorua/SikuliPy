# Product Backlog

## Feature: Interactive Action Recorder

**Purpose:** 
To ease the generation of automation code in an interactive mode by providing a GUI interface for constructing application interactions.

**Trigger:** 
User clicks on the "⏺ Record" button in the main toolbar of the IDE.

**UI Description:**
A popup window (Recorder Dialog) opens containing a tabbed interface and a main "Close" button at the bottom. 

**Tabs & Controls:**

1. **Web Auto**
   - Field: Edit box to enter the URL for a page under test.
   - Buttons: `OK`, `Cancel`.

2. **Application**
   - Buttons: `Launch App`, `Close App`.

3. **Image**
   - Buttons: `Click`, `DblClick`, `RClick`, `Wait`, `WaitVanish`, `WaitAppear`, `Drag&Drop`, `Swipe`.

4. **Text**
   - Buttons: `Text.Click`, `Text.Wait`, `Text.Exists`.

5. **Keyboard**
   - Buttons: `Type`, `Key Combo`, `Pause`.

**Expected Workflow:**
Interacting with these controls should generate the corresponding Python code and automatically insert it into the active editor, potentially triggering region/screen capture workflows or text input prompts to gather the necessary arguments for the code snippet.
