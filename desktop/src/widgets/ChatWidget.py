"""
Siri-style chat widget for desktop application
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont
from src.services.api_client import APIClient
from src.widgets.VoiceButton import VoiceButton
from src.widgets.WaveformWidget import WaveformWidget
import json


class CompactMessageBubble(QLabel):
    """Compact message bubble for Siri-style"""
    
    def __init__(self, message: str, is_user: bool, parent=None):
        super().__init__(parent)
        self.message = message
        self.is_user = is_user
        self.init_ui()
    
    def init_ui(self):
        """Initialize message bubble UI"""
        self.setText(self.message)
        self.setWordWrap(True)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.setObjectName("assistantMessage" if not self.is_user else "userMessage")
        
        font = QFont()
        font.setPointSize(15)
        self.setFont(font)
        
        # Set size policy
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        self.setMaximumWidth(300)
        
        # Calculate height based on content
        self.adjustSize()


class ChatWidget(QWidget):
    """Siri-style chat widget component"""
    
    message_sent = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.api_client = APIClient()
        self.messages = []
        self.is_recording = False
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Background
        self.setStyleSheet("background: #000000;")
        
        # Messages area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none; background: transparent;")
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        messages_widget = QWidget()
        self.messages_layout = QVBoxLayout(messages_widget)
        self.messages_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.messages_layout.setSpacing(8)
        self.messages_layout.setContentsMargins(16, 20, 16, 20)
        
        # Empty state
        self.empty_label = QLabel("Say something\nTap the microphone to start")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("color: white; font-size: 24px; font-weight: 600;")
        self.empty_label.setWordWrap(True)
        self.messages_layout.addWidget(self.empty_label)
        
        scroll_area.setWidget(messages_widget)
        layout.addWidget(scroll_area, stretch=1)
        
        # Voice button area
        voice_container = QWidget()
        voice_layout = QVBoxLayout(voice_container)
        voice_layout.setContentsMargins(0, 20, 0, 40)
        voice_layout.setSpacing(16)
        voice_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Waveform widget
        self.waveform = WaveformWidget(self)
        self.waveform.setVisible(False)
        voice_layout.addWidget(self.waveform)
        
        # Recording label
        self.recording_label = QLabel("Listening...")
        self.recording_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.recording_label.setStyleSheet("color: white; font-size: 14px; font-weight: 500;")
        self.recording_label.setVisible(False)
        voice_layout.addWidget(self.recording_label)
        
        # Voice button
        self.voice_button = VoiceButton(self)
        self.voice_button.clicked.connect(self.toggle_recording)
        voice_layout.addWidget(self.voice_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(voice_container)
    
    def toggle_recording(self):
        """Toggle voice recording"""
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
    
    def start_recording(self):
        """Start voice recording"""
        self.is_recording = True
        self.voice_button.set_active(True)
        self.waveform.set_active(True)
        self.waveform.setVisible(True)
        self.recording_label.setVisible(True)
        # TODO: Start actual voice recording
    
    def stop_recording(self):
        """Stop voice recording and process"""
        self.is_recording = False
        self.voice_button.set_active(False)
        self.waveform.set_active(False)
        self.waveform.setVisible(False)
        self.recording_label.setVisible(False)
        
        # TODO: Process voice recording and convert to text
        # For now, simulate with a placeholder
        transcript = "Hello, how are you?"
        self.send_message(transcript)
    
    def send_message(self, text: str):
        """Send chat message"""
        if not text.strip():
            return
        
        # Hide empty state
        if self.empty_label:
            self.empty_label.setVisible(False)
        
        # Add user message
        user_bubble = CompactMessageBubble(text, is_user=True)
        self.messages_layout.addWidget(user_bubble, alignment=Qt.AlignmentFlag.AlignRight)
        self.messages_layout.addStretch(0)
        
        # Scroll to bottom
        QTimer.singleShot(100, lambda: self.scroll_to_bottom())
        
        # Get AI response
        self.get_ai_response(text)
    
    def get_ai_response(self, user_message: str):
        """Get AI response"""
        try:
            # TODO: Call actual API
            # For now, simulate response
            response_text = "Hello! I'm JarvisX. How can I help you today?"
            
            assistant_bubble = CompactMessageBubble(response_text, is_user=False)
            self.messages_layout.addWidget(assistant_bubble, alignment=Qt.AlignmentFlag.AlignLeft)
            self.messages_layout.addStretch(0)
            
            QTimer.singleShot(100, lambda: self.scroll_to_bottom())
        except Exception as e:
            print(f"Error getting AI response: {e}")
    
    def scroll_to_bottom(self):
        """Scroll messages to bottom"""
        # Find scroll area and scroll to bottom
        scroll_area = self.findChild(QScrollArea)
        if scroll_area:
            scroll_bar = scroll_area.verticalScrollBar()
            scroll_bar.setValue(scroll_bar.maximum())
