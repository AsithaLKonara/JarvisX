"""
Siri-style styling for PyQt6
"""
def get_siri_stylesheet() -> str:
    """Get Siri-style stylesheet"""
    return """
    QMainWindow {
        background: #000000;
    }
    
    QWidget {
        background: transparent;
        color: white;
        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
    }
    
    /* Message Bubble */
    QLabel#userMessage {
        background: #007AFF;
        color: white;
        border: none;
        border-radius: 18px;
        padding: 12px 16px;
        max-width: 300px;
        font-size: 15px;
    }
    
    QLabel#assistantMessage {
        background: rgba(255, 255, 255, 0.15);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 18px;
        padding: 12px 16px;
        max-width: 300px;
        font-size: 15px;
    }
    
    /* Voice Button */
    QPushButton#voiceButton {
        background: white;
        border: none;
        border-radius: 50%;
        min-width: 120px;
        min-height: 120px;
        max-width: 120px;
        max-height: 120px;
    }
    
    QPushButton#voiceButton:pressed {
        background: #ff3b30;
    }
    
    QPushButton#voiceButton:hover {
        background: #f5f5f5;
    }
    
    /* Waveform Bars */
    QFrame#waveformBar {
        background: white;
        border: none;
        border-radius: 2px;
        min-width: 4px;
        min-height: 8px;
    }
    
    /* Scroll Area */
    QScrollArea {
        border: none;
        background: transparent;
    }
    
    QScrollBar:vertical {
        background: transparent;
        width: 8px;
        border-radius: 4px;
    }
    
    QScrollBar::handle:vertical {
        background: rgba(255, 255, 255, 0.3);
        border-radius: 4px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background: rgba(255, 255, 255, 0.5);
    }
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0;
        width: 0;
    }
    """

