"""
Chat widget for desktop application
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from src.services.api_client import APIClient
from src.services.auth_service import AuthService
import json

class ChatWidget(QWidget):
    """Chat widget component"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.api_client = APIClient()
        self.auth_service = AuthService()
        self.messages = []
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Header
        header = QFrame()
        header.setObjectName("glassPanel")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 12, 16, 12)
        
        title_label = QLabel("JarvisX V2")
        title_font = QFont("Alata", 24, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: white;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        close_btn = QPushButton("✕")
        close_btn.setObjectName("glassButton")
        close_btn.setFixedSize(32, 32)
        close_btn.clicked.connect(self.parent().hide if self.parent() else lambda: None)
        header_layout.addWidget(close_btn)
        
        layout.addWidget(header)
        
        # Messages area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none; background: transparent;")
        
        messages_widget = QWidget()
        self.messages_layout = QVBoxLayout(messages_widget)
        self.messages_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.messages_layout.setSpacing(8)
        
        scroll_area.setWidget(messages_widget)
        layout.addWidget(scroll_area, stretch=1)
        
        # Input area
        input_frame = QFrame()
        input_frame.setObjectName("glassPanel")
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(12, 12, 12, 12)
        input_layout.setSpacing(8)
        
        self.input_field = QLineEdit()
        self.input_field.setObjectName("glassInput")
        self.input_field.setPlaceholderText("Type your message...")
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field, stretch=1)
        
        mic_btn = QPushButton("🎤")
        mic_btn.setObjectName("glassButton")
        mic_btn.setFixedSize(54, 54)
        input_layout.addWidget(mic_btn)
        
        send_btn = QPushButton("Send")
        send_btn.setObjectName("glassButton")
        send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(send_btn)
        
        layout.addWidget(input_frame)
    
    def send_message(self):
        """Send chat message"""
        text = self.input_field.text().strip()
        if not text:
            return
        
        # Add user message
        self.add_message("user", text)
        self.input_field.clear()
        
        # Get AI response
        self.get_ai_response(text)
    
    def add_message(self, role: str, content: str):
        """Add message to chat"""
        message_label = QLabel(content)
        message_label.setObjectName("messageBubble" if role == "user" else "assistantMessage")
        message_label.setWordWrap(True)
        message_label.setAlignment(
            Qt.AlignmentFlag.AlignRight if role == "user" else Qt.AlignmentFlag.AlignLeft
        )
        message_label.setStyleSheet("""
            QLabel {
                background: rgba(59, 130, 246, 0.2);
                border: 1px solid rgba(59, 130, 246, 0.3);
                border-radius: 12px;
                padding: 12px;
                color: white;
                max-width: 80%;
            }
            QLabel#assistantMessage {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        
        self.messages_layout.addWidget(message_label)
        self.messages.append({"role": role, "content": content})
    
    def get_ai_response(self, user_message: str):
        """Get AI response from backend"""
        try:
            response = self.api_client.post("/chat/messages", {
                "content": user_message,
                "conversation_id": None
            })
            
            if response and "message" in response:
                ai_content = response["message"]["content"]
                self.add_message("assistant", ai_content)
        except Exception as e:
            self.add_message("assistant", f"Error: {str(e)}")

