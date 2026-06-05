from typing import Dict, List
from fastapi import WebSocket
import json

class WebSocketManager:
    """
    Real-vaqt bidding uchun WebSocket ulanishlarini boshqarish.
    Har bir auktsion o'z ulanishlar ro'yxatiga ega.
    """
    def __init__(self):
        # {auction_id: [WebSocket, ...]}
        self.rooms: Dict[int, List[WebSocket]] = {}

    async def connect(self, auction_id: int, websocket: WebSocket):
        await websocket.accept()
        if auction_id not in self.rooms:
            self.rooms[auction_id] = []
        self.rooms[auction_id].append(websocket)

    def disconnect(self, auction_id: int, websocket: WebSocket):
        if auction_id in self.rooms:
            self.rooms[auction_id].remove(websocket)
            if not self.rooms[auction_id]:
                del self.rooms[auction_id]

    async def broadcast(self, auction_id: int, data: dict):
        """Auktsion xonasidagi barcha ulangan foydalanuvchilarga xabar yuborish"""
        if auction_id not in self.rooms:
            return
        dead = []
        for ws in self.rooms[auction_id]:
            try:
                await ws.send_text(json.dumps(data, ensure_ascii=False))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.rooms[auction_id].remove(ws)

    def get_watchers(self, auction_id: int) -> int:
        return len(self.rooms.get(auction_id, []))

# Global instance
ws_manager = WebSocketManager()
