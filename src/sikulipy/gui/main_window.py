from PyQt6.QtWidgets import (
    QMainWindow, QDockWidget, QTextEdit, QTreeView, 
    QLabel, QToolBar, QStatusBar, QFileDialog, QMessageBox,
    QWidget, QVBoxLayout, QListWidget
)
from PyQt6.QtGui import QFileSystemModel, QPixmap
from PyQt6.QtCore import Qt
from sikulipy.gui.editor import PythonEditor
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
        
        self.toolbar.addAction("▶ Run")
        self.toolbar.addAction("⏹ Stop")
        self.toolbar.addSeparator()
        self.toolbar.addAction("📷 Capture Screen")
        self.toolbar.addAction("✂ Capture Region")
        self.toolbar.addSeparator()
        self.toolbar.addAction("📱 Device")
        self.toolbar.addAction("⏺ Record")
        self.toolbar.addSeparator()
        docs_action = self.toolbar.addAction("📚 Docs")
        docs_action.triggered.connect(self.open_docs)

        # Status Bar
        self.setStatusBar(QStatusBar())
        self.statusBar().setStyleSheet("background-color: #007ACC; color: white;")
        self.statusBar().showMessage("Ready")

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
