from enum import Enum

class Color (str, Enum):
    BLACK= "black"
    WHITE= "white"

class MessageType(str, Enum):
    WAITING = "waiting"
    GAME_START = "game_start"
    MOVE = "move"
    GAME_OVER = "game_over"
    CheckMate = "checkmate"
    DRAW = "draw"
    ILLEGAL_MOVE = "illegal_move"
    WHITE_WINS = "white_win"
    BLACK_WINS = "black_win"
    TIMEOUT = "timeout"