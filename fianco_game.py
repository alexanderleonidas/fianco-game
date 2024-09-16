import numpy as np

class FiancoGame:
    def __init__(self):
        self.board = np.zeros((9, 9), dtype=int)
        # Initialize player 1 (top)
        self.board[0, :] = 1
        self.board[1, [1, 7]] = 1
        self.board[2, [2, 6]] = 1
        self.board[3, [3, 5]] = 1
        # Initialize player 2 (bottom)
        self.board[8, :] = 2
        self.board[7, [1, 7]] = 2
        self.board[6, [2, 6]] = 2
        self.board[5, [3, 5]] = 2
        self.current_player = 1
        self.move_history = []

    def is_valid_move(self, start, end):
        sx, sy = start
        ex, ey = end

        # Check if the move is within the board
        if not (0 <= ex < 9 and 0 <= ey < 9):
            return False

        # Check if the start position contains the current player's stone
        if self.board[sx, sy] != self.current_player:
            return False

        # Check if the end position is empty
        if self.board[ex, ey] != 0:
            return False

        # Check if it's a valid move or capture
        dx, dy = ex - sx, ey - sy
        if dx == 0 and abs(dy) == 1:  # Sideways move
            return True
        elif self.current_player == 1 and dx == 1 and abs(dy) <= 1:  # Forward move for player 1
            return True
        elif self.current_player == 2 and dx == -1 and abs(dy) <= 1:  # Forward move for player 2
            return True
        elif abs(dx) == 2 and abs(dy) == 2:  # Potential capture
            mx, my = sx + dx//2, sy + dy//2
            return self.board[mx, my] == 3 - self.current_player  # Check if middle piece is opponent's

        return False

    def get_valid_moves(self):
        valid_moves = []
        for x in range(9):
            for y in range(9):
                if self.board[x, y] == self.current_player:
                    for dx in [-2, -1, 0, 1, 2]:
                        for dy in [-2, -1, 0, 1, 2]:
                            end = (x + dx, y + dy)
                            if self.is_valid_move((x, y), end):
                                valid_moves.append(((x, y), end))
        return valid_moves

    def make_move(self, start, end):
        if not self.is_valid_move(start, end):
            return False

        sx, sy = start
        ex, ey = end
        captured_piece = None

        # Handle capture
        if abs(ex - sx) == 2 and abs(ey - sy) == 2:
            mx, my = (sx + ex) // 2, (sy + ey) // 2
            captured_piece = (mx, my, self.board[mx, my])
            self.board[mx, my] = 0

        # Move the piece
        self.board[ex, ey] = self.board[sx, sy]
        self.board[sx, sy] = 0

        # Record the move
        self.move_history.append((start, end, captured_piece))

        self.current_player = 3 - self.current_player
        return True

    def undo_move(self):
        if not self.move_history:
            return False

        start, end, captured_piece = self.move_history.pop()
        sx, sy = start
        ex, ey = end

        # Move the piece back
        self.board[sx, sy] = self.board[ex, ey]
        self.board[ex, ey] = 0

        # Restore captured piece if any
        if captured_piece:
            mx, my, piece_value = captured_piece
            self.board[mx, my] = piece_value

        # Switch back to the previous player
        self.current_player = 3 - self.current_player
        return True

    def is_game_over(self):
        # Check if any player has reached the opposite side
        if 1 in self.board[8, :] or 2 in self.board[0, :]:
            return True

        # Check if current player has no valid moves
        return len(self.get_valid_moves()) == 0

    def get_winner(self):
        if 1 in self.board[8, :]:
            return 1
        elif 2 in self.board[0, :]:
            return 2
        return None