"""
Liquid glass styling for PyQt6
"""
def get_liquid_glass_stylesheet() -> str:
    """Get liquid glass stylesheet"""
    return """
    QMainWindow {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #3B82F6, stop:0.5 #06B6D4, stop:1 #A855F7);
    }
    
    QWidget {
        background: rgba(0, 0, 0, 0.001);
        color: white;
        font-family: 'Albert Sans', sans-serif;
    }
    
    /* Glass Panel */
    QFrame#glassPanel {
        background: rgba(0, 0, 0, 0.001);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
    }
    
    /* Glass Button */
    QPushButton#glassButton {
        background: rgba(0, 0, 0, 0.001);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 12px 24px;
        color: white;
        font-size: 14px;
        font-weight: 600;
    }
    
    QPushButton#glassButton:hover {
        background: rgba(255, 255, 255, 0.05);
    }
    
    QPushButton#glassButton:pressed {
        background: rgba(255, 255, 255, 0.1);
    }
    
    /* Glass Input */
    QLineEdit#glassInput {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 12px;
        color: white;
        font-size: 14px;
    }
    
    QLineEdit#glassInput:focus {
        border: 1px solid #06B6D4;
    }
    
    /* Message Bubble */
    QLabel#messageBubble {
        background: rgba(59, 130, 246, 0.2);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 12px;
        padding: 12px;
        color: white;
    }
    
    QLabel#assistantMessage {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Scroll Area */
    QScrollArea {
        border: none;
        background: transparent;
    }
    
    QScrollBar:vertical {
        background: rgba(255, 255, 255, 0.05);
        width: 8px;
        border-radius: 4px;
    }
    
    QScrollBar::handle:vertical {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 4px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background: rgba(255, 255, 255, 0.3);
    }
    """

