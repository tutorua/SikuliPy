from PyQt6.QtWidgets import (
    QMainWindow, QDockWidget, QTextEdit, QTreeView, 
    QLabel, QToolBar, QStatusBar, QFileDialog, QMessageBox,
    QWidget, QVBoxLayout, QListWidget
)
from PyQt6.QtGui import QFileSystemModel, QPixmap
from PyQt6.QtCore import Qt, QProcess
from sikulipy.gui.editor import PythonEditor
from sikulipy.gui.overlay import RegionCaptureOverlay
from sikulipy.vision import VisionEngine
from sikulipy.gui.recorder import RecorderDialog
from sikulipy.gui.web_inspector import WebInspectorWorker, WebInspectorCanvas, WebInspectorPane
import os

class SikuliPyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SikuliPy - Visual Testing IDE")
        self.resize(1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2D2D2D;
            }
            QDockWidget {
                color: #CCCCCC;
                font-weight: bold;
            }
            QDockWidget::title {
                background: #3C3C3C;
                padding-left: 5px;
                padding-top: 4px;
                padding-bottom: 4px;
            }
        """)

        self.current_file = None
        self.file_model = None
        self.project_dir = os.getcwd()

        self.setup_ui()
        self.setup_menu()

    def setup_ui(self):
        # Center Widget: Editor
        self.editor = PythonEditor()
        self.setCentralWidget(self.editor)

        # Left Dock: Explorer
        self.explorer_dock = QDockWidget("Project Explorer", self)
        self.explorer_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        self.file_tree = QTreeView()
        self.file_tree.setStyleSheet("background-color: #252526; color: #CCCCCC; border: none;")
        self.file_tree.doubleClicked.connect(self.on_tree_double_click)
        self.file_tree.clicked.connect(self.on_tree_clicked)
        self.explorer_dock.setWidget(self.file_tree)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.explorer_dock)

        # Right Dock: Image Preview
        self.preview_dock = QDockWidget("Image Preview", self)
        self.preview_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        
        self.preview_widget = QWidget()
        self.preview_layout = QVBoxLayout(self.preview_widget)
        self.preview_layout.setContentsMargins(0, 0, 0, 0)
        self.preview_layout.setSpacing(0)
        
        self.image_list = QListWidget()
        self.image_list.setStyleSheet("background-color: #252526; color: #CCCCCC; border: none; padding: 5px;")
        self.image_list.itemClicked.connect(self.on_image_list_clicked)
        
        self.preview_label = QLabel("No image selected.")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #1E1E1E; color: #888888; border: none;")
        self.preview_label.setMinimumHeight(200)
        
        self.preview_layout.addWidget(self.image_list)
        self.preview_layout.addWidget(self.preview_label)
        
        self.preview_dock.setWidget(self.preview_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.preview_dock)

        # Connect editor signals
        self.editor.textChanged.connect(self.update_image_list)
        self.editor.cursorPositionChanged.connect(self.on_cursor_position_changed)

        # Bottom Dock: Console
        self.console_dock = QDockWidget("Console Output", self)
        self.console_dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)
        self.console_text = QTextEdit()
        self.console_text.setReadOnly(True)
        self.console_text.setStyleSheet("background-color: #1E1E1E; color: #CCCCCC; border: none; font-family: Consolas; padding: 5px;")
        self.console_text.append("[System] SikuliPy initialized successfully...")
        self.console_dock.setWidget(self.console_text)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.console_dock)

        # Toolbar
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setStyleSheet("background-color: #3C3C3C; color: white; border: none; padding: 2px;")
        self.addToolBar(self.toolbar)
        
        new_btn = self.toolbar.addAction("📄 New")
        new_btn.triggered.connect(self.new_file)
        open_btn = self.toolbar.addAction("📂 Open")
        open_btn.triggered.connect(self.open_folder)
        save_btn = self.toolbar.addAction("💾 Save")
        save_btn.triggered.connect(self.save_file)
        self.toolbar.addSeparator()
        
        self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        self.run_icon_green = self.create_text_icon("▶", "#4CAF50")
        self.run_icon_gray = self.create_text_icon("▶", "#808080")
        self.stop_icon_green = self.create_text_icon("⏹", "#4CAF50")
        self.stop_icon_gray = self.create_text_icon("⏹", "#808080")
        
        self.run_action = self.toolbar.addAction(self.run_icon_green, "Run")
        self.run_action.triggered.connect(self.run_script)
        self.stop_action = self.toolbar.addAction(self.stop_icon_gray, "Stop")
        self.stop_action.triggered.connect(self.stop_script)
        self.stop_action.setEnabled(False)
        self.toolbar.addSeparator()
        self.toolbar.addAction("📷 Capture Screen")
        self.capture_action = self.toolbar.addAction("✂ Capture Region")
        self.capture_action.triggered.connect(self.start_region_capture)
        self.toolbar.addSeparator()
        self.toolbar.addAction("📱 Device")
        self.record_action = self.toolbar.addAction("⏺ Record")
        self.record_action.triggered.connect(self.open_recorder)
        self.toolbar.addSeparator()
        docs_action = self.toolbar.addAction("📚 Docs")
        docs_action.triggered.connect(self.open_docs)

        # Status Bar
        self.setStatusBar(QStatusBar())
        self.statusBar().setStyleSheet("background-color: #007ACC; color: white;")
        self.statusBar().showMessage("Ready")

    def open_recorder(self):
        if not hasattr(self, 'recorder_dialog') or not self.recorder_dialog.isVisible():
            self.recorder_dialog = RecorderDialog(self.editor, self)
            self.recorder_dialog.imageActionRequested.connect(self.on_recorder_image_action)
            self.recorder_dialog.webAutoRequested.connect(self.on_web_auto_requested)
            self.recorder_dialog.show()

    def create_text_icon(self, text, color_name):
        from PyQt6.QtGui import QPixmap, QPainter, QColor, QIcon
        from PyQt6.QtCore import Qt
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QColor(color_name))
        font = painter.font()
        font.setPixelSize(18)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, text)
        painter.end()
        return QIcon(pixmap)

    def setup_menu(self):
        menubar = self.menuBar()
        menubar.setStyleSheet("background-color: #3C3C3C; color: white;")
        
        file_menu = menubar.addMenu("File")
        
        new_action = file_menu.addAction("New")
        new_action.triggered.connect(self.new_file)
        
        open_action = file_menu.addAction("Open")
        open_action.triggered.connect(self.open_folder)
        
        save_action = file_menu.addAction("Save")
        save_action.triggered.connect(self.save_file)

    def new_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Create New File", "", "Python Files (*.py);;All Files (*)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("")
                self.editor.setPlainText("")
                self.current_file = file_path
                self.preview_label.clear()
                self.preview_label.setText("No image selected.")
                self.console_text.append(f"[System] Created new file: {file_path}")
                self.statusBar().showMessage(f"Editing: {os.path.basename(file_path)}")
            except Exception as e:
                self.console_text.append(f"[Error] Could not create file: {e}")

    def open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if folder:
            self.file_model = QFileSystemModel()
            self.file_model.setRootPath(folder)
            self.file_tree.setModel(self.file_model)
            self.file_tree.setRootIndex(self.file_model.index(folder))
            self.project_dir = folder
            # Hide some columns for better view (size, type, date modified)
            for i in range(1, 4):
                self.file_tree.hideColumn(i)
            self.console_text.append(f"[System] Opened folder: {folder}")

    def save_file(self):
        if self.current_file:
            try:
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    f.write(self.editor.toPlainText())
                self.console_text.append(f"[System] Saved file: {self.current_file}")
                self.statusBar().showMessage(f"Saved: {os.path.basename(self.current_file)}", 3000)
            except Exception as e:
                self.console_text.append(f"[Error] Could not save file: {e}")
        else:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Python Files (*.py);;All Files (*)")
            if file_path:
                self.current_file = file_path
                self.save_file()

    def on_tree_double_click(self, index):
        if not self.file_model:
            return
        file_path = self.file_model.filePath(index)
        if not self.file_model.isDir(index):
            # Only open text/python files in editor, not images
            if not file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                self.load_file(file_path)

    def on_tree_clicked(self, index):
        if not self.file_model:
            return
        file_path = self.file_model.filePath(index)
        if not self.file_model.isDir(index):
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                self.display_image_path(file_path)

    def load_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.editor.setPlainText(content)
            self.current_file = file_path
            self.preview_label.clear()
            self.preview_label.setText("No image selected.")
            self.console_text.append(f"[System] Opened file: {file_path}")
            self.statusBar().showMessage(f"Editing: {os.path.basename(file_path)}")
        except Exception as e:
            self.console_text.append(f"[Error] Could not open file: {e}")

    def open_docs(self):
        from PyQt6.QtGui import QDesktopServices
        from PyQt6.QtCore import QUrl
        QDesktopServices.openUrl(QUrl("https://sikulix-2014.readthedocs.io/en/latest/"))

    def update_image_list(self):
        import re
        text = self.editor.toPlainText()
        # Find strings ending with common image extensions
        matches = re.findall(r'["\']([^"\']+\.(?:png|jpg|jpeg))["\']', text, re.IGNORECASE)
        # Unique list preserving order
        images = list(dict.fromkeys(matches))
        
        # Only update if changed to avoid unnecessary clears/flashes
        current_items = [self.image_list.item(i).text() for i in range(self.image_list.count())]
        if current_items != images:
            self.image_list.clear()
            for img in images:
                self.image_list.addItem(img)

    def on_image_list_clicked(self, item):
        self.display_image(item.text())

    def display_image(self, image_name):
        if not self.current_file:
            return
        import os
        base_dir = os.path.dirname(self.current_file)
        img_path = os.path.join(base_dir, image_name)
        self.display_image_path(img_path, image_name)

    def display_image_path(self, img_path, display_name=None):
        import os
        display_name = display_name or os.path.basename(img_path)
        if os.path.exists(img_path):
            pixmap = QPixmap(img_path)
            # Scale down if it's too large, but keep aspect ratio
            scaled_pixmap = pixmap.scaled(self.preview_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.preview_label.setPixmap(scaled_pixmap)
        else:
            self.preview_label.clear()
            self.preview_label.setText(f"Image not found:\n{display_name}")

    def run_script(self):
        if not self.current_file:
            self.console_text.append("[Error] No file is currently open to run.")
            return
            
        self.save_file()
        
        self.run_action.setIcon(self.run_icon_gray)
        self.run_action.setEnabled(False)
        self.stop_action.setIcon(self.stop_icon_green)
        self.stop_action.setEnabled(True)
        self.statusBar().showMessage("Running...")
        
        self.console_text.append(f"\n[System] Starting script: {self.current_file}")
        
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)
        
        import sys
        # Use current python executable to run the script
        self.process.start(sys.executable, ["-u", self.current_file])

    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode('utf-8', errors='replace')
        self.console_text.insertPlainText(data)
        self.console_text.ensureCursorVisible()

    def handle_stderr(self):
        data = self.process.readAllStandardError().data().decode('utf-8', errors='replace')
        self.console_text.insertPlainText(data)
        self.console_text.ensureCursorVisible()

    def stop_script(self):
        if hasattr(self, 'process') and self.process and self.process.state() == QProcess.ProcessState.Running:
            self.console_text.append("[System] Terminating script...")
            self.process.kill()

    def process_finished(self, exitCode, exitStatus):
        self.run_action.setIcon(self.run_icon_green)
        self.run_action.setEnabled(True)
        self.stop_action.setIcon(self.stop_icon_gray)
        self.stop_action.setEnabled(False)
        self.statusBar().showMessage(f"Ready (Exit code {exitCode})")
        self.console_text.append(f"[System] Script finished with exit code {exitCode}")
        self.process = None

    def on_cursor_position_changed(self):
        import re
        cursor = self.editor.textCursor()
        line_text = cursor.block().text()
        pos_in_line = cursor.positionInBlock()
        
        for match in re.finditer(r'["\']([^"\']+\.(?:png|jpg|jpeg))["\']', line_text, re.IGNORECASE):
            if match.start() <= pos_in_line <= match.end():
                image_name = match.group(1)
                items = self.image_list.findItems(image_name, Qt.MatchFlag.MatchExactly)
                if items:
                    self.image_list.setCurrentItem(items[0])
                    self.display_image(image_name)
                break

    def start_region_capture(self, callback=None):
        self.overlay = RegionCaptureOverlay()
        if callback:
            self.overlay.captureComplete.connect(callback)
        else:
            self.overlay.captureComplete.connect(self.on_region_captured_for_ocr)
        self.overlay.show()

    def on_region_captured_for_ocr(self, rect):
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QByteArray, QBuffer, QIODevice
        import numpy as np
        import cv2

        screen = QApplication.primaryScreen()
        # Grab the specified region from the screen
        pixmap = screen.grabWindow(0, rect.x(), rect.y(), rect.width(), rect.height())
        
        # Convert QPixmap to numpy array by saving to a memory buffer as PNG
        byte_array = QByteArray()
        buffer = QBuffer(byte_array)
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        pixmap.save(buffer, "PNG")
        buffer.close()
        
        img_np = np.frombuffer(byte_array.data(), dtype=np.uint8)
        arr_bgr = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
        
        self.console_text.append(f"\n[System] Captured region {rect.x()}, {rect.y()}, {rect.width()}x{rect.height()}. Running OCR...")
        from PyQt6.QtWidgets import QApplication
        QApplication.processEvents() # Force UI update
        
        try:
            text = VisionEngine.extract_text(arr_bgr)
            self.console_text.append(f"[OCR Result]\n{text}\n{'-'*20}")
        except Exception as e:
            self.console_text.append(f"[Error] OCR failed: {e}")

    def on_recorder_image_action(self, action_name):
        self.recorder_dialog.hide() # Temporarily hide recorder
        
        def callback(rect):
            from PyQt6.QtWidgets import QApplication
            import os
            import time
            
            screen = QApplication.primaryScreen()
            pixmap = screen.grabWindow(0, rect.x(), rect.y(), rect.width(), rect.height())
            
            assets_dir = os.path.join(self.project_dir, "assets")
            if not os.path.exists(assets_dir):
                os.makedirs(assets_dir)
                
            filename = f"img_{int(time.time())}.png"
            filepath = os.path.join(assets_dir, filename)
            pixmap.save(filepath, "PNG")
            
            action_map = {
                "Click": "click", "DblClick": "dbl_click", "RClick": "rclick",
                "Wait": "wait", "WaitVanish": "wait_vanish", "WaitAppear": "wait_appear",
                "Drag&Drop": "drag_drop", "Swipe": "swipe"
            }
            func_name = action_map.get(action_name, action_name.lower())
            rel_path = f"assets/{filename}"
            code_str = f'{func_name}("{rel_path}")'
            
            cursor = self.editor.textCursor()
            cursor.insertText(code_str + "\n")
            self.editor.setTextCursor(cursor)
            self.editor.setFocus()
            self.console_text.append(f"[System] Captured and saved {rel_path}")
            
            self.recorder_dialog.show() # Restore recorder
            
        self.start_region_capture(callback)

    def on_web_auto_requested(self, url):
        self.console_text.append(f"[System] Starting Playwright Web Inspector for {url}...")
        self.web_inspector_url = url   # store for POM generation
        self.recorder_dialog.hide()
        
        self.web_worker = WebInspectorWorker(url)
        self.web_worker.finished_capture.connect(self.on_web_capture_finished)
        self.web_worker.error.connect(lambda e: self.console_text.append(f"[Error] Web Inspector: {e}"))
        self.web_worker.start()

    def on_web_capture_finished(self, pixmap, elements):
        self.console_text.append("[System] Web Inspector capture complete.")
        
        if not hasattr(self, 'original_central_widget') or self.original_central_widget is None:
            self.original_central_widget = self.takeCentralWidget()
        else:
            old = self.takeCentralWidget()
            if old and old != self.original_central_widget:
                old.deleteLater()
        
        self.web_canvas = WebInspectorCanvas()
        self.web_canvas.set_image(pixmap)
        self.all_web_elements = elements
        # Don't draw elements until user clicks Apply with selected filters
        
        self.setCentralWidget(self.web_canvas)
        self.explorer_dock.hide()
        
        self.web_pane = WebInspectorPane()
        # Start with an empty list to match the unmarked checkboxes
        self.web_pane.update_list([])
        
        self.web_pane.applyFilters.connect(self.on_web_pane_apply_filters)
        self.web_pane.closeInspector.connect(self.on_web_pane_close)
        self.web_pane.listItemSelected.connect(self.web_canvas.select_element_by_id)
        self.web_pane.takeScreenshot.connect(self.on_web_take_screenshot)
        
        self.web_canvas.elementClicked.connect(lambda el: self.web_pane.select_list_item(el['id']))
        self.web_canvas.elementClicked.connect(lambda el: self.web_pane.set_preview_image(self.web_canvas.get_selected_pixmap()))
        
        self.preview_dock.setWidget(self.web_pane)
        self.preview_dock.setWindowTitle("Web Inspector")

    def on_web_pane_apply_filters(self, active_categories):
        filtered_els = [el for el in self.all_web_elements if el['category'] in active_categories]
        self.console_text.append(f"[System] Applied filters: {active_categories}. Found {len(filtered_els)} elements.")
        self.web_canvas.draw_elements(filtered_els)
        self.web_pane.update_list(filtered_els)

    def on_web_pane_close(self):
        old = self.takeCentralWidget()
        if old:
            old.deleteLater()
        if hasattr(self, 'original_central_widget') and self.original_central_widget is not None:
            self.setCentralWidget(self.original_central_widget)
            self.original_central_widget = None
            
        self.explorer_dock.show()
        self.preview_dock.setWidget(self.preview_widget)
        self.preview_dock.setWindowTitle("Image Preview")
        self.recorder_dialog.show()
        
    def on_web_take_screenshot(self):
        if not self.web_canvas or not self.web_pane:
            self.console_text.append("[Error] Web Inspector components not found.")
            return

        import os, time, re
        from urllib.parse import urlparse

        update_mode = self.web_pane.rb_update.isChecked()
        timestamp = int(time.time())
        count = 0
        captured_elements = []   # will carry '_asset_path' for codegen

        # ---- derive a page name from the URL ----
        url = getattr(self, 'web_inspector_url', 'page')
        parsed = urlparse(url)
        raw = parsed.netloc.replace('www.', '') + parsed.path
        page_name = re.sub(r'[^a-z0-9]+', '_', raw.lower()).strip('_') or 'page'

        for i in range(self.web_pane.list_widget.count()):
            item = self.web_pane.list_widget.item(i)
            if item.checkState() != Qt.CheckState.Checked:
                continue

            el_id = item.data(Qt.ItemDataRole.UserRole)
            category = item.data(Qt.ItemDataRole.UserRole + 1)

            rect_item = next(
                (r for r in self.web_canvas.rect_items if r.element_data['id'] == el_id),
                None
            )
            if not rect_item:
                continue

            rect = rect_item.rect()
            el_pixmap = self.web_canvas.full_pixmap.copy(
                int(rect.x()), int(rect.y()), int(rect.width()), int(rect.height())
            )

            el_data = rect_item.element_data
            source_text = el_data['text'] if el_data['text'] else el_data.get('ariaLabel', '')
            safe_text = ''.join(
                c for c in source_text if c.isalnum() or c in (' ', '_', '-')
            ).strip()[:20].replace(' ', '_')
            if not safe_text:
                safe_text = f'el_{i}'

            cat_dir = os.path.join(self.project_dir, 'assets', category)
            os.makedirs(cat_dir, exist_ok=True)

            if update_mode:
                # In Update Baseline mode: no timestamp → overwrites existing baseline
                filename = f'{safe_text}_{i}.png'
            else:
                filename = f'{safe_text}_{timestamp}_{i}.png'

            filepath = os.path.join(cat_dir, filename)
            el_pixmap.save(filepath, 'PNG')
            count += 1

            rel_path = f'assets/{category}/{filename}'
            el_data['_asset_path'] = rel_path
            captured_elements.append(el_data)

            # Insert click snippet if this is the currently selected element
            if (not update_mode and self.web_canvas.selected_rect
                    and self.web_canvas.selected_rect.element_data['id'] == el_id):
                code_str = f'click("{rel_path}")'
                cursor = self.editor.textCursor()
                cursor.insertText(code_str + '\n')
                self.editor.setTextCursor(cursor)
                self.console_text.append(f'[System] Inserted click action: {rel_path}')

        self.console_text.append(
            f'[System] Saved {count} element(s) into assets/ category subfolders.'
        )

        # ---- Generate Tests mode: run POM + test file generators ----
        if not update_mode and captured_elements:
            try:
                from sikulipy.codegen.pom_generator import generate_page_object
                from sikulipy.codegen.test_generator import generate_test_file

                pom_path = generate_page_object(
                    project_dir=self.project_dir,
                    page_name=page_name,
                    url=url,
                    elements=captured_elements,
                )
                test_path = generate_test_file(
                    project_dir=self.project_dir,
                    page_name=page_name,
                    url=url,
                    elements=captured_elements,
                )

                # Write sikulipy_config.py at project root if it doesn't exist
                config_dest = os.path.join(self.project_dir, 'sikulipy_config.py')
                if not os.path.exists(config_dest):
                    import shutil, inspect
                    from sikulipy.codegen import config_template
                    shutil.copy(inspect.getfile(config_template), config_dest)
                    self.console_text.append(f'[System] Created config: {config_dest}')

                # Copy the testing helpers library into the project so tests are self-contained
                import shutil, inspect
                import sikulipy.testing as _testing_module
                testing_src = inspect.getfile(_testing_module)
                testing_dest = os.path.join(self.project_dir, 'sikulipy_testing.py')
                shutil.copy(testing_src, testing_dest)
                self.console_text.append(f'[System] Copied testing helpers → {testing_dest}')

                self.console_text.append(f'[System] Page Object  → {pom_path}')
                self.console_text.append(f'[System] Test file    → {test_path}')
                self.console_text.append(
                    f'[System] Run tests with: pytest {os.path.relpath(test_path, self.project_dir)} -v'
                )

            except Exception as e:
                self.console_text.append(f'[Error] Code generation failed: {e}')
        elif update_mode:
            self.console_text.append('[System] Update Baseline mode — test files were NOT regenerated.')
