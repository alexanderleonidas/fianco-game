import pygame
from constants import *

BLACK = (0, 0, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GRAY = (185, 185, 185)


class Piece():
    def __init__(self, row, col, color) -> None:
        self.col = col
        self.row = row
        self.pixel_row = 0
        self.pixel_col = 0
        self.color = color
        self.selected = False
        self.translate_board_to_pixel_coord()
    
    def draw(self, surface):
        if self.selected:
            pygame.draw.circle(surface, RED, (self.pixel_col, self.pixel_row), SQUARE_SIZE//2-12)
        elif self.color == BLACK:
            pygame.draw.circle(surface, GRAY, (self.pixel_col, self.pixel_row), SQUARE_SIZE//2-12)
        elif self.color == WHITE:
            pygame.draw.circle(surface, BLACK, (self.pixel_col, self.pixel_row), SQUARE_SIZE//2-12)
        pygame.draw.circle(surface, self.color, (self.pixel_col, self.pixel_row), SQUARE_SIZE//2-15)
    
    def translate_board_to_pixel_coord(self):
        self.pixel_col = self.col * SQUARE_SIZE + SQUARE_SIZE // 2
        self.pixel_row = self.row * SQUARE_SIZE + SQUARE_SIZE // 2
    
    def select(self, selected=True):
        self.selected = selected

    def __str__(self):
        return f"{self.color}_{self.row}_{self.col}"