from fianco_game import FiancoGame
import numpy as np
from typing import Tuple
class FiancoAI():
    def __init__(self) -> None:
        pass

    def negamax(self, game: FiancoGame, depth: int, alpha: float, beta: float, color: int) -> float:
    # Negamax algorithm for AI move evaluation
        if depth == 0 or game.is_terminal():
            return color * game.evaluate()

        max_value = float('-inf')
        for move in game.get_possible_moves(game.current_player):
            game_copy = FiancoGame()
            game_copy.board = np.copy(game.board)
            game_copy.current_player = game.current_player
            game_copy.make_move(move)
            value = -self.negamax(game_copy, depth - 1, -beta, -alpha, -color)
            max_value = max(max_value, value)
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return max_value

    def get_ai_move(self, game: FiancoGame, depth: int) -> Tuple[int, int, int, int]:
        # Get the best move for the AI using the negamax algorithm
        best_move = None
        best_value = float('-inf')
        for move in game.get_possible_moves(game.current_player):
            game_copy = FiancoGame()
            game_copy.board = np.copy(game.board)
            game_copy.current_player = game.current_player
            game_copy.make_move(move)
            value = -self.negamax(game_copy, depth - 1, float('-inf'), float('inf'), -1)
            if value > best_value:
                best_value = value
                best_move = move
        return best_move