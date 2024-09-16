import math
from fianco_game import FiancoGame

def negamax_alpha_beta(game: FiancoGame, depth, alpha, beta, color):
    if depth == 0 or game.is_game_over():
        return color * evaluate(game)

    max_eval = -math.inf
    for move in game.get_valid_moves():
        game.make_move(*move)
        _eval = -negamax_alpha_beta(game, depth - 1, -beta, -alpha, -color)
        # game.undo_move(*move)  # Assuming we implement an undo_move method
        game.undo_move()
        max_eval = max(max_eval, _eval)
        alpha = max(alpha, _eval)
        if alpha >= beta:
            break
    return max_eval

def evaluate(game: FiancoGame):
    # This is a simple evaluation function. You might want to improve it.
    player1_score = sum(1 for x in range(9) for y in range(9) if game.board[x, y] == 1)
    player2_score = sum(1 for x in range(9) for y in range(9) if game.board[x, y] == 2)
    return player1_score - player2_score

def get_best_move(game: FiancoGame, depth):
    best_move = None
    max_eval = -math.inf
    alpha = -math.inf
    beta = math.inf
    for move in game.get_valid_moves():
        game.make_move(*move)
        _eval = -negamax_alpha_beta(game, depth - 1, -beta, -alpha, -1)
        # game.undo_move(*move)
        game.undo_move()
        if _eval > max_eval:
            max_eval = _eval
            best_move = move
        alpha = max(alpha, _eval)
    return best_move