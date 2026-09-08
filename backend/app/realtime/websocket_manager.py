from typing import List, Dict
import json
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # Map well_id -> list of active WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, well_id: str):
        await websocket.accept()
        if well_id not in self.active_connections:
            self.active_connections[well_id] = []
        self.active_connections[well_id].append(websocket)

    def disconnect(self, websocket: WebSocket, well_id: str):
        if well_id in self.active_connections:
            if websocket in self.active_connections[well_id]:
                self.active_connections[well_id].remove(websocket)
            if not self.active_connections[well_id]:
                del self.active_connections[well_id]

    async def broadcast_to_well(self, well_id: str, message: dict):
        if well_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[well_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.append(connection)
            for dead in disconnected:
                self.disconnect(dead, well_id)

ws_manager = ConnectionManager()
