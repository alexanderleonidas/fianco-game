import pygame
from piece import Piece
from constants import *

class Board:
    def __init__(self, width, height):
        self.state = [[EMPTY_SPACE] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.width = width
        self.height = height
        self.board_surface = pygame.Surface((SQUARE_SIZE * BOARD_SIZE, SQUARE_SIZE * BOARD_SIZE))
        self.init_state()
        self.history = []
        self.move_history = []
        self.highlight_squares = []
    
    def init_state(self):
        for i in range(BOARD_SIZE):
            self.state[0][i] = Piece(0, i, BLACK)
            self.state[8][i] = Piece(8, i, WHITE)

        self.state[1][1] = Piece(1, 1, BLACK)
        self.state[1][7] = Piece(1, 7, BLACK)
        self.state[2][2] = Piece(2, 2, BLACK)
        self.state[2][6] = Piece(2, 6, BLACK)
        self.state[3][3] = Piece(3, 3, BLACK)
        self.state[3][5] = Piece(3, 5, BLACK)

        self.state[7][1] = Piece(7, 1, WHITE)
        self.state[7][7] = Piece(7, 7, WHITE)
        self.state[6][2] = Piece(6, 2, WHITE)
        self.state[6][6] = Piece(6, 6, WHITE)
        self.state[5][3] = Piece(5, 3, WHITE)
        self.state[5][5] = Piece(5, 5, WHITE)
        
    def draw_squares(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
                pygame.draw.rect(self.board_surface, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def draw(self, screen):
        self.draw_squares()
        self.draw_highlights()
        self.draw_notation()
        for row in range(BOARD_SIZE): 
            for col in range(BOARD_SIZE):
                piece = self.state[row][col]
                if piece != EMPTY_SPACE:
                    piece.draw(self.board_surface)
                    
        # screen.blit(self.board_surface, ((WIDTH - BOARD_WIDTH) // 2, (HEIGHT - BOARD_HEIGHT) // 2))
        screen.blit(self.board_surface, (0, 0))


    def draw_highlights(self):
        highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        highlight_surface.fill(HIGHLIGHT_COLOR)
        for row, col in self.highlight_squares:
            self.board_surface.blit(highlight_surface, (col * SQUARE_SIZE, row * SQUARE_SIZE))
    
    def draw_notation(self):
        font = pygame.font.Font(None, 24)
        for i in range(BOARD_SIZE):
            # Draw row numbers
            text = font.render(str(BOARD_SIZE - i), True, BLACK)
            self.board_surface.blit(text, (5, i * SQUARE_SIZE + 5))
            # Draw column letters
            text = font.render(chr(97 + i), True, BLACK)
            self.board_surface.blit(text, (i * SQUARE_SIZE + SQUARE_SIZE - 20, BOARD_HEIGHT - 20))

    def get_valid_moves(self, piece):
        moves = []
        captures = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # Right, Left, Down, Up
        capture_directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]  # Diagonal captures

        for dx, dy in directions:
            new_row, new_col = piece.row + dx, piece.col + dy
            if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:
                if self.state[new_row][new_col] == EMPTY_SPACE:
                    # White or black can't move backwards
                    if piece.color == WHITE and dx <= 0 or piece.color == BLACK and dx >= 0:
                        moves.append((new_row, new_col))

        for dx, dy in capture_directions:
            new_row, new_col = piece.row + 2*dx, piece.col + 2*dy
            if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:
                if self.state[new_row][new_col] == EMPTY_SPACE:
                    middle_row, middle_col = piece.row + dx, piece.col + dy
                    if self.state[middle_row][middle_col] != EMPTY_SPACE and self.state[middle_row][middle_col].color != piece.color:
                        # White and black can only capture forward
                        if piece.color == WHITE and dx < 0 or piece.color == BLACK and dx > 0:  
                            captures.append((new_row, new_col))

        return captures if captures else moves

    def move_piece(self, piece, new_row, new_col):
        old_row, old_col = piece.row, piece.col
        self.state[old_row][old_col] = EMPTY_SPACE
        piece.row, piece.col = new_row, new_col
        self.state[new_row][new_col] = piece
        piece.translate_board_to_pixel_coord()

        # Check if it's a capture move
        capture = False
        if abs(new_row - old_row) == 2:
            captured_row = (old_row + new_row) // 2
            captured_col = (old_col + new_col) // 2
            self.state[captured_row][captured_col] = EMPTY_SPACE
            capture = True

        # Add move to history using chess notation
        self.move_history.append(self.get_move_notation(old_col, old_row, new_col, new_row, capture))

        # Add the current state to history
        self.history.append(self.get_state_hash())
    
    def get_move_notation(self, from_col, from_row, to_col, to_row, capture):
        from_square = chr(97 + from_col) + str(BOARD_SIZE - from_row)
        to_square = chr(97 + to_col) + str(BOARD_SIZE - to_row)
        if capture:
            return f"{from_square}x{to_square}"
        else:
            return f"{from_square}-{to_square}"

    def get_state_hash(self):
        return tuple(tuple(str(cell) if cell != EMPTY_SPACE else EMPTY_SPACE for cell in row) for row in self.state)

    def check_threefold_repetition(self):
        if len(self.history) < 6:  # Need at least 6 moves for a threefold repetition
            return False
        current_state = self.history[-1]
        return self.history.count(current_state) >= 3

    def check_win_condition(self, color):
        if color == WHITE:
            return any(isinstance(self.state[0][i], Piece) and self.state[0][i].color == WHITE for i in range(BOARD_SIZE))
        else:
            return any(isinstance(self.state[8][i], Piece) and self.state[8][i].color == BLACK for i in range(BOARD_SIZE))

    def check_no_moves(self, color):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.state[row][col]
                if isinstance(piece, Piece) and piece.color == color:
                    if self.get_valid_moves(piece):
                        return False
        return True

    def check_no_pieces(self, color):
        return not any(isinstance(piece, Piece) and piece.color == color for row in self.state for piece in row)
