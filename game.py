import time
import pygame
from const import *
from board import Board
from move import Move
from mover import Mover
from ai import AI

class Game:
    def __init__(self):
        self.board = Board()
        self.mover = Mover()
        self.player = WHITE
        self.user_player = WHITE
        self.game_mode = 'pvc' # pvp (player v player) or pvc (player v computer)
        self.running = True
        self.white_time = 600  # 10 minutes in seconds
        self.black_time = 600  # 10 minutes in seconds
        self.last_tick = pygame.time.get_ticks()  # Track last tick for timing updates
        self.game_started = False  # Flag to track if the game has started

    def start_game(self):
        """Call this method after the user selects a player to start the game and timer."""
        self.game_started = True
        self.last_tick = pygame.time.get_ticks()  # Reset the last tick to start the timer

    def start_ai(self):
        self.ai = AI(1, BLACK if self.user_player == WHITE else WHITE)
 
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
        capture = False
        piece = self.mover.piece
        initial_square = self.board.state[self.mover.initial_row][self.mover.initial_col]
        final_square = self.board.state[final_row][final_col]

        if abs(initial_square.row - final_square.row) == 2:
            capture = True

        move = Move(initial_square, final_square, capture)

        if self.board.valid_moves(piece, move):
            self.board.move_piece(piece, move)

            if self.is_over():
                self.running = False
                return

            self.next_turn()  # Switch turn to the next player
            self.mover.unpick_piece()
    
    def make_ai_move(self):
        # start_time = pygame.time.get_ticks()
        move = self.ai.eval(self.board)
        if move:
            piece = self.board.state[move.initial.row][move.initial.col].piece
            self.select_piece(piece, move.initial.row, move.initial.col)
            self.move_piece(move.final.row, move.final.col)

            # Calculate AI move time and update the appropriate player's timer
            # ai_move_time = (pygame.time.get_ticks() - start_time) / 1000  # Time in seconds
            if self.player == BLACK:
                # self.white_time -= ai_move_time
                self.white_time -= self.ai.move_time
            else:
                # self.black_time -= ai_move_time
                self.black_time -= self.ai.move_time


    def is_over(self):
        return self.board.final_state(self.player) != 0