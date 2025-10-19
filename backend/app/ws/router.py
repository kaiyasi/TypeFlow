from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from typing import Optional, Dict, List
import json
import uuid
import asyncio
import structlog
from datetime import datetime, timedelta
import time

from app.core.database import get_db
from app.core.security import verify_token
from app.models.users import User

logger = structlog.get_logger()

# Session data storage for real-time calculations
session_data = {}

class SessionData:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.start_time = datetime.utcnow()
        self.keystrokes = []
        self.correct_chars = 0
        self.total_chars = 0
        self.errors = 0
        self.last_update = datetime.utcnow()
    
    def add_keystroke(self, char: str, correct: bool, timestamp: datetime):
        self.keystrokes.append({
            "char": char,
            "correct": correct,
            "timestamp": timestamp
        })
        self.total_chars += 1
        if correct:
            self.correct_chars += 1
        else:
            self.errors += 1
    
    def calculate_metrics(self):
        """Calculate current WPM and accuracy"""
        now = datetime.utcnow()
        elapsed_minutes = (now - self.start_time).total_seconds() / 60.0
        
        if elapsed_minutes == 0:
            return {"net_wpm": 0, "gross_wpm": 0, "accuracy": 100}
        
        # Calculate gross WPM (total characters / 5 / minutes)
        gross_wpm = (self.total_chars / 5) / elapsed_minutes
        
        # Calculate net WPM (correct characters / 5 / minutes)
        net_wpm = (self.correct_chars / 5) / elapsed_minutes
        
        # Alternative net WPM calculation: gross WPM - (errors / minutes)
        # net_wpm_alt = gross_wpm - (self.errors / elapsed_minutes)
        
        # Calculate accuracy
        accuracy = (self.correct_chars / self.total_chars * 100) if self.total_chars > 0 else 100
        
        return {
            "net_wpm": round(max(0, net_wpm), 1),
            "gross_wpm": round(gross_wpm, 1),
            "accuracy": round(accuracy, 1),
            "errors": self.errors,
            "total_chars": self.total_chars,
            "correct_chars": self.correct_chars
        }

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_sessions: Dict[str, str] = {}  # user_id -> session_id
        self.update_tasks: Dict[str, asyncio.Task] = {}  # session_id -> update task
    
    async def connect(self, websocket: WebSocket, session_id: str, user_id: Optional[str] = None):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        if user_id:
            self.user_sessions[user_id] = session_id
        logger.info("WebSocket connected", session_id=session_id, user_id=user_id)
    
    def disconnect(self, session_id: str, user_id: Optional[str] = None):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if user_id and user_id in self.user_sessions:
            del self.user_sessions[user_id]
        
        # Cancel update task if exists
        if session_id in self.update_tasks:
            self.update_tasks[session_id].cancel()
            del self.update_tasks[session_id]
        
        # Clean up session data
        if session_id in session_data:
            del session_data[session_id]
            
        logger.info("WebSocket disconnected", session_id=session_id, user_id=user_id)
    
    async def send_personal_message(self, message: dict, session_id: str):
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            await websocket.send_text(json.dumps(message))
    
    async def broadcast(self, message: dict):
        for websocket in self.active_connections.values():
            await websocket.send_text(json.dumps(message))
    
    async def start_metrics_updates(self, session_id: str):
        """Start periodic metrics updates every 30 seconds"""
        
        async def update_metrics():
            while session_id in self.active_connections and session_id in session_data:
                await asyncio.sleep(30)  # Update every 30 seconds
                
                if session_id not in session_data:
                    break
                    
                data = session_data[session_id]
                metrics = data.calculate_metrics()
                
                response = {
                    "type": "metrics_update",
                    "metrics": metrics,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                await self.send_personal_message(response, session_id)
                logger.info("Metrics updated", session_id=session_id, metrics=metrics)
        
        task = asyncio.create_task(update_metrics())
        self.update_tasks[session_id] = task

manager = ConnectionManager()

@router.websocket("/")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: Optional[str] = Query(None),
    token: Optional[str] = Query(None)
):
    """WebSocket endpoint for real-time typing sessions"""
    
    # Verify token and get user
    user_id = None
    if token:
        payload = verify_token(token)
        if payload:
            user_id = payload.get("sub")
    
    # Generate session ID if not provided
    if not session_id:
        session_id = str(uuid.uuid4())
    
    await manager.connect(websocket, session_id, user_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            await handle_websocket_message(websocket, session_id, user_id, message)
            
    except WebSocketDisconnect:
        manager.disconnect(session_id, user_id)
    except Exception as e:
        logger.error("WebSocket error", exc_info=e, session_id=session_id)
        manager.disconnect(session_id, user_id)

async def handle_websocket_message(
    websocket: WebSocket, 
    session_id: str, 
    user_id: Optional[str], 
    message: dict
):
    """Handle incoming WebSocket messages"""
    
    message_type = message.get("type")
    
    if message_type == "start_session":
        await handle_start_session(websocket, session_id, user_id, message)
    elif message_type == "keystroke":
        await handle_keystroke(websocket, session_id, user_id, message)
    elif message_type == "heartbeat":
        await handle_heartbeat(websocket, session_id, user_id, message)
    elif message_type == "finish_session":
        await handle_finish_session(websocket, session_id, user_id, message)
    else:
        logger.warning("Unknown message type", type=message_type, session_id=session_id)

async def handle_start_session(websocket: WebSocket, session_id: str, user_id: Optional[str], message: dict):
    """Handle session start"""
    
    # Initialize session data
    session_data[session_id] = SessionData(session_id)
    
    # Start metrics update task
    await manager.start_metrics_updates(session_id)
    
    response = {
        "type": "session_started",
        "session_id": session_id,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await manager.send_personal_message(response, session_id)
    logger.info("Session started", session_id=session_id, user_id=user_id)

async def handle_keystroke(websocket: WebSocket, session_id: str, user_id: Optional[str], message: dict):
    """Handle keystroke event"""
    
    # Extract keystroke data
    char = message.get("char", "")
    correct = message.get("correct", False)
    position = message.get("position", 0)
    timestamp_str = message.get("timestamp", datetime.utcnow().isoformat())
    
    try:
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except:
        timestamp = datetime.utcnow()
    
    # Update session data
    if session_id in session_data:
        data = session_data[session_id]
        data.add_keystroke(char, correct, timestamp)
        
        # Send immediate feedback
        response = {
            "type": "keystroke_processed",
            "char": char,
            "correct": correct,
            "position": position,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await manager.send_personal_message(response, session_id)
    


async def handle_heartbeat(websocket: WebSocket, session_id: str, user_id: Optional[str], message: dict):
    """Handle heartbeat (keepalive)"""
    
    response = {
        "type": "heartbeat_ack",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await manager.send_personal_message(response, session_id)

async def handle_finish_session(websocket: WebSocket, session_id: str, user_id: Optional[str], message: dict):
    """Handle session completion"""
    
    # Calculate final metrics
    final_metrics = {"net_wpm": 0, "gross_wpm": 0, "accuracy": 100, "errors": 0}
    
    if session_id in session_data:
        data = session_data[session_id]
        final_metrics = data.calculate_metrics()
    
    # Process final results
    final_text = message.get("text", "")
    keystrokes = message.get("keystrokes", [])
    
    response = {
        "type": "session_ended",
        "session_id": session_id,
        "final_results": final_metrics,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await manager.send_personal_message(response, session_id)
    logger.info("Session finished", session_id=session_id, user_id=user_id, final_results=final_metrics)