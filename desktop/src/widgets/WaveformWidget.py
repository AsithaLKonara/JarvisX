"""
Waveform animation widget for voice recording
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QColor, QPainter


class WaveformBar(QFrame):
    """Individual waveform bar"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(4)
        self.setMinimumHeight(8)
        self.setMaximumHeight(32)
        self._height = 8
        self.setObjectName("waveformBar")
        self.animation = None
    
    def get_height(self):
        return self._height
    
    def set_height(self, height):
        self._height = height
        self.setFixedHeight(int(height))
    
    height = pyqtProperty(float, get_height, set_height)
    
    def start_animation(self, delay=0):
        """Start bar animation"""
        if self.animation:
            self.animation.stop()
        
        self.animation = QPropertyAnimation(self, b"height")
        self.animation.setDuration(600 + delay)
        self.animation.setStartValue(8)
        self.animation.setEndValue(32)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.animation.setLoopCount(-1)  # Infinite loop
        self.animation.start()


class WaveformWidget(QWidget):
    """Waveform animation widget"""
    
    def __init__(self, parent=None, bar_count=5):
        super().__init__(parent)
        self.bar_count = bar_count
        self.bars = []
        self.is_active = False
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        for i in range(self.bar_count):
            bar = WaveformBar(self)
            self.bars.append(bar)
            layout.addWidget(bar)
    
    def set_active(self, active: bool):
        """Set animation active state"""
        self.is_active = active
        if active:
            for i, bar in enumerate(self.bars):
                QTimer.singleShot(i * 100, lambda b=bar, d=i*100: b.start_animation(d))
        else:
            for bar in self.bars:
                if bar.animation:
                    bar.animation.stop()
                bar.set_height(8)

