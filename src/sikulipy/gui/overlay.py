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
