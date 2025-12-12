"""
Main application class
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import QMainWindow, QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QIcon, QAction
from src.windows.MainWindow import MainWindow
from src.widgets.ChatWidget import ChatWidget

class JarvisApp(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JarvisX V2")
        self.setMinimumSize(400, 600)
        
        # System tray
        self.tray_icon = None
        self.setup_system_tray()
        
        # Main window or widget
        self.chat_widget = ChatWidget()
        self.setCentralWidget(self.chat_widget)
        
        # Apply liquid glass styling
        self.apply_liquid_glass_style()
    
    def setup_system_tray(self):
        """Setup system tray icon"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        
        self.tray_icon = QSystemTrayIcon(self)
        # Set icon (create icon file later)
        # self.tray_icon.setIcon(QIcon("resources/icons/app_icon.png"))
        
        tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()
    
    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()
            self.raise_()
            self.activateWindow()
    
    def apply_liquid_glass_style(self):
        """Apply liquid glass styling"""
        from src.styles.liquid_glass import get_liquid_glass_stylesheet
        self.setStyleSheet(get_liquid_glass_stylesheet())
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.tray_icon and self.tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            event.accept()

