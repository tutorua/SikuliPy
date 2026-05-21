"""Device stream widget scaffold — shows a video canvas and control toolbar."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QToolBar, QLabel, QHBoxLayout
from PyQt6.QtGui import QIcon, QPixmap, QAction
from PyQt6.QtCore import Qt


class DeviceStreamWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Device Stream')
        layout = QVBoxLayout(self)

        # Toolbar
        toolbar = QToolBar()
        self.screenshot_action = QAction('Screenshot', self)
        self.stop_action = QAction('Stop', self)
        toolbar.addAction(self.screenshot_action)
        toolbar.addAction(self.stop_action)
        layout.addWidget(toolbar)

        # Canvas placeholder
        self.canvas = QLabel('No stream')
        self.canvas.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.canvas.setStyleSheet('background: #111; color: #DDD;')
        layout.addWidget(self.canvas, 1)

        # status
        status = QHBoxLayout()
        self.info_label = QLabel('Resolution: -')
        status.addWidget(self.info_label)
        layout.addLayout(status)

        # signals and state
        self._bridge = None

    def attach_bridge(self, bridge):
        """Attach a bridge (e.g., AndroidBridge) to receive frames and control events."""
        if self._bridge:
            try:
                self._bridge.frameReady.disconnect(self._on_frame)
            except Exception:
                pass
        self._bridge = bridge
        if bridge:
            try:
                bridge.frameReady.connect(self._on_frame)
            except Exception:
                pass

    def _on_frame(self, pixmap):
        """Receive a QPixmap/QImage and display it on the canvas."""
        try:
            if hasattr(pixmap, 'isNull') and pixmap.isNull():
                return
            if hasattr(pixmap, 'toImage'):
                qpix = QPixmap.fromImage(pixmap.toImage())
            else:
                qpix = pixmap
            self.canvas.setPixmap(qpix.scaled(self.canvas.size(), Qt.AspectRatioMode.KeepAspectRatio))
        except Exception:
            pass
