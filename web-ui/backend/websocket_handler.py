#!/usr/bin/env python3
"""
WebSocket handler for real-time chat communication
"""

import json
import logging
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"✅ Client {client_id} connected")
    
    def disconnect(self, client_id: str):
        """Remove disconnected client"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"❌ Client {client_id} disconnected")
    
    async def send_message(self, client_id: str, message: Dict[str, Any]):
        """Send message to specific client"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending to {client_id}: {e}")
                self.disconnect(client_id)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        for client_id in list(self.active_connections.keys()):
            await self.send_message(client_id, message)


# Global connection manager
manager = ConnectionManager()


async def handle_websocket(websocket: WebSocket, client_id: str, jarvis_brain):
    """
    Handle WebSocket communication for a client
    
    Message types:
    - chat: User message, stream AI response
    - system_status: Request system status update
    - tts_status: Request TTS status
    - ping: Keep-alive ping
    """
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            message_type = message.get('type', 'chat')
            
            if message_type == 'chat':
                await handle_chat_message(websocket, client_id, message, jarvis_brain)
            
            elif message_type == 'system_status':
                await handle_system_status(websocket, client_id)
            
            elif message_type == 'ping':
                await websocket.send_json({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                })
            
            else:
                await websocket.send_json({
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}'
                })
    
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
        manager.disconnect(client_id)


async def handle_chat_message(websocket: WebSocket, client_id: str, message: Dict, jarvis_brain):
    """Handle chat message and stream response"""
    user_message = message.get('message', '')
    mode = message.get('mode', 'casual')
    
    if not user_message:
        return
    
    try:
        # Send typing indicator
        await websocket.send_json({
            'type': 'typing',
            'status': True
        })
        
        # Get response from Jarvis
        # Note: Current implementation doesn't support streaming
        # For now, send complete response
        response = jarvis_brain.get_response(user_message)
        
        # Get emotion if available
        emotion = None
        if hasattr(jarvis_brain, 'get_last_emotion'):
            emotion = jarvis_brain.get_last_emotion()
        
        # Send response
        await websocket.send_json({
            'type': 'message',
            'role': 'assistant',
            'content': response,
            'emotion': emotion,
            'mode': mode,
            'timestamp': datetime.now().isoformat()
        })
        
        # Send typing indicator off
        await websocket.send_json({
            'type': 'typing',
            'status': False
        })
    
    except Exception as e:
        logger.error(f"Chat handling error: {e}")
        await websocket.send_json({
            'type': 'error',
            'message': str(e)
        })


async def handle_system_status(websocket: WebSocket, client_id: str):
    """Send system status update"""
    try:
        import psutil
        
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        await websocket.send_json({
            'type': 'system_status',
            'data': {
                'cpu': cpu_percent,
                'memory': {
                    'percent': memory.percent,
                    'used_gb': round(memory.used / (1024**3), 2),
                    'total_gb': round(memory.total / (1024**3), 2)
                },
                'disk': {
                    'percent': disk.percent,
                    'used_gb': round(disk.used / (1024**3), 2),
                    'total_gb': round(disk.total / (1024**3), 2)
                }
            },
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"System status error: {e}")

