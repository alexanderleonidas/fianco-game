from const import *
from board import Board
import math
from copy import deepcopy

class AI():
    def __init__(self, level=0, player=BLACK):
        self.level = level
        self.player = player
        self.max_depth = 4

    def negamax(self, board: Board, depth, alpha, beta, color):
        if depth == 0:
            return color * self.eval()  # Assuming higher values are better for the current player
        elif board.final_state(WHITE) == 1:
            return 1 # Player 1 wins
        elif board.final_state(BLACK) == 2:
            return -1 # Player 2 wins
        elif board.final_state() == 3:
            return 1 # Draw but considered as loss

        max_value = float('-inf')
        for i in range(ROWS):
            for j in range(COLS):
                piece = board.state[i][j].piece
                if piece != None:
                    board.calculate_moves(piece, i, j)
                    possible_moves = piece.valid_moves
                    for move in possible_moves:
                        board.move_piece(piece, move)
                        value = -self.negamax(board, depth - 1, -beta, -alpha, -color)
                        board.undo_move(move)

                        max_value = max(max_value, value)
                        alpha = max(alpha, value)

                        if alpha >= beta:
                            break  # Beta cutoff

        return max_value

    def find_best_move(self, board: Board, color):
        copy_board = deepcopy(board)
        best_move = None
        best_value = float('-inf')
        alpha = float('-inf')
        beta = float('inf')

        for i in range(ROWS):
            for j in range(COLS):
                piece = copy_board.state[i][j].piece
                if piece != None:
                    copy_board.calculate_moves(piece, i, j)
                    possible_moves = piece.valid_moves
                    for move in possible_moves:
                        copy_board.move_piece(piece, move)
                        value = -self.negamax(board, self.max_depth - 1, -beta, -alpha, -color)
                        board.undo_move(move)

                        if value > best_value:
                            best_value = value
                            best_move = move

                        alpha = max(alpha, value)

        return best_move
    
    def eval(self):
        if self.level == 0:
            # Random choice
            pass
        else:
            # Negamax
            pass