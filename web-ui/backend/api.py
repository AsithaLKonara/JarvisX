#!/usr/bin/env python3
"""
Jarvis X V2 - Web UI Backend API
FastAPI server for the web interface
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import Jarvis modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
import psutil
import json
from datetime import datetime

# Import Jarvis modules
try:
    from core.hybrid_brain import HybridBrain
    from utils.config import Config
    BRAIN_AVAILABLE = True
except ImportError:
    BRAIN_AVAILABLE = False
    print("⚠️  Warning: Jarvis brain modules not found")

try:
    from speech.text_to_speech import TTSEngine
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Jarvis X V2 Web API",
    description="Backend API for Jarvis X V2 web interface",
    version="2.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Jarvis brain
jarvis_brain = None
tts_engine = None

@app.on_event("startup")
async def startup_event():
    """Initialize Jarvis brain on startup"""
    global jarvis_brain, tts_engine
    
    logger.info("🚀 Starting Jarvis Web API...")
    
    if BRAIN_AVAILABLE:
        try:
            config = Config()
            jarvis_brain = HybridBrain(config)
            logger.info("✅ Jarvis brain initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize brain: {e}")
    
    if TTS_AVAILABLE:
        try:
            tts_engine = TTSEngine(engine="pyttsx3", rate=150)
            if tts_engine.is_available:
                logger.info("✅ TTS engine initialized")
        except Exception as e:
            logger.warning(f"⚠️  TTS initialization failed: {e}")


# Pydantic models for request/response
class ChatMessage(BaseModel):
    message: str
    mode: Optional[str] = "casual"
    max_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.7

class ChatResponse(BaseModel):
    response: str
    mode: str
    emotion: Optional[str] = None
    timestamp: str
    tts_audio: Optional[str] = None

class SystemStatus(BaseModel):
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    timestamp: str

class ModeInfo(BaseModel):
    id: str
    name: str
    icon: str
    description: str
    active: bool

class Settings(BaseModel):
    theme: str = "professional"
    tts_enabled: bool = False
    tts_engine: str = "pyttsx3"
    show_avatar: bool = True
    mode: str = "casual"


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Jarvis X V2 Web API",
        "version": "2.0.0",
        "status": "online",
        "brain_available": jarvis_brain is not None,
        "tts_available": tts_engine is not None and tts_engine.is_available
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "brain": jarvis_brain is not None,
            "tts": tts_engine is not None and tts_engine.is_available
        }
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """
    Send a message to Jarvis and get a response
    """
    if not jarvis_brain:
        raise HTTPException(status_code=503, detail="Jarvis brain not available")
    
    try:
        # Get response from Jarvis brain
        response = jarvis_brain.get_response(message.message)
        
        # Get emotion if available
        emotion = None
        if hasattr(jarvis_brain, 'get_last_emotion'):
            emotion = jarvis_brain.get_last_emotion()
        
        return ChatResponse(
            response=response,
            mode=message.mode,
            emotion=emotion,
            timestamp=datetime.now().isoformat(),
            tts_audio=None  # Will add TTS generation later
        )
    
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/modes", response_model=List[ModeInfo])
async def get_modes():
    """Get list of available modes"""
    modes = [
        {
            "id": "engineer",
            "name": "Engineer",
            "icon": "🔧",
            "description": "Software engineering & development",
            "active": False
        },
        {
            "id": "system",
            "name": "System Monitor",
            "icon": "📊",
            "description": "Real-time PC monitoring & control",
            "active": False
        },
        {
            "id": "designer",
            "name": "Designer",
            "icon": "🎨",
            "description": "Professional design workflows",
            "active": False
        },
        {
            "id": "editor",
            "name": "Editor",
            "icon": "🎬",
            "description": "Video editing automation",
            "active": False
        },
        {
            "id": "business",
            "name": "Business",
            "icon": "💼",
            "description": "Financial & business management",
            "active": False
        },
        {
            "id": "casual",
            "name": "Casual",
            "icon": "💬",
            "description": "Natural conversations & Sinhala",
            "active": True
        },
        {
            "id": "career",
            "name": "Career",
            "icon": "👔",
            "description": "Job-specific guidance (169 roles)",
            "active": False
        }
    ]
    return modes

@app.get("/system-status", response_model=SystemStatus)
async def get_system_status():
    """Get current system status (CPU, RAM, Disk)"""
    try:
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_gb = memory.used / (1024**3)
        memory_total_gb = memory.total / (1024**3)
        
        # Disk
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        disk_used_gb = disk.used / (1024**3)
        disk_total_gb = disk.total / (1024**3)
        
        return SystemStatus(
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_used_gb=round(memory_used_gb, 2),
            memory_total_gb=round(memory_total_gb, 2),
            disk_percent=disk_percent,
            disk_used_gb=round(disk_used_gb, 2),
            disk_total_gb=round(disk_total_gb, 2),
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        logger.error(f"System status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/settings", response_model=Settings)
async def get_settings():
    """Get current settings"""
    # TODO: Load from database or config file
    return Settings(
        theme="professional",
        tts_enabled=False,
        tts_engine="pyttsx3",
        show_avatar=True,
        mode="casual"
    )

@app.post("/settings")
async def update_settings(settings: Settings):
    """Update settings"""
    # TODO: Save to database or config file
    return {"status": "success", "settings": settings.dict()}

@app.post("/tts/speak")
async def speak_text(text: str, engine: str = "pyttsx3"):
    """Generate TTS audio for given text"""
    if not tts_engine or not tts_engine.is_available:
        raise HTTPException(status_code=503, detail="TTS not available")
    
    try:
        # Generate speech (non-blocking)
        tts_engine.speak(text, blocking=False)
        return {"status": "success", "text": text}
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket endpoint
from websocket_handler import handle_websocket

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time chat"""
    await handle_websocket(websocket, client_id, jarvis_brain)


if __name__ == "__main__":
    import uvicorn
    
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║        🤖 JARVIS X V2 - WEB API SERVER                        ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

Starting server on: http://localhost:8000
API docs: http://localhost:8000/docs
    """)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

