from PyQt6.QtWidgets import (
    QMainWindow, QDockWidget, QTextEdit, QTreeView, 
    QLabel, QToolBar, QStatusBar
)
from PyQt6.QtCore import Qt
from sikulipy.gui.editor import PythonEditor

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

        self.setup_ui()

    def setup_ui(self):
        # Center Widget: Editor
        self.editor = PythonEditor()
        self.setCentralWidget(self.editor)

        # Left Dock: Explorer
        self.explorer_dock = QDockWidget("Project Explorer", self)
        self.explorer_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        self.file_tree = QTreeView()
        self.file_tree.setStyleSheet("background-color: #252526; color: #CCCCCC; border: none;")
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

    def open_docs(self):
        from PyQt6.QtGui import QDesktopServices
        from PyQt6.QtCore import QUrl
        QDesktopServices.openUrl(QUrl("https://sikulix-2014.readthedocs.io/en/latest/"))
