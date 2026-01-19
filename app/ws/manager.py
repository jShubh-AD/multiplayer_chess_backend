from fastapi import WebSocket
from app.ws.game import Game, GameMessage
from app.constants.enums import MessageType, Color
from app.ws.helpers import WsHelper
import chess
import uuid

class GameManager:
    def __init__(self):
        self.games: dict[str, Game] = {}
        self.waitingUser: WebSocket | None = None
        
        
    #  handle connect ws
    async def connectUser(self, ws: WebSocket):
        try: 
            if(self.waitingUser):
                await self.start_game(self.waitingUser, ws)
                self.waitingUser = None
                return
            else:
                self.waitingUser = ws
                await ws.send_json(
                    GameMessage(
                        type= MessageType.WAITING,
                        message= "Waiting for another player to join"
                    ).model_dump()
                )
                ws.state.game_id = None
                return
        except any as e: print(e)


    #  handle start game
    async def start_game(self, p1: WebSocket, p2: WebSocket):
        game_id = str(uuid.uuid4())
        game = Game(p1, p2, game_id)
        self.games[game_id] = game

        p1.state.game_id = game_id
        p2.state.game_id = game_id

        await p1.send_json(
            GameMessage(
             type=MessageType.GAME_START,
             message="Game Starts Now",
             color=Color.WHITE
            ).model_dump()
        )
        await p2.send_json(
            GameMessage(
                type=MessageType.GAME_START,
                message="Game Starts Now",
                color=Color.BLACK
              ).model_dump())

    #  handle disconect ws
    async def disconnect(self, ws: WebSocket):
        if ws is self.waitingUser:
            self.waitingUser = None
            return
        else:
           game_id =  WsHelper.get_game_id(ws)

           if not game_id: return
           game = self.games.pop(game_id, None)
           if not game: return
           otherPlaer =  game.player1 if game.player2 is ws else game.player2
           await otherPlaer.send_json(GameMessage(type= MessageType.DISCONNECT, message="Opponent has left the game").model_dump())
           await otherPlaer.close()

    #  handle broadcast move
    async def broadcast(self, game_id: str, payload: GameMessage):
        game = self.games.get(game_id)
        if not game: return

        await game.player1.send_json(payload)
        await game.player2.send_json(payload)


    # message handeler 
    async def message_handeler(self,raw, ws: WebSocket):
        msg = GameMessage.model_validate_json(raw)

        match msg.type:
            case MessageType.MOVE:
                await self.make_move(ws=ws, message=msg.move)

            case MessageType.CHAT:
                await self.broadcast_chat(ws, msg)

            case MessageType.REMATCH_REQUEST:
                await self.request_rematch(ws)

            case MessageType.REMATCH_ACCEPT:
                await self.accept_rematch(ws)

            case MessageType.REMATCH_REJECT:
                await self.reject_rematch(ws)

            case MessageType.CHALLENGE:
                await self.challenge_player(ws=ws, msg=msg)


    # handle broadcasting chat msg
    async def broadcast_chat():
        print("broadcast_chat called")

    # handle broadcasting chat msg
    async def request_rematch(self, ws: WebSocket):
        print("request_rematch called")
        game_id = WsHelper.get_game_id(ws)
        if not game_id : return
        game = self.games.get(game_id)
        if not game : return
        other_player = game.player1 if ws is game.player2 else  game.player2
        await other_player.send_json(GameMessage(type=MessageType.REMATCH_REQUEST, message="Opponent wants a rematch").model_dump())

    # handle broadcasting chat msg
    async def accept_rematch(self, ws: WebSocket):
        print("accept_rematch called")
        game_id = WsHelper.get_game_id(ws)
        if not game_id : return
        game = self.games.get(game_id)
        if not game : return
        other_player = game.player1 if ws is game.player2 else  game.player2
        game.moves.clear()
        game.board = chess.Board()

        await ws.send_json(
            GameMessage(
             type=MessageType.GAME_START,
             message="Game Starts Now",
             color=Color.WHITE
            ).model_dump()
        )
        await other_player.send_json(
            GameMessage(
                type=MessageType.GAME_START,
                message="Game Starts Now",
                color=Color.BLACK
              ).model_dump())

    # handle broadcasting chat msg
    async def reject_rematch(self, ws:WebSocket):
        print("reject_rematch called")
        await self.disconnect(ws)

    # handle broadcasting chat msg
    async def challenge_player(self, ws: WebSocket, msg: str):
        print("challenge_player called")
        # exit the current room 
        await self.disconnect(ws=ws)
        # check if any player in waiting if not join waiting 
        if self.waitingUser is None: 
            self.waitingUser = ws
            await ws.send_json(GameMessage(type= MessageType.WAITING, message= "Waiting for opponent").model_dump())
            return

        # else start match with person in waiting
        opponent = self.waitingUser
        self.waitingUser = None

        await self.start_game(p1=opponent, p2=ws)

           
    #  handle make move and broadcast them to user
    async def make_move(self, message: str, ws: WebSocket):
        # get game id
        game_id = WsHelper.get_game_id(ws)

        if not game_id: return
        game = self.games.get(game_id)

        if not game: return
        
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
        if board.is_checkmate(): result = "checkmate"
        elif board.is_stalemate():result = "stalemate"
        elif board.is_insufficient_material(): result = "draw"
        else: result = "ok"

        await self.broadcast(
            game_id,
            GameMessage(
                type=MessageType.MOVE,
                move=message,
                board=board.fen(),
            ).model_dump())