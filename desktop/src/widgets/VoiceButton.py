"""
Large Siri-style voice button widget
"""
from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush


class VoiceButton(QPushButton):
    """Large Siri-style voice button"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(120, 120)
        self.setObjectName("voiceButton")
        self.is_active = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def set_active(self, active: bool):
        """Set button active state"""
        self.is_active = active
        self.update()
    
    def paintEvent(self, event):
        """Custom paint event for button"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        center = rect.center()
        radius = min(rect.width(), rect.height()) / 2
        
        # Draw button circle
        if self.is_active:
            painter.setBrush(QBrush(QColor("#ff3b30")))
        else:
            painter.setBrush(QBrush(QColor("#ffffff")))
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center.x() - radius, center.y() - radius, 
                           radius * 2, radius * 2)
        
        # Draw inner circle
        inner_radius = radius * 0.7
        if not self.is_active:
            painter.setPen(QPen(QColor("#000000"), 2))
            painter.setBrush(QBrush(QColor("#ffffff")))
        else:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor("#ff3b30")))
        
        painter.drawEllipse(center.x() - inner_radius, center.y() - inner_radius,
                           inner_radius * 2, inner_radius * 2)
        
        # Draw microphone icon (when not active) or stop icon (when active)
        icon_size = 24
        if self.is_active:
            # Draw stop icon (square)
            stop_size = icon_size
            painter.setBrush(QBrush(QColor("#ffffff")))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(
                center.x() - stop_size / 2,
                center.y() - stop_size / 2,
                stop_size, stop_size, 4, 4
            )
        else:
            # Draw microphone icon
            mic_width = 20
            mic_height = 30
            mic_x = center.x() - mic_width / 2
            mic_y = center.y() - mic_height / 2
            
            painter.setPen(QPen(QColor("#000000"), 3))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            
            # Microphone body
            painter.drawRoundedRect(mic_x, mic_y, mic_width, mic_height, 10, 10)
            
            # Microphone stand
            stand_x = center.x() - 2
            stand_y = mic_y + mic_height - 2
            painter.setBrush(QBrush(QColor("#000000")))
            painter.drawRect(stand_x, stand_y, 4, 8)


