from fastapi import WebSocket
from app.ws.game import Game
from app.ws.helpers import WsHelper
import chess
import uuid

class GameManager:
    def __init__(self):
        self.games: dict[str, Game] = {}
        self.waitingUser: WebSocket | None = None

    async def connectUser(self, ws: WebSocket):
        try: 
            if(self.waitingUser):
                await ws.send_text("Found a perfect match for you.")
                await self.start_game(self.waitingUser, ws)
                self.waitingUser = None
                return
            else:
                self.waitingUser = ws
                await ws.send_text("Waiting for a perfect match.")
                ws.state.game_id = None
                return
        except any as e:
            print(e)


    async def disconnect(self, ws: WebSocket):
        if ws is self.waitingUser:
            self.waitingUser = None
            return
        else:
           game_id =  WsHelper.get_game_id(ws)

           if not game_id:
               return
           game = self.games.pop(game_id, None)
           if not game:
               return
           otherPlaer =  game.player1 if game.player2 is ws else game.player2
           await otherPlaer.send_text("Player Disconnected, Closing game")
           await otherPlaer.close()

    async def make_move(self, message: str, ws: WebSocket):
        # get game id
        game_id = WsHelper.get_game_id(ws)

        if not game_id:
            return
        game = self.games.get(game_id)

        if not game:
            return
        
        board = game.board

        #  validate move 

        try: 
            move = chess.Move.from_uci(message)
            print(f"move {move}")
            print(f"message {message}")
        except ValueError:
            await ws.send_text("invalid_move_format")
            return
        
        if move not in board.legal_moves:
            await ws.send_text("illegal_move")
            return

        board.push(move)
        game.moves.append(message)

         # game state checks
        if board.is_checkmate():
            result = "checkmate"
        elif board.is_stalemate():
            result = "stalemate"
        elif board.is_insufficient_material():
            result = "draw"
        else:
            result = "ok"

        await self.broadcast(
            game_id,
            {
                "move": message,
                "fen": board.fen(),
                "state": result
            }
        )


    async def broadcast(self, game_id: str, payload: dict):
        game = self.games.get(game_id)
        if not game:
            return

        await game.player1.send_json(payload)
        await game.player2.send_json(payload)


      #  start game method
    async def start_game(self, p1: WebSocket, p2: WebSocket):
        game_id = str(uuid.uuid4())
        game = Game(p1, p2, game_id)
        self.games[game_id] = game

        p1.state.game_id = game_id
        p2.state.game_id = game_id

        await self.broadcast(game_id, {"message": "Game started"})