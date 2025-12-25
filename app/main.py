from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.ws.manager import ConnectionManager

app = FastAPI()
manager = ConnectionManager()

@app.websocket("/ws")
async def web_endpoint(websocket: WebSocket, room_id: str):
    await manager.connectUser(ws=websocket,room_id=room_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(room_id=room_id, message=data)
    except WebSocketDisconnect:
        await manager.disconnect(room_id=room_id, websocket=websocket)