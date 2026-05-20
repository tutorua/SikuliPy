from PyQt6.QtWidgets import QWidget, QInputDialog
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt, QRect, QPoint
from PyQt6 import QtGui

class OverlayWidget(QWidget):
    """A full-screen overlay used for screen and region capture.

    Modes: 'screen' or 'region'
    """
    def __init__(self, mode='screen', parent=None):
        super().__init__(parent)
        self.mode = mode
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)
        self.start = None
        self.end = None
        self.selecting = False
        self.on_captured = None

        # cover virtual geometry
        screen = QtGui.QGuiApplication.primaryScreen()
        geom = QtGui.QGuiApplication.primaryScreen().virtualGeometry()
        self.setGeometry(geom)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # dim whole desktop
        painter.fillRect(self.rect(), QColor(0, 0, 0, 160))

        if self.mode == 'region' and self.start and self.end:
            r = QRect(self.mapFromGlobal(self.start), self.mapFromGlobal(self.end)).normalized()
            # clear selection area (draw transparent rect)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(r, QColor(0, 0, 0, 0))
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            pen = QPen(QColor(180, 180, 180), 2)
            painter.setPen(pen)
            painter.drawRect(r)

    def mousePressEvent(self, event):
        global_pos = self.mapToGlobal(event.position().toPoint())
        if self.mode == 'screen':
            # capture full screen containing this point
            self.capture_screen_at(global_pos)
        else:
            self.start = global_pos
            self.end = global_pos
            self.selecting = True
            self.update()

    def mouseMoveEvent(self, event):
        if self.mode == 'region' and self.selecting:
            self.end = self.mapToGlobal(event.position().toPoint())
            self.update()

    def mouseReleaseEvent(self, event):
        if self.mode == 'region' and self.selecting:
            self.end = self.mapToGlobal(event.position().toPoint())
            self.selecting = False
            self.update()
            self.capture_region()

    def capture_screen_at(self, global_pos):
        screen = QtGui.QGuiApplication.screenAt(global_pos)
        if not screen:
            screen = QtGui.QGuiApplication.primaryScreen()
        pix = screen.grabWindow(0)
        # call callback if present, then close
        if callable(self.on_captured):
            try:
                self.on_captured(pix)
            except Exception:
                pass
        self.close()

    def capture_region(self):
        if not (self.start and self.end):
            return
        r = QRect(self.start, self.end).normalized()
        screen = QtGui.QGuiApplication.screenAt(self.start)
        if not screen:
            screen = QtGui.QGuiApplication.primaryScreen()
        # grab full screen then copy region in global coordinates
        pix = screen.grabWindow(0)
        # map global rect to screen-local by subtracting screen geometry
        sg = screen.geometry()
        local_rect = QRect(r.left() - sg.left(), r.top() - sg.top(), r.width(), r.height())
        cropped = pix.copy(local_rect)
        if callable(self.on_captured):
            try:
                self.on_captured(cropped)
            except Exception:
                pass
        self.close()
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QRect, pyqtSignal, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen

class RegionCaptureOverlay(QWidget):
    captureComplete = pyqtSignal(QRect)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.ToolTip)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.CrossCursor)

        screen = QApplication.primaryScreen()
        self.setGeometry(screen.geometry())

        self.start_point = QPoint()
        self.end_point = QPoint()
        self.is_drawing = False

    def paintEvent(self, event):
        painter = QPainter(self)
        # Draw a semi-transparent dark background
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))

        if self.is_drawing:
            # Clear the selected area
            selection_rect = QRect(self.start_point, self.end_point).normalized()
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(selection_rect, Qt.GlobalColor.transparent)

            # Draw a border around the selection
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            pen = QPen(QColor(255, 0, 0))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawRect(selection_rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_point = event.pos()
            self.end_point = self.start_point
            self.is_drawing = True
            self.update()

    def mouseMoveEvent(self, event):
        if self.is_drawing:
            self.end_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_drawing:
            self.end_point = event.pos()
            self.is_drawing = False
            self.update()
            
            selection_rect = QRect(self.start_point, self.end_point).normalized()
            if selection_rect.width() > 0 and selection_rect.height() > 0:
                self.captureComplete.emit(selection_rect)
            
            self.close()
            
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
