from const import *
from board import Board
from square import Square
from piece import Piece
import random
import time
from typing import Dict, Tuple

class TranspositionTable:
    def __init__(self):
        # Initialize Zobrist keys for each piece type and position
        self.zobrist_keys = {
            'white_piece': [[random.getrandbits(64) for _ in range(COLS)] for _ in range(ROWS)],
            'black_piece': [[random.getrandbits(64) for _ in range(COLS)] for _ in range(ROWS)]
        }
        self.table: Dict[int, Tuple[float, int, str]] = {}  # hash -> (value, depth, flag)

    def get_zobrist_key(self, board: Board) -> int:
        """Calculate the Zobrist hash for the current board position"""
        h = 0
        for row in range(ROWS):
            for col in range(COLS):
                piece = board.state[row][col].piece
                if isinstance(piece, Piece):
                    piece_type = f"{'white' if piece.color == WHITE else 'black'}_{piece.__class__.__name__.lower()}"
                    if piece_type in self.zobrist_keys:
                        h ^= self.zobrist_keys[piece_type][row][col]
        return h

class AI:
    def __init__(self, level, color):
        self.level = level
        print("AI level: ", level)
        self.color = color
        self.player = -1 if color == BLACK else 1
        self.max_depth = level
        self.move_time = 0
        self.tt = TranspositionTable()

    def eval(self, board: Board):
        start_time = time.time()  # Start time tracking
        move = self._iterative_deepening(board, self.max_depth, self.player)
        time.sleep(1)
        self.move_time = time.time() - start_time  # Calculate time taken for move
        return move

    def _negamax(self, board: Board, depth, player, alpha=float('-inf'), beta=float('inf')):
        # Check transposition table
        tt_entry = None
        position_hash = self.tt.get_zobrist_key(board)

        if position_hash in self.tt.table:
            tt_entry = self.tt.table[position_hash]
            if tt_entry[1] >= depth:  # If stored position was searched to sufficient depth
                return tt_entry[0], None

        alpha_orig = alpha
        best_move = None
        best_value = float('-inf')

        if depth == 0:
            return self._quiescence_search(board, alpha, beta), None

        if board.final_state(self.color) != 0:
            return self._evaluate(board) * self.player, None

        legal_moves = []
        for row in range(ROWS):
            for col in range(COLS):
                piece = board.state[row][col].piece
                if isinstance(piece, Piece) and piece.value_sign == player:
                    piece.clear_moves()
                    board.calculate_moves(piece, row, col)
                    for move in piece.valid_moves:
                        legal_moves.append(move)

        # Simple move ordering: captures first
        legal_moves.sort(key=lambda m: board.state[m.final.row][m.final.col].piece is not None, reverse=True)

        for move in legal_moves:
            board.move_piece(move.initial.piece, move)
            value, _ = self._negamax(board, depth - 1, -player, -beta, -alpha)
            value = -value
            if value > best_value:
                best_value = value
                best_move = move
            board.undo_move(move)

            alpha = max(alpha, value)
            if alpha >= beta:
                break

        # Store position in transposition table
        flag = 'EXACT'
        if best_value <= alpha_orig:
            flag = 'UPPERBOUND'
        elif best_value >= beta:
            flag = 'LOWERBOUND'

        self.tt.table[position_hash] = (best_value, depth, flag)

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

    def _quiescence_search(self, board: Board, alpha: float, beta: float, depth: int = 0) -> float:
        """
        Quiescence search optimized for two piece types
        """
        stand_pat = self._evaluate(board) * self.player

        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat
        if depth > -3:  # Limit quiescence depth
            return stand_pat

        # Generate capturing moves only
        captures = []
        for row in range(ROWS):
            for col in range(COLS):
                piece = board.state[row][col].piece
                if isinstance(piece, Piece) and piece.value_sign == self.player:
                    piece.clear_moves()
                    board.calculate_moves(piece, row, col)
                    for move in piece.valid_moves:
                        if board.state[move.final.row][move.final.col].piece is not None:
                            captures.append(move)

        for move in captures:
            board.move_piece(move.initial.piece, move)
            score = -self._quiescence_search(board, -beta, -alpha, depth - 1)
            board.undo_move(move)

            if score >= beta:
                return beta
            if score > alpha:
                alpha = score

        return alpha

    #----------------------------------------#
    #---------- Evaluation methods ----------#
    # ---------------------------------------#

    def _evaluate(self, board: Board):
        """
        Enhanced evaluation function optimized for two piece types (black and white)
        """
        material_score = self._calculate_material(board)
        position_score = self._evaluate_positional_factors(board)
        mobility_score = self._evaluate_mobility(board)
        structure_score = self._evaluate_structure(board)
        king_safety_score = self._evaluate_king_safety(board)
        development_score = self._evaluate_development(board)
        control_score = self._evaluate_control(board)

        # Weighted combination of all factors
        final_score = (
                1.0 * material_score +
                0.7 * position_score +
                0.5 * mobility_score +
                0.5 * structure_score +
                0.8 * king_safety_score +
                0.4 * development_score +
                0.6 * control_score
        )

        # Terminal position bonus
        final_score += 10000 * -board.final_state(self.color)

        # Game phase adjustments
        game_phase = self._determine_game_phase(board)
        if game_phase == 'endgame':
            final_score += self._evaluate_piece_positioning(board) * 0.5

        return final_score

    @staticmethod
    def _evaluate_king_safety(board: Board):
        """Evaluates piece safety based on surrounding friendly pieces"""
        score = 0
        for row in range(ROWS):
            for col in range(COLS):
                piece = board.state[row][col].piece
                if isinstance(piece, Piece):
                    # Check surrounding pieces for protection
                    friendly_count = 0
                    for dr, dc in [(1, 0), (1, 1), (1, -1), (-1, 0), (-1, 1), (-1, -1), (0, 1), (0, -1)]:
                        new_row, new_col = row + dr, col + dc
                        if Square.in_range(new_row, new_col):
                            adjacent_piece = board.state[new_row][new_col].piece
                            if isinstance(adjacent_piece, Piece) and adjacent_piece.color == piece.color:
                                friendly_count += 1

                    # Bonus for having protecting pieces
                    score += friendly_count * 0.2 * piece.value_sign

        return score

    @staticmethod
    def _evaluate_development(board: Board):
        """Evaluates piece advancement and board control"""
        score = 0

        for row in range(ROWS):
            for col in range(COLS):
                piece = board.state[row][col].piece
                if isinstance(piece, Piece):
                    # Bonus for advanced pieces
                    if piece.color == WHITE:
                        score += (row / ROWS) * 0.3  # More points for advancing toward opponent's side
                    else:
                        score -= ((ROWS - 1 - row) / ROWS) * 0.3

                    # Control of key squares
                    if 2 <= row <= 5 and 2 <= col <= 5:
                        score += 0.3 * piece.value_sign

        return score

    @staticmethod
    def _evaluate_control(board: Board):
        """Evaluates control of key squares and lines"""
        score = 0
        controlled_squares = set()

        # Calculate controlled squares for both sides
        for row in range(ROWS):
            for col in range(COLS):
                piece = board.state[row][col].piece
                if isinstance(piece, Piece):
                    board.calculate_moves(piece, row, col)
                    for move in piece.valid_moves:
                        controlled_squares.add((move.final.row, move.final.col, piece.value_sign))

        # Score controlled squares
        for row, col, value_sign in controlled_squares:
            # Higher value for central squares
            if 2 <= row <= 5 and 2 <= col <= 5:
                score += 0.3 * value_sign
            else:
                score += 0.1 * value_sign

        return score

    @staticmethod
    def _determine_game_phase(board: Board):
        """Determines the current game phase based on piece count"""
        piece_count = 0
        for row in range(ROWS):
            for col in range(COLS):
                if isinstance(board.state[row][col].piece, Piece):
                    piece_count += 1

        if piece_count <= 6:
            return 'endgame'
        else:
            return 'midgame'

    @staticmethod
    def _evaluate_piece_positioning(board: Board):
        """Evaluates piece positioning, especially important in endgame"""
        score = 0
        for row in range(ROWS):
            for col in range(COLS):
                piece = board.state[row][col].piece
                if isinstance(piece, Piece):
                    # In endgame, centralized pieces are better
                    center_distance = abs(4 - row) + abs(4 - col)
                    score -= center_distance * 0.1 * piece.value_sign

                    # Bonus for pieces advanced toward opponent's side
                    if piece.color == WHITE:
                        score += row * 0.1
                    else:
                        score -= (ROWS - 1 - row) * 0.1
        return score

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