from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.rooms: dict[str, list[WebSocket]] = {}

    async def connectUser(self, room_id : str, ws: WebSocket):
        await ws.accept()
        self.rooms.setdefault(room_id, [])
        self.rooms[room_id].append(ws)
        print(f"roome created {self.rooms} ")

    async def disconnect(self, room_id : str, websocket: WebSocket):
        if room_id in self.rooms and websocket in self.rooms[room_id]:
            self.rooms[room_id].remove(websocket)

        if room_id in self.rooms and not self.rooms[room_id]:
            del self.rooms[room_id]

    async def broadcast(self,room_id: str, message: str):
        for ws in self.rooms.get(room_id, []):
            await ws.send_text(message)