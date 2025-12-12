#!/usr/bin/env python3
"""
JarvisX V2 - Desktop Application
Main entry point
"""
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from src.app import JarvisApp

def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("JarvisX V2")
    app.setOrganizationName("JarvisX")
    
    # Enable high DPI scaling
    app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    # Create and show main window
    window = JarvisApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

