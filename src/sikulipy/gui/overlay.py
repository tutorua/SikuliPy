from PyQt6.QtWidgets import QWidget, QInputDialog
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt, QRect, QPoint, QTimer
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
        # don't set WA_NoSystemBackground; keep translucent background only
        # For screen mode we want overlay to be click-through so underlying apps remain interactive
        if self.mode == 'screen':
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        self.start = None
        self.end = None
        self.selecting = False
        self.on_captured = None
        self.target_rect = None

        # cover virtual geometry
        # compute virtual desktop geometry across all screens so overlay covers multi-monitor setups
        try:
            screens = QtGui.QGuiApplication.screens()
            if screens:
                left = min(s.geometry().left() for s in screens)
                top = min(s.geometry().top() for s in screens)
                right = max(s.geometry().right() for s in screens)
                bottom = max(s.geometry().bottom() for s in screens)
                geom = QRect(QPoint(left, top), QPoint(right, bottom))
            else:
                geom = QtGui.QGuiApplication.primaryScreen().geometry()
        except Exception:
            geom = QtGui.QGuiApplication.primaryScreen().geometry()
        self.setGeometry(geom)

        if self.mode == 'region':
            self.setCursor(Qt.CursorShape.CrossCursor)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # If in screen mode and a target rect was provided, dim only that window area.
        if self.mode == 'screen' and self.target_rect:
            try:
                # convert global rect to overlay-local
                r = QRect(self.mapFromGlobal(self.target_rect.topLeft()), self.mapFromGlobal(self.target_rect.bottomRight())).normalized()
                painter.fillRect(r, QColor(0, 0, 0, 160))
            except Exception:
                pass
        if self.mode == 'region':
            # dim the entire overlay first
            painter.fillRect(self.rect(), QColor(0, 0, 0, 120))
            if self.start and self.end:
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
            # hide overlay first and delay actual grab so it's not visible in the screenshot
            self.hide()
            QTimer.singleShot(80, lambda: self.capture_screen_at(global_pos))
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
        # If a target rect is provided (foreground window), crop to that rect so only the dimmed window is captured
        try:
            if hasattr(self, 'target_rect') and self.target_rect is not None:
                sg = screen.geometry()
                tr = self.target_rect
                local_rect = QRect(tr.left() - sg.left(), tr.top() - sg.top(), tr.width(), tr.height())
                pix = pix.copy(local_rect)
        except Exception:
            pass
        # call callback if present, then close
        if callable(self.on_captured):
            try:
                self.on_captured(pix)
            except Exception:
                pass
        try:
            self.close()
        except Exception:
            pass

    def capture_region(self):
        if not (self.start and self.end):
            return
        r = QRect(self.start, self.end).normalized()
        screen = QtGui.QGuiApplication.screenAt(self.start)
        if not screen:
            screen = QtGui.QGuiApplication.primaryScreen()
        # hide overlay first so it isn't in the captured image
        self.hide()
        def do_grab():
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
            try:
                self.close()
            except Exception:
                pass

        QTimer.singleShot(80, do_grab)
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
