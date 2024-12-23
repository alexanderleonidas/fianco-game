import time
import pygame
from const import *
from board import Board
from move import Move
from mover import Mover
from square import Square
from ai import AI
from copy import deepcopy

class Game:
    def __init__(self):
        self.board = Board()
        self.mover = Mover()
        self.player = WHITE
        self.ai = AI(1)
        self.game_mode = 'pvc' # pvp or pvc
        self.running = True
 
    def next_turn(self):
        self.player = WHITE if self.player == BLACK else BLACK
    
    def reset(self):
        self.__init__()
    
    def select_piece(self, piece, row: int, col: int):
        if piece.color == self.player:
            self.board.calculate_moves(piece, row, col)
            self.mover.save_initial(row, col)
            self.mover.pick_piece(piece)
    
    def move_piece(self, final_row: int, final_col: int):
        piece = self.mover.piece
        move = Move(Square(self.mover.initial_row, self.mover.initial_col), Square(final_row, final_col))
        if self.board.valid_moves(piece, move):
            self.board.move_piece(piece, move)
            if self.is_over():
                self.running = False
                return
            self.next_turn()
            self.mover.unpick_piece()
        elif self.board.state[final_row][final_col].is_empty():
            self.mover.unpick_piece()
    
    def make_ai_move(self):
        move = self.ai.eval(deepcopy(self.board))
        if move:
            piece = self.board.state[move.initial.row][move.initial.col].piece
            self.select_piece(piece, move.initial.row, move.initial.col)
            time.sleep(0.5)
            self.move_piece(move.final.row, move.final.col)
    
    def is_over(self):
        return self.board.final_state(self.player) != 0