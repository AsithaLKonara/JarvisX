"""
Siri-style main window for desktop application
"""
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from src.widgets.ChatWidget import ChatWidget
from src.styles.siri_style import get_siri_stylesheet


class MainWindow(QMainWindow):
    """Siri-style main window"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.set_siri_style()
    
    def init_ui(self):
        """Initialize UI"""
        # Set window properties
        self.setWindowTitle("JarvisX V2")
        self.setMinimumSize(400, 600)
        self.resize(400, 700)
        
        # Center window
        self.center_window()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Add chat widget
        self.chat_widget = ChatWidget(self)
        layout.addWidget(self.chat_widget)
        
        # Set window flags for compact appearance
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        
        # Make window semi-transparent if needed (optional)
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
    
    def center_window(self):
        """Center window on screen"""
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)
    
    def set_siri_style(self):
        """Apply Siri-style stylesheet"""
        self.setStyleSheet(get_siri_stylesheet())
    
    def mousePressEvent(self, event):
        """Handle mouse press for window dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for window dragging"""
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, 'drag_position'):
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

