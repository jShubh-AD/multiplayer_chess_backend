from datetime import datetime
from fastapi import WebSocket
import chess

class Game :
   def  __init__(self, p1: WebSocket , p2 : WebSocket, game_id):
    self.game_id = game_id
    self.player1= p1
    self.player2= p2
    self.moves= []
    self.finishTime= datetime
    self.board = chess.Board()
