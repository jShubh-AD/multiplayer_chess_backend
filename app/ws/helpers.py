from fastapi import WebSocket

class WsHelper:
    @staticmethod
    def get_game_id(ws: WebSocket) -> str|None:
        return getattr(ws.state, "game_id", None)