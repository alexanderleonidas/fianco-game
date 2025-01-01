from const import *
from board import Board
from square import Square
from piece import Piece
import random
import time

class AI:
    def __init__(self, level, color):
        self.level = level
        self.color = color
        self.player = -1 if color == BLACK else 1
        self.max_depth = 3
        self.move_time = 0

    def eval(self, board: Board):
        start_time = time.time()  # Start time tracking
        if self.level == 0:
            move = self._find_random_move(board)
        else:
            move = self._iterative_deepening(board, self.max_depth, self.player)
        time.sleep(1)
        self.move_time = time.time() - start_time  # Calculate time taken for move
        return move
        
    def _negamax(self, board: Board, depth, player, alpha=float('-inf'), beta=float('inf')):
        best_move = None
        best_value = float('-inf')

        if depth == 0 or board.final_state(self.color) != 0:
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

        # Order moves: prioritize captures
        legal_moves.sort(key=lambda m: 'x' in str(m), reverse=True)

        for move in legal_moves:
            board.move_piece(move.initial.piece, move)
            value, _ = self._negamax(board, depth - 1, -player, -beta, -alpha)
            # print(move.convert_to_notation(), value)
            value = -value
            if value > best_value:
                best_value = value
                best_move = move
            board.undo_move(move)

            alpha = max(alpha, value)
            if alpha >= beta:
                break  # Beta cutoff

        return best_value, best_move

    def _iterative_deepening(self, board: Board, max_depth, player):
        best_move = None
        for depth in range(1, max_depth + 1):
            print(f"Searching depth: {depth}")
            start_time = time.time()  # Record the start time for each depth
            best_value, best_move = self._negamax(board, depth, player)
            end_time = time.time()  # Record the end time for each depth

            # Calculate the elapsed time for this depth
            elapsed_time = end_time - start_time
            print(
                f"Depth {depth}: Best move: {best_move.convert_to_notation() if best_move else 'None'} "
                f"with value {best_value}. Time taken: {elapsed_time:.4f} seconds"
            )
        return best_move

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

        # time_factor = self._evaluate_time()
        
        final_score = (1.0 * material_score + 0.6 * position_score + 0.4 * mobility_score + 0.5 * structure_score)
        final_score += 10000 * -board.final_state(self.color) # Bonus for terminal move
        
        return final_score

    # def _evaluate_time(self):
    #     """
    #     Evaluates based on the AI's remaining time.
    #     Returns a bonus/penalty score based on how much time the AI has left.
    #     """
    #     # Assume the game object tracks time remaining for each player
    #     if self.color == WHITE:
    #         time_left = self.game.white_time
    #         opponent_time_left = self.game.black_time
    #     else:
    #         time_left = self.game.black_time
    #         opponent_time_left = self.game.white_time
    #
    #     # Time bonus: If the AI has more time than the opponent, add a positive bonus
    #     time_bonus = (time_left - opponent_time_left) * 0.1  # Adjust the 0.1 factor as needed
    #
    #     return time_bonus

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