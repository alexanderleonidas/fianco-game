from const import *

class Piece:
    def __init__(self, name, color, value):
        self.name = name
        self.color = color
        value_sign = 1 if color == WHITE else -1 # Value sign needed for AI so white is positive and black in negative
        self.value = value * value_sign
        self.valid_moves = []
        self.moved = False

    def add_moves(self, move):
        self.valid_moves.append( move)
    
    def clear_moves(self):
        self.valid_moves = []

class Circle(Piece):
    def __init__(self, color):
        self.direction = -1 if color == WHITE else 1
        super().__init__('Circle', color, 1.0)