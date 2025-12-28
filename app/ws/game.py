from datetime import datetime
from fastapi import WebSocket
import chess
from pydantic import BaseModel
from app.constants.enums import Color, MessageType

class Game :
   def  __init__(self, p1: WebSocket , p2 : WebSocket, game_id):
    self.game_id = game_id
    self.player1= p1
    self.player2= p2
    self.moves= []
    self.finishTime= datetime
    self.board = chess.Board()


class GameMessage (BaseModel):
  type: MessageType
  message : str | None = None
  move: str | None = None
  board : str |None = None
  data : str | None = None
  color: Color | None = None
  turn : Color | None = None
  game_over : bool | None = None