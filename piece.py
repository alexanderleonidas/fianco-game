from const import *

class Piece:
    def __init__(self, color):
        self.color = color
        self.value_sign = 1 if color == WHITE else -1 # Value sign needed for AI so white is positive and black in negative
        self.value = 2 * self.value_sign
        self.valid_moves = []

    def add_moves(self, move):
        self.valid_moves.append(move)
    
    def clear_moves(self):
        self.valid_moves = []