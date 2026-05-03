from PyQt6.QtWidgets import (
    QMainWindow, QDockWidget, QTextEdit, QTreeView, 
    QLabel, QToolBar, QStatusBar, QFileDialog, QMessageBox
)
from PyQt6.QtGui import QFileSystemModel
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
        self.explorer_dock.setWidget(self.file_tree)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.explorer_dock)

        # Right Dock: Image Preview
        self.preview_dock = QDockWidget("Image Preview", self)
        self.preview_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.preview_label = QLabel("No image selected.")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #1E1E1E; color: #888888; border: none;")
        self.preview_dock.setWidget(self.preview_label)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.preview_dock)

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
            self.load_file(file_path)

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
