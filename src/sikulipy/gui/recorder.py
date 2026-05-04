from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, 
    QPushButton, QLineEdit, QLabel, QCheckBox, QRadioButton, QComboBox, QInputDialog
)
from PyQt6.QtCore import Qt, pyqtSignal

class KeyComboDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Key Combo")
        
        layout = QVBoxLayout(self)
        
        # Modifiers
        self.ctrl_cb = QCheckBox("Ctrl")
        self.alt_cb = QCheckBox("Alt")
        self.shift_cb = QCheckBox("Shift")
        
        mod_layout = QHBoxLayout()
        mod_layout.addWidget(self.ctrl_cb)
        mod_layout.addWidget(self.alt_cb)
        mod_layout.addWidget(self.shift_cb)
        layout.addLayout(mod_layout)
        
        # Radio buttons
        self.special_rb = QRadioButton("Special key")
        self.char_rb = QRadioButton("Character")
        self.char_rb.setChecked(True)
        
        radio_layout = QHBoxLayout()
        radio_layout.addWidget(self.special_rb)
        radio_layout.addWidget(self.char_rb)
        layout.addLayout(radio_layout)
        
        # Inputs
        self.special_cb = QComboBox()
        self.special_cb.addItems(["Enter", "Tab", "Space", "Esc", "Up", "Down", "Left", "Right", "Backspace", "Delete"])
        self.special_cb.setEnabled(False)
        
        self.char_edit = QLineEdit()
        self.char_edit.setMaxLength(1)
        
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.special_cb)
        input_layout.addWidget(self.char_edit)
        layout.addLayout(input_layout)
        
        self.special_rb.toggled.connect(self._on_radio_toggled)
        
        # OK / Cancel
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
    def _on_radio_toggled(self):
        is_special = self.special_rb.isChecked()
        self.special_cb.setEnabled(is_special)
        self.char_edit.setEnabled(not is_special)
        
    def get_combo_string(self):
        mods = []
        if self.ctrl_cb.isChecked(): mods.append("ctrl")
        if self.alt_cb.isChecked(): mods.append("alt")
        if self.shift_cb.isChecked(): mods.append("shift")
        
        if self.special_rb.isChecked():
            key = self.special_cb.currentText().lower()
        else:
            key = self.char_edit.text()
            
        if mods:
            return f"{'+'.join(mods)}+{key}"
        return key

class RecorderDialog(QDialog):
    # Signals to communicate complex workflows back to the main window
    webAutoRequested = pyqtSignal(str)
    imageActionRequested = pyqtSignal(str)

    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.setWindowTitle("Interactive Action Recorder")
        self.setMinimumWidth(400)
        
        # Always on top
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        
        main_layout = QVBoxLayout(self)
        
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        self.setup_web_auto_tab()
        self.setup_app_tab()
        self.setup_image_tab()
        self.setup_text_tab()
        self.setup_keyboard_tab()
        
        # Close button at the bottom
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        main_layout.addWidget(close_btn)

    def insert_code(self, code_str):
        cursor = self.editor.textCursor()
        cursor.insertText(code_str + "\n")
        self.editor.setTextCursor(cursor)
        # Make sure the editor has focus so the user sees the update
        self.editor.setFocus()

    def setup_web_auto_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("Enter URL here (e.g. https://google.com)")
        layout.addWidget(self.url_edit)
        
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.on_web_auto_ok)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)
        
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        self.tabs.addTab(tab, "Web Auto")
        
    def on_web_auto_ok(self):
        url = self.url_edit.text().strip()
        if url:
            self.insert_code(f'open_browser("{url}")')
            self.webAutoRequested.emit(url)

    def setup_app_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        launch_btn = QPushButton("Launch App")
        launch_btn.clicked.connect(lambda: self.prompt_and_insert("Launch App", "App Path or Name:", 'launch_app("{}")'))
        
        close_app_btn = QPushButton("Close App")
        close_app_btn.clicked.connect(lambda: self.prompt_and_insert("Close App", "App Name:", 'close_app("{}")'))
        
        layout.addWidget(launch_btn)
        layout.addWidget(close_app_btn)
        layout.addStretch()
        
        self.tabs.addTab(tab, "Application")

    def setup_image_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        buttons = ["Click", "DblClick", "RClick", "Wait", "WaitVanish", "WaitAppear", "Drag&Drop", "Swipe"]
        for btn_text in buttons:
            btn = QPushButton(btn_text)
            # Emit signal to main window to handle region capture for these actions
            btn.clicked.connect(lambda checked, text=btn_text: self.imageActionRequested.emit(text))
            layout.addWidget(btn)
            
        layout.addStretch()
        self.tabs.addTab(tab, "Image")

    def setup_text_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        for btn_text in ["Text.Click", "Text.Wait", "Text.Exists"]:
            btn = QPushButton(btn_text)
            # These can prompt for text to look for
            btn.clicked.connect(lambda checked, t=btn_text: self.prompt_and_insert(t, "Enter Text to Match:", f'{t.lower().replace(".", "_")}("{{}}")'))
            layout.addWidget(btn)
            
        layout.addStretch()
        self.tabs.addTab(tab, "Text")

    def setup_keyboard_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        type_btn = QPushButton("Type")
        type_btn.clicked.connect(lambda: self.prompt_and_insert("Type", "Text to type:", 'type("{}")'))
        
        combo_btn = QPushButton("Key Combo")
        combo_btn.clicked.connect(self.on_key_combo)
        
        pause_btn = QPushButton("Pause")
        pause_btn.clicked.connect(lambda: self.prompt_and_insert("Pause", "Duration (seconds):", 'pause({})'))
        
        layout.addWidget(type_btn)
        layout.addWidget(combo_btn)
        layout.addWidget(pause_btn)
        layout.addStretch()
        
        self.tabs.addTab(tab, "Keyboard")

    def prompt_and_insert(self, title, label, template):
        text, ok = QInputDialog.getText(self, title, label)
        if ok and text:
            # Escape quotes if necessary
            clean_text = text.replace('"', '\\"')
            self.insert_code(template.format(clean_text))
            
    def on_key_combo(self):
        dialog = KeyComboDialog(self)
        if dialog.exec():
            combo_str = dialog.get_combo_string()
            self.insert_code(f'key_combo("{combo_str}")')
