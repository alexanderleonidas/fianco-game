import time
import pygame
from const import *
from board import Board
from move import Move
from mover import Mover
from square import Square
from ai import AI

class Game:
    def __init__(self):
        self.board = Board()
        self.mover = Mover()
        self.player = WHITE
        self.ai = AI()
        self.game_mode = 'pvp' # pvp or ai

    def next_turn(self):
        self.player = WHITE if self.player == BLACK else BLACK
    
    def reset(self):
        self.__init__()
    
    def select_piece(self, piece, pos, row: int, col: int):
        if piece.color == self.player:
            self.board.calculate_moves(piece, row, col)
            self.mover.save_initial(pos)
            self.mover.pick_piece(piece)
    
    def move_piece(self, final_row: int, final_col: int):
        piece = self.mover.piece
        move = Move(Square(self.mover.initial_row, self.mover.initial_col), Square(final_row, final_col))
        if self.board.valid_moves(piece, move):
            self.board.move_piece(piece, move)
            self.next_turn()
            self.mover.unpick_piece()
        elif self.board.state[final_row][final_col].is_empty():
            self.mover.unpick_piece()
    
    def unmove_piece(self):
        self.board.undo_move()
        self.next_turn()
    
    def show_last_move(self, surface):
        if self.board.last_move:
            initial = self.board.last_move.initial
            final = self.board.last_move.final

            for pos in [initial, final]:
                color = NEON_GREEN if (pos.row + pos.col) % 2 == 0 else DARK_NEON_GREEN
                rect = (pos.col * SQUARE_SIZE, pos.row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                pygame.draw.rect(surface, color, rect)

    def show_background(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                if (row + col) % 2 == 0:
                    color = LIGHT_GREEN
                else:
                    color = DARK_GREEN
                rect = (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                pygame.draw.rect(surface, color, rect)
        
                # row coordinates
                if col == 0:
                    color = BLACK if row % 2 == 0 else GRAY
                    lbl = pygame.font.SysFont('monospace', 18, bold=True).render(str(ROWS-row), 1, color)
                    lbl_pos = (5, 5 + row * SQUARE_SIZE)
                    surface.blit(lbl, lbl_pos)

                # col coordinates
                if row == 8:
                    # color
                    color = BLACK if (row + col) % 2 == 0 else GRAY
                    # label
                    lbl = pygame.font.SysFont('monospace', 18, bold=True).render(Square.get_alphacol(col), 1, color)
                    lbl_pos = (col * SQUARE_SIZE + SQUARE_SIZE - 20, HEIGHT - 20)
                    # blit
                    surface.blit(lbl, lbl_pos)
    
    def show_moves(self, surface):
        if self.mover.selected:
            piece = self.mover.piece
            for move in piece.valid_moves:
                color = '#C86464' if (move.final.row + move.final.col) % 2 == 0 else '#C84646'
                rect = (move.final.col * SQUARE_SIZE, move.final.row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                pygame.draw.rect(surface, color, rect)

    def show_pieces(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                if self.board.state[row][col].has_piece():
                    color = self.board.state[row][col].piece.color
                    center = col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2
                    self._draw_piece(surface, color, center, self.mover.piece == self.board.state[row][col].piece)
    
    def _draw_piece(self, surface, color, center, selected):
        if selected:
            pygame.draw.circle(surface, RED, center, SQUARE_SIZE//2-12)
        elif color == BLACK:
            pygame.draw.circle(surface, GRAY, center, SQUARE_SIZE//2-12)
        elif color == WHITE:
            pygame.draw.circle(surface, BLACK, center, SQUARE_SIZE//2-12)
        pygame.draw.circle(surface, color, center, SQUARE_SIZE//2-15)