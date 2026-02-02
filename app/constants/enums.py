from enum import Enum

class Color (str, Enum):
    BLACK= "black"
    WHITE= "white"

class MessageType(str, Enum):
    WAITING = "waiting"
    DISCONNECT = "disconnect"
    GAME_START = "game_start"
    MOVE = "move"
    CHAT = "chat"
    REMATCH_REQUEST = "rematch_request"
    REMATCH_ACCEPT = "rematch_accept"
    REMATCH_REJECT = "rematch_reject"
    CHALLENGE = "challenge"
    GAME_OVER = "game_over"
    CHECKMATE = "checkmate"
    DRAW = "draw"
    ILLEGAL_MOVE = "illegal_move"
    WHITE_WINS = "white_win"
    BLACK_WINS = "black_win"
    TIMEOUT = "timeout"
    OFFER = "offer"
    ANSWER = "answer"
    ICE = "ice"
