from const import *
from square import Square
from piece import Piece, Circle
from move import Move
import numpy as np

class Board:
    def __init__(self):
        self.state = [[0,0,0,0,0,0,0,0,0] for _ in range(COLS)]
        self.last_move = None
        self.captured_pieces = {WHITE: [], BLACK: []}
        self.state_history = []
        self.move_history = []
        self._create()
        self._add_pieces()
    
    def move_piece(self, piece: Piece, move: Move):
        initial = move.initial
        final = move.final

        # Check for capture
        capture = False
        if abs(initial.row - final.row) == 2:
            captured_row = (initial.row + final.row) // 2
            captured_col = (initial.col + final.col) // 2
            captured_piece = self.state[captured_row][captured_col].piece
            self.captured_pieces[WHITE if captured_piece.color == BLACK else BLACK].append(captured_piece)
            self.state[captured_row][captured_col].piece = None
            capture = True

        # Update board state
        self.state[initial.row][initial.col].piece = None
        self.state[final.row][final.col].piece = piece

        piece.moved = True
        piece.clear_moves()
        self.move_history.append(move.convert_to_notation(capture))
        self.last_move = move
        print('Move History ', self.move_history)
        self.state_history.append(self._get_state_hash())
    
    def undo_move(self):
        initial = self.last_move.initial
        final = self.last_move.final
        piece = self.state[final.row][final.col].piece

        # Check for capture
        if abs(initial.row - final.row) == 2:
            captured_row = (initial.row + final.row) // 2
            captured_col = (initial.col + final.col) // 2
            captured_piece = self.captured_pieces[piece.color].pop()
            self.state[captured_row][captured_col].piece = captured_piece

        # Undo the move in the baord state
        self.state[initial.row][initial.col].piece = piece
        self.state[final.row][final.col].piece = None

        # Remove last element
        self.move_history.pop()
        self.state_history.pop()
        # Check if they are the first moves of the players
        if len(self.move_history) == 0:
            piece.moved = False
            self.last_move = None
        elif len(self.move_history) == 1:
            piece.moved = False
            self.last_move = Move.convert_to_move(self.move_history[0])
        else:
            self.last_move = Move.convert_to_move(self.move_history[-1])
        piece.clear_moves()

    def valid_moves(self, piece, move):
        return move in piece.valid_moves
    
    def calculate_moves(self, piece: Piece, row, col):
        # Calculate all possible legal moves of of a piece on a specific position
        # There are 5 legal moves a piece can perform, left, up, right, capture on the diagonal jumping over the opponent
        if isinstance(piece, Circle):
            pssible_moves = {
                'translation': [(row, col-piece.direction), (row+piece.direction, col), (row, col+piece.direction)],
                'capture': [(row+piece.direction, col-1), (row+piece.direction, col+1)]
                }
            for name, possible_move in pssible_moves.items():
                for possible_row, possible_col in possible_move:
                    if Square.in_range(possible_row, possible_col):
                        initial = Square(row, col)
                        if self.state[possible_row][possible_col].has_opponent(piece.color) and name == 'capture':
                            # Calculate the landing square for capture
                            capture_row = possible_row + piece.direction
                            capture_col = possible_col + (1 if possible_col > col else -1)
                            if Square.in_range(capture_row, capture_col) and self.state[capture_row][capture_col].is_empty():
                                final = Square(capture_row, capture_col)
                                move = Move(initial, final)
                                piece.add_moves(move) # append new legal moves to piece class
                        if self.state[possible_row][possible_col].is_empty() and name == 'translation':
                            # Calculate the landing square for movement
                            final = Square(possible_row, possible_col)
                            move = Move(initial, final)
                            piece.add_moves(move)
    
    def final_state(self, color=WHITE):
        # Function to check win conditions and draw conditions
        # Returns a value depending on the outcome: no win(0), white wins(1), black wins(2) or they draw(3),
        opponent = BLACK if color == WHITE else WHITE
        if self._check_win_condition(color) or self._check_no_pieces(opponent) or self._check_no_moves(opponent):
            return 1 if color == WHITE else 2
        elif self._check_threefold_repetition():
            return 3
        else:
            return 0       

    def _create(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.state[row][col] = Square(row, col)

    def _add_pieces(self):
        for col in range(COLS):
            self.state[0][col] = Square(0, col, Circle(BLACK))
            self.state[8][col] = Square(8, col, Circle(WHITE))

        self.state[1][1] = Square(1, 1, Circle(BLACK))
        self.state[1][7] = Square(1, 7, Circle(BLACK))
        self.state[2][2] = Square(2, 2, Circle(BLACK))
        self.state[2][6] = Square(2, 6, Circle(BLACK))
        self.state[3][3] = Square(3, 3, Circle(BLACK))
        self.state[3][5] = Square(3, 5, Circle(BLACK))

        self.state[7][1] = Square(7, 1, Circle(WHITE))
        self.state[7][7] = Square(7, 7, Circle(WHITE))
        self.state[6][2] = Square(6, 2, Circle(WHITE))
        self.state[6][6] = Square(6, 6, Circle(WHITE))
        self.state[5][3] = Square(5, 3, Circle(WHITE))
        self.state[5][5] = Square(5, 5, Circle(WHITE))
    
    def _get_state_hash(self):
        return tuple(tuple(str(square) if square.piece != None else None for square in row) for row in self.state)
    
    def _check_threefold_repetition(self):
        if len(self.state_history) < 6:  # Need at least 6 moves for a threefold repetition
            return False
        current_state = self.history[-1]
        return self.state_history.count(current_state) >= 3
    
    def _check_win_condition(self, color):
        if color == WHITE:
            return any(isinstance(self.state[0][i], Circle) and self.state[0][i].color == WHITE for i in range(ROWS))
        else:
            return any(isinstance(self.state[8][i], Circle) and self.state[8][i].color == BLACK for i in range(ROWS))
    
    def _check_no_moves(self, color):
        for row in range(ROWS):
            for col in range(ROWS):
                piece = self.state[row][col].piece
                if isinstance(piece, Circle) and piece.color == color:
                    if piece.valid_moves:
                        return False
        return True

    def _check_no_pieces(self, color):
        return not any(isinstance(piece, Piece) and piece.color == color for row in self.state for piece in row)