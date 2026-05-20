import os

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, 
    QPushButton, QLineEdit, QLabel, QCheckBox, QRadioButton, QComboBox, QInputDialog, QTextEdit, QMessageBox
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
        self.setMinimumWidth(600)
        
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
        self.setup_api_tab()
        
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
        self.url_edit.setText("https://")
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

    def setup_api_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.api_base_url_edit = QLineEdit()
        self.api_base_url_edit.setPlaceholderText("Base URL (e.g. https://api.example.com)")
        layout.addWidget(QLabel("Base URL:"))
        layout.addWidget(self.api_base_url_edit)

        self.api_endpoint_edit = QLineEdit()
        self.api_endpoint_edit.setPlaceholderText("Endpoint path (e.g. /users)")
        layout.addWidget(QLabel("Endpoint:"))
        layout.addWidget(self.api_endpoint_edit)

        self.api_method_combo = QComboBox()
        self.api_method_combo.addItems(["GET", "POST", "PUT", "PATCH", "DELETE"])
        layout.addWidget(QLabel("HTTP Method:"))
        layout.addWidget(self.api_method_combo)

        self.api_headers_edit = QTextEdit()
        self.api_headers_edit.setPlaceholderText("Header-Name: value\nAuthorization: Bearer ...")
        self.api_headers_edit.setFixedHeight(80)
        layout.addWidget(QLabel("Headers (one per line):"))
        layout.addWidget(self.api_headers_edit)

        self.api_params_edit = QTextEdit()
        self.api_params_edit.setPlaceholderText("param1=value1\nparam2=value2")
        self.api_params_edit.setFixedHeight(80)
        layout.addWidget(QLabel("Query Parameters (one per line):"))
        layout.addWidget(self.api_params_edit)

        self.api_body_edit = QTextEdit()
        self.api_body_edit.setPlaceholderText('{"key": "value"}')
        self.api_body_edit.setFixedHeight(120)
        layout.addWidget(QLabel("JSON Body (optional):"))
        layout.addWidget(self.api_body_edit)

        self.api_test_name_edit = QLineEdit("test_api_request")
        layout.addWidget(QLabel("Pytest Function Name:"))
        layout.addWidget(self.api_test_name_edit)

        generate_btn = QPushButton("Generate API Test")
        generate_btn.clicked.connect(self.on_generate_api_test)
        layout.addWidget(generate_btn)

        save_btn = QPushButton("Save API Test File")
        save_btn.clicked.connect(self.on_save_api_test_file)
        layout.addWidget(save_btn)

        layout.addStretch()
        self.tabs.addTab(tab, "API")

    def _parse_key_value_text(self, text):
        data = {}
        for line in text.splitlines():
            if not line.strip():
                continue
            if ':' in line:
                key, value = line.split(':', 1)
            elif '=' in line:
                key, value = line.split('=', 1)
            else:
                continue
            data[key.strip()] = value.strip()
        return data

    def _format_dict_literal(self, data):
        if not data:
            return "{}"
        import json
        return json.dumps(data, indent=4)

    def _build_api_test_snippet(
        self,
        url,
        method,
        headers,
        params,
        body,
        test_name,
    ):
        import json

        lines = [
            "import json",
            "import urllib.request",
            "import urllib.parse",
            "",
            f"def {test_name}():",
            f"    url = \"{url}\"",
        ]

        if params:
            lines += [
                f"    params = {json.dumps(params, indent=4)}",
                "    query = urllib.parse.urlencode(params)",
                "    url = url + '?' + query",
            ]

        if headers:
            lines.append(f"    headers = {json.dumps(headers, indent=4)}")
        else:
            lines.append("    headers = {}")

        if body is not None:
            lines += [
                f"    body = json.dumps({json.dumps(body, indent=4)})",
                "    data = body.encode('utf-8')",
            ]
        else:
            lines.append("    data = None")

        request_args = ["url", "headers=headers", f"method=\"{method}\"" ]
        if body is not None:
            request_args.append("data=data")

        lines += [
            f"    req = urllib.request.Request({', '.join(request_args)})",
            "    with urllib.request.urlopen(req) as response:",
            "        assert response.status == 200",
            "        raw = response.read().decode('utf-8')",
            "        if raw:",
            "            try:",
            "                data = json.loads(raw)",
            "            except ValueError:",
            "                data = raw",
            "            assert data is not None",
        ]

        return '\n'.join(lines)

    def _collect_api_test_data(self):
        base_url = self.api_base_url_edit.text().strip()
        endpoint = self.api_endpoint_edit.text().strip()
        method = self.api_method_combo.currentText()
        test_name = self.api_test_name_edit.text().strip() or "test_api_request"

        if not base_url or not endpoint:
            QMessageBox.warning(self, "API Test Generator", "Please enter both Base URL and Endpoint.")
            return None

        if endpoint.startswith("/"):
            endpoint = endpoint[1:]

        url = base_url.rstrip("/") + "/" + endpoint
        headers = self._parse_key_value_text(self.api_headers_edit.toPlainText())
        params = self._parse_key_value_text(self.api_params_edit.toPlainText())

        body_text = self.api_body_edit.toPlainText().strip()
        body = None
        if body_text:
            try:
                import json
                body = json.loads(body_text)
            except Exception:
                QMessageBox.warning(self, "API Test Generator", "JSON Body is invalid. Please enter valid JSON.")
                return None

        return {
            "url": url,
            "method": method,
            "headers": headers,
            "params": params,
            "body": body,
            "test_name": test_name,
        }

    def _safe_test_file_name(self, test_name):
        import re
        safe_name = re.sub(r"[^0-9a-zA-Z_]+", "_", test_name.strip())
        if not safe_name:
            safe_name = "test_api_request"
        if not safe_name.startswith("test_"):
            safe_name = f"test_{safe_name}"
        return safe_name + ".py"

    def _get_project_dir(self):
        if self.parent() is not None and hasattr(self.parent(), "project_dir"):
            return getattr(self.parent(), "project_dir")
        return None

    def on_generate_api_test(self):
        data = self._collect_api_test_data()
        if data is None:
            return

        snippet = self._build_api_test_snippet(**data)
        self.insert_code(snippet)
        QMessageBox.information(self, "API Test Generated", "API test template inserted into the editor.")

    def on_save_api_test_file(self):
        data = self._collect_api_test_data()
        if data is None:
            return

        project_dir = self._get_project_dir()
        if not project_dir:
            QMessageBox.warning(self, "API Test Generator", "Unable to determine project directory. Save failed.")
            return

        tests_dir = os.path.join(project_dir, "tests")
        os.makedirs(tests_dir, exist_ok=True)
        init_file = os.path.join(tests_dir, "__init__.py")
        if not os.path.exists(init_file):
            open(init_file, "w", encoding="utf-8").close()

        file_name = self._safe_test_file_name(data["test_name"])
        file_path = os.path.join(tests_dir, file_name)

        if os.path.exists(file_path):
            result = QMessageBox.question(
                self,
                "Overwrite Test File?",
                f"The file {file_name} already exists. Overwrite?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if result != QMessageBox.StandardButton.Yes:
                return

        snippet = self._build_api_test_snippet(**data)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(snippet + "\n")
            QMessageBox.information(self, "API Test Saved", f"API test saved to {file_path}")
        except Exception as exc:
            QMessageBox.critical(self, "Save Failed", f"Could not save API test file: {exc}")

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
