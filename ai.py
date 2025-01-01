from traits.trait_types import self

from const import *
from board import Board
from square import Square
from piece import Piece
import random
from copy import deepcopy

class AI:
    def __init__(self, level=0, color=BLACK):
        self.level = level
        self.color = color
        self.player = -1 if color == BLACK else 1
        self.max_depth = 3

    def eval(self, board: Board):
        if self.level == 0:
            return self._find_random_move(board)
        else:
            _, best_move = self._negamax(board, self.max_depth, self.player)
            return best_move
        
    def _negamax(self, board: Board, depth, player, alpha=float('-inf'), beta=float('inf')):
        best_move = None
        best_value = float('-inf')

        if depth == 0 or board.final_state() != 0:
            return self._evaluate(board) * self.player, None

        # Get all the legal moves
        legal_moves = []
        for row in range(ROWS):
            for col in range(COLS):
                piece = board.state[row][col].piece
                if isinstance(piece, Piece) and piece.value_sign == player:
                    piece.clear_moves()
                    board.calculate_moves(piece, row, col)
                    for move in piece.valid_moves:
                        legal_moves.append(move)

        for move in legal_moves:
            board.move_piece(move.initial.piece, move)
            value, _ = self._negamax(board, depth - 1, -player, -beta, -alpha)
            print(move.convert_to_notation(), value)
            value = -value
            if value > best_value:
                best_value = value
                best_move = move
            board.undo_move(move)

            alpha = max(alpha, value)
            if alpha >= beta:
                break  # Beta cutoff

        return best_value, best_move

    def _find_random_move(self, board: Board):
        all_possible_moves = []
        move=None
        for i in range(ROWS):
            for j in range(COLS):
                piece = board.state[i][j].piece
                if isinstance(piece, Piece) and piece.color == self.color:
                    board.calculate_moves(piece, i, j)
                    for move in piece.valid_moves:
                        all_possible_moves.append(move)
                    piece.clear_moves()
        if all_possible_moves:
            move = random.choice(all_possible_moves)
        return move
    
    # Evaluation methods
        
    def _evaluate(self, board: Board):
        """
        Evaluates a Fianco position from the given perspective.
        Returns a score where positive is good for white, negative is good for black
        """
        material_score = self._calculate_material(board)
        position_score = self._evaluate_positional_factors(board)
        mobility_score = self._evaluate_mobility(board)
        structure_score = self._evaluate_structure(board)
        
        final_score = (1.0 * material_score + 0.6 * position_score + 0.4 * mobility_score + 0.5 * structure_score)
        final_score += 10000 * -board.final_state(self.color)
        
        return final_score

    @staticmethod
    def _calculate_material(board: Board):
        # Calculate the material balance
        score = 0
        for row in range(ROWS):
            for col in range(COLS):
                piece = board.state[row][col].piece
                if isinstance(piece, Piece):
                    score += piece.value
        return score

    @staticmethod
    def _evaluate_positional_factors(board: Board):
        # Evaluate positional factors
        score = 0
        
        # Center control bonus (inner 4x4)
        center_bonus = 0.2
        for row in range(2, 6):
            for col in range(2, 6):
                piece = board.state[row][col].piece
                if isinstance(piece, Piece):
                    score += center_bonus * piece.value_sign         
        
        # Edge penalty
        edge_penalty = 0.1
        for row in range(ROWS):
            for col in [0, 8]:
                piece = board.state[row][col].piece
                if isinstance(piece, Piece):
                    score -= edge_penalty * piece.value_sign
        
        for col in range(COLS):
            for row in [0, 8]:
                piece = board.state[row][col].piece
                if isinstance(piece, Piece):
                    score -= edge_penalty * piece.value_sign
                    
        return score

    @staticmethod
    def _evaluate_mobility(board: Board):
        # Evaluate piece mobility - pieces with more available moves are worth more
        score = 0        
        for row in range(ROWS):
            for col in range(COLS):
                piece = board.state[row][col].piece
                if isinstance(piece, Piece):
                    board.calculate_moves(piece, row, col)
                    moves = len(piece.valid_moves)
                    score += moves * 0.05 * piece.value_sign
        return score

    @staticmethod
    def _evaluate_structure(board: Board):
        # Evaluate piece structure - connected pieces support each other
        score = 0
        directions = [(1,0), (-1,0), (0,1), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)]
        
        for row in range(ROWS):
            for col in range(COLS):
                piece = board.state[row][col].piece
                if isinstance(piece, Piece):
                    supporters = 0
                    for dr, dc in directions:
                        new_row, new_col = row + dr, col + dc
                        if Square.in_range(new_row, new_col) and isinstance(board.state[new_row][new_col].piece, Piece):
                            supporters += 1
                    
                    support_bonus = supporters * 0.1
                    score += support_bonus * piece.value_sign
                        
        return score