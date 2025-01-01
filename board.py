from const import *
from square import Square
from piece import Piece
from move import Move

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
        if move.capture:
            captured_row = (initial.row + final.row) // 2
            captured_col = (initial.col + final.col) // 2
            captured_piece = self.state[captured_row][captured_col].piece
            self.captured_pieces[WHITE if captured_piece.color == BLACK else BLACK].append(captured_piece)
            self.state[captured_row][captured_col].piece = None

        # Update board state
        self.state[initial.row][initial.col].piece = None
        self.state[final.row][final.col].piece = piece

        piece.clear_moves()
        self.move_history.append(move.convert_to_notation())
        self.state_history.append(self._get_state_hash())
        self.last_move = move

    def undo_move(self, move: Move):
        initial = move.initial
        final = move.final
        piece = self.state[final.row][final.col].piece

        # Check for capture and undo
        if move.capture:
            captured_row = (initial.row + final.row) // 2
            captured_col = (initial.col + final.col) // 2
            captured_piece = self.captured_pieces[piece.color].pop()
            self.state[captured_row][captured_col].piece = captured_piece

        # Undo the move in the baord state
        self.state[initial.row][initial.col].piece = piece
        self.state[final.row][final.col].piece = None

        # Remove from history
        idx = self.move_history.index(move.convert_to_notation())
        self.move_history.pop(idx)
        self.state_history.pop(idx)
        # Check if they are the first moves of the players
        if len(self.move_history) == 0:
            self.last_move = None
        elif len(self.move_history) == 1:
            self.last_move = Move.convert_to_move(self.move_history[0])
        else:
            self.last_move = Move.convert_to_move(self.move_history[-1])

    def valid_moves(self, piece, move):
        return move in piece.valid_moves
    
    def calculate_moves(self, piece: Piece, row, col):
        # Calculate all possible legal moves of a piece on a specific position
        # There are 5 legal moves a piece can perform, left, up, right, capture on the diagonal jumping over the opponent
        if isinstance(piece, Piece):
            direction = -1 if piece.color == WHITE else 1
            possible_moves = {
                'translation': [(row, col-direction), (row+direction, col), (row, col+direction)],
                'capture': [(row+direction, col-1), (row+direction, col+1)]
                }
            for name, possible_move in possible_moves.items():
                for possible_row, possible_col in possible_move:
                    if Square.in_range(possible_row, possible_col):
                        initial = self.state[row][col]
                        if self.state[possible_row][possible_col].has_opponent(piece.color) and name == 'capture':
                            # Calculate the landing square for capture
                            land_row = possible_row + direction
                            land_col = possible_col + (1 if possible_col > col else -1)
                            if Square.in_range(land_row, land_col) and self.state[land_row][land_col].is_empty():
                                final = self.state[land_row][land_col]
                                move = Move(initial, final, True)
                                if move not in piece.valid_moves:
                                    piece.add_moves(move) # append new legal moves to piece class
                        if self.state[possible_row][possible_col].is_empty() and name == 'translation':
                            # Calculate the landing square for movement
                            final = self.state[possible_row][possible_col]
                            move = Move(initial, final)
                            if move not in piece.valid_moves:
                                piece.add_moves(move)

    def _create(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.state[row][col] = Square(row, col)

    def _add_pieces(self):
        for col in range(COLS):
            self.state[0][col] = Square(0, col, Piece(BLACK))
            self.state[8][col] = Square(8, col, Piece(WHITE))

        self.state[1][1] = Square(1, 1, Piece(BLACK))
        self.state[1][7] = Square(1, 7, Piece(BLACK))
        self.state[2][2] = Square(2, 2, Piece(BLACK))
        self.state[2][6] = Square(2, 6, Piece(BLACK))
        self.state[3][3] = Square(3, 3, Piece(BLACK))
        self.state[3][5] = Square(3, 5, Piece(BLACK))

        self.state[7][1] = Square(7, 1, Piece(WHITE))
        self.state[7][7] = Square(7, 7, Piece(WHITE))
        self.state[6][2] = Square(6, 2, Piece(WHITE))
        self.state[6][6] = Square(6, 6, Piece(WHITE))
        self.state[5][3] = Square(5, 3, Piece(WHITE))
        self.state[5][5] = Square(5, 5, Piece(WHITE))

    def final_state(self, color):
        # Function to check win conditions and draw conditions
        # Returns a value depending on the outcome: no win(0), white wins(1), black wins(-1) or they draw(3),
        opponent = BLACK if color == WHITE else WHITE
        if self._check_win_condition(color) or self._check_no_pieces(opponent) or self._check_no_moves(opponent):
            return 1 if color == WHITE else -1
        elif self._check_threefold_repetition():
            return 0.000001
        else:
            return 0
    
    def _get_state_hash(self):
        return tuple(tuple(str(square) if isinstance(square.piece, Piece) else None for square in row) for row in self.state)

    def _check_threefold_repetition(self):
        if len(self.state_history) < 6:  # Need at least 6 moves for a threefold repetition
            return False
        current_state = self.state_history[-1]
        return self.state_history.count(current_state) >= 3
    
    def _check_win_condition(self, color):
        if color == WHITE:
            return any(isinstance(self.state[0][i].piece, Piece) and self.state[0][i].piece.color == WHITE for i in range(COLS))
        elif color == BLACK:
            return any(isinstance(self.state[8][i].piece, Piece) and self.state[8][i].piece.color == BLACK for i in range(COLS))
    
    def _check_no_moves(self, color):
        for row in range(ROWS):
            for col in range(ROWS):
                piece = self.state[row][col].piece
                if isinstance(piece, Piece) and piece.color == color:
                    self.calculate_moves(piece, row, col)
                    if piece.valid_moves:
                        return False
        return True

    def _check_no_pieces(self, color):
        return not any(isinstance(square.piece, Piece) and square.piece.color == color for row in self.state for square in row)