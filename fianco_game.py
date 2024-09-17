from typing import Tuple, List, Optional
from collections import Counter 
from player import Player
import numpy as np

class FiancoGame:
    def __init__(self):
        # Initialize the game board as a 9x9 numpy array
        self.board = np.zeros((9, 9), dtype=int)
        self._setup_board()
        self.current_player = Player.WHITE
        self.move_count = 0
        self.ai_time = 0
        self.game_history = []
        self.position_history = []

    def _setup_board(self):
        # Set up the initial board configuration
        # Black pieces (top of the board)
        self.board[0, :] = Player.BLACK.value
        self.board[1, [1, 7]] = Player.BLACK.value
        self.board[2, [2, 6]] = Player.BLACK.value
        self.board[3, [3, 5]] = Player.BLACK.value

        # White pieces (bottom of the board)
        self.board[8, :] = Player.WHITE.value
        self.board[7, [1, 7]] = Player.WHITE.value
        self.board[6, [2, 6]] = Player.WHITE.value
        self.board[5, [3, 5]] = Player.WHITE.value

    def get_possible_moves(self, player: Player) -> List[Tuple[int, int, int, int]]:
        # Get all possible moves for the given player
        moves = []
        captures = []
        for i, j in np.ndindex(self.board.shape):
            if self.board[i][j] == player.value:
                moves.extend(self._get_regular_moves(i, j, player))
                captures.extend(self._get_capture_moves(i, j, player))
        # Prioritize captures over regular moves
        return captures if captures else moves

    def _get_regular_moves(self, i: int, j: int, player: Player) -> List[Tuple[int, int, int, int]]:
        # Get regular moves for a piece (forward and sideways)
        directions = [(0, -1), (0, 1)]  # Sideways moves
        directions.append((-1, 0) if player == Player.WHITE else (1, 0))  # Forward move
        return [
            (i, j, i + di, j + dj)
            for di, dj in directions
            if 0 <= i + di < 9 and 0 <= j + dj < 9 and self.board[i + di][j + dj] == 0
        ]

    def _get_capture_moves(self, i: int, j: int, player: Player) -> List[Tuple[int, int, int, int]]:
        # Get capture moves for a piece (diagonal forward jumps)
        capture_directions = [(2, 2), (2, -2)] if player == Player.WHITE else [(-2, 2), (-2, -2)]
        return [
            (i, j, i + di, j + dj)
            for di, dj in capture_directions
            if (0 <= i + di < 9 and 0 <= j + dj < 9 and
                self.board[i + di][j + dj] == 0 and
                self.board[i + di // 2][j + dj // 2] == Player(3 - player.value).value)
        ]

    def make_move(self, move: Tuple[int, int, int, int]):
        # Execute a move on the board
        start_i, start_j, end_i, end_j = move
        self.board[end_i][end_j] = self.board[start_i][start_j]
        self.board[start_i][start_j] = 0

        if abs(start_i - end_i) == 2:  # Capture move
            capture_i, capture_j = (start_i + end_i) // 2, (start_j + end_j) // 2
            self.board[capture_i][capture_j] = 0

        self.game_history.append(move)
        self.current_player = Player(3 - self.current_player.value)
        self.move_count += 1

        # Add current board position to position history
        self.position_history.append(self._get_board_state())

    def is_terminal(self) -> bool:
        # Check if the game has ended
        return (
            self._player_reached_opposite_side() or
            self._player_has_no_pieces() or
            not self.get_possible_moves(self.current_player) or
            self.is_threefold_repetition()
        )

    def _get_board_state(self) -> Tuple[Tuple[int, ...], ...]:
        # Convert the board to a hashable type (tuple of tuples)
        return tuple(tuple(row) for row in self.board)

    def is_threefold_repetition(self) -> bool:
        # Check if the current position has occurred three times
        return Counter(self.position_history)[self._get_board_state()] >= 3
    
    def _player_reached_opposite_side(self) -> bool:
        # Check if any player has reached the opposite side of the board
        return Player.WHITE.value in self.board[0, :] or Player.BLACK.value in self.board[8, :]

    def _player_has_no_pieces(self) -> bool:
        # Check if any player has no pieces left on the board
        return Player.WHITE.value not in self.board or Player.BLACK.value not in self.board

    def get_winner(self) -> Optional[Player]:
        # Determine the winner of the game, if any
        if self.is_threefold_repetition():
            return None  # It's a draw
        if Player.WHITE.value in self.board[0, :]:
            return Player.WHITE
        if Player.BLACK.value in self.board[8, :]:
            return Player.BLACK
        if Player.WHITE.value not in self.board:
            return Player.BLACK
        if Player.BLACK.value not in self.board:
            return Player.WHITE
        if not self.get_possible_moves(self.current_player):
            return Player(3 - self.current_player.value)
        return None

    def validate_move(self, move: Tuple[int, int, int, int]) -> bool:
        # Check if a given move is valid
        possible_moves = self.get_possible_moves(self.current_player)
        return move in possible_moves
    
    def evaluate(self) -> int:
        winner = self.get_winner()
        if winner == self.current_player:
            return 1000
        elif winner == 3 - self.current_player.value:
            return -1000
        
        # Improved evaluation function
        player1_score = 0
        player2_score = 0
        for y in range(9):
            for x in range(9):
                if self.board[y, x] == Player.WHITE.value:
                    player1_score += 10 + (8 - y)  # More value for advanced pieces
                elif self.board[y, x] == Player.BLACK.value:
                    player2_score += 10 + y  # More value for advanced pieces
        
        # Add bonus for controlling the center
        center_control = np.sum(self.board[3:6, 3:6] == 1) - np.sum(self.board[3:6, 3:6] == 2)
        player1_score += center_control * 5
        player2_score -= center_control * 5

        return player1_score - player2_score if self.current_player == Player.WHITE else player2_score - player1_score

    def print_board(self):
        # Print the current board state
        bold_start, bold_end = "\033[1m", "\033[0m"
        print("    A   B   C   D   E   F   G   H   I")
        print("  +---+---+---+---+---+---+---+---+---+")
        for i in range(9):
            row = f"{9 - i} | "
            for j in range(9):
                if self.board[i, j] == Player.WHITE.value:
                    row += f'{bold_start}W{bold_end} | '
                elif self.board[i, j] == Player.BLACK.value:
                    row += f'{bold_start}B{bold_end} | '
                else:
                    row += '  | '
            print(row + str(9 - i))
            print("  +---+---+---+---+---+---+---+---+---+")
        print("    A   B   C   D   E   F   G   H   I")