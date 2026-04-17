#!/usr/bin/env python3
"""
JarvisX V2 - Desktop Application
Main entry point
"""
import sys
from pathlib import Path

# Add desktop directory to path for imports like src.*
sys.path.insert(0, str(Path(__file__).parent.parent))
# Add project root for core/, memory/, backend/ modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from src.app import JarvisApp

def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("JarvisX V2")
    app.setOrganizationName("JarvisX")
    
    # Enable high DPI scaling when supported by the current Qt build.
    if hasattr(Qt.ApplicationAttribute, "AA_EnableHighDpiScaling"):
        app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt.ApplicationAttribute, "AA_UseHighDpiPixmaps"):
        app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    # Create widget app (floating button + popup)
    _widget_app = JarvisApp(app)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

