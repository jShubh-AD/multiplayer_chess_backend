from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.ws.manager import GameManager

app = FastAPI()
manager = GameManager()

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    print("connect with user")
    await manager.connectUser(ws=ws)
    try:
        while True:
            data = await ws.receive_text()
            await manager.make_move(message=data, ws= ws)

    except WebSocketDisconnect:
        await manager.disconnect(ws)

