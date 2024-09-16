import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QLabel, QMessageBox, QPushButton
from PyQt5.QtCore import QTimer, Qt, QRect
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen

from fianco_game import FiancoGame
from fianco_ai import get_best_move

class FiancoGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.game = FiancoGame()
        self.selected_piece = None
        self.valid_moves = []
        self.player_times = [600, 600]  # 10 minutes for each player
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Fianco')
        self.setGeometry(100, 100, 600, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QGridLayout()
        central_widget.setLayout(layout)

        self.board_widget = BoardWidget(self.game, self)
        layout.addWidget(self.board_widget, 0, 0, 9, 9)

        self.timer_label = QLabel('Player 1: 10:00 | Player 2: 10:00')
        layout.addWidget(self.timer_label, 9, 0, 1, 8)

        self.undo_button = QPushButton('Undo')
        self.undo_button.clicked.connect(self.undo_move)
        layout.addWidget(self.undo_button, 9, 8, 1, 1)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Update every second

    def update_time(self):
        current_player = self.game.current_player - 1
        self.player_times[current_player] -= 1
        if self.player_times[current_player] <= 0:
            self.game_over(3 - self.game.current_player)
        minutes1, seconds1 = divmod(self.player_times[0], 60)
        minutes2, seconds2 = divmod(self.player_times[1], 60)
        self.timer_label.setText(f'Player 1: {minutes1:02d}:{seconds1:02d} | Player 2: {minutes2:02d}:{seconds2:02d}')

    def game_over(self, winner):
        self.timer.stop()
        self.board_widget.setEnabled(False)
        self.undo_button.setEnabled(False)
        QMessageBox.information(self, 'Game Over', f'Player {winner} wins!')

    def undo_move(self):
        if self.game.undo_move():
            # Undo the player's move
            self.board_widget.update()
            # Undo the AI's move if it's the AI's turn
            if self.game.current_player == 2:
                self.game.undo_move()
                self.board_widget.update()
            self.selected_piece = None
            self.valid_moves = []

class BoardWidget(QWidget):
    def __init__(self, game, parent):
        super().__init__(parent)
        self.game = game
        self.parent = parent
        self.setFixedSize(540, 540)

    def paintEvent(self, event):
        painter = QPainter(self)
        cell_size = self.width() // 9

        # Draw the grid
        painter.setPen(QPen(Qt.black, 1, Qt.SolidLine))
        for i in range(10):
            painter.drawLine(i * cell_size, 0, i * cell_size, self.height())
            painter.drawLine(0, i * cell_size, self.width(), i * cell_size)

        # Draw the pieces
        for y in range(9):
            for x in range(9):
                if self.game.board[y, x] == 1:
                    painter.setBrush(QBrush(QColor(255, 0, 0)))  # Red for player 1
                    painter.drawEllipse(x * cell_size + 5, y * cell_size + 5, cell_size - 10, cell_size - 10)
                elif self.game.board[y, x] == 2:
                    painter.setBrush(QBrush(QColor(0, 0, 255)))  # Blue for player 2
                    painter.drawEllipse(x * cell_size + 5, y * cell_size + 5, cell_size - 10, cell_size - 10)

        # Highlight selected piece
        if self.parent.selected_piece:
            y, x = self.parent.selected_piece
            painter.setBrush(QBrush(QColor(255, 255, 0, 100)))
            painter.drawRect(x * cell_size, y * cell_size, cell_size, cell_size)

        # Highlight valid moves
        painter.setBrush(QBrush(QColor(0, 255, 0, 100)))
        for move in self.parent.valid_moves:
            _, (y, x) = move
            painter.drawRect(x * cell_size, y * cell_size, cell_size, cell_size)

    def mousePressEvent(self, event):
        cell_size = self.width() // 9
        x = event.x() // cell_size
        y = event.y() // cell_size

        if self.parent.selected_piece is None:
            if self.game.board[y, x] == self.game.current_player:
                self.parent.selected_piece = (y, x)
                self.parent.valid_moves = [move for move in self.game.get_valid_moves() if move[0] == (y, x)]
        else:
            start = self.parent.selected_piece
            end = (y, x)
            if (start, end) in self.parent.valid_moves:
                self.game.make_move(start, end)
                self.parent.selected_piece = None
                self.parent.valid_moves = []
                self.update()
                
                if self.game.is_game_over():
                    winner = self.game.get_winner()
                    self.parent.game_over(winner)
                else:
                    # AI move
                    ai_move = get_best_move(self.game, depth=3)
                    if ai_move:
                        self.game.make_move(*ai_move)
                    self.update()
                    if self.game.is_game_over():
                        winner = self.game.get_winner()
                        self.parent.game_over(winner)
            else:
                self.parent.selected_piece = None
                self.parent.valid_moves = []
        
        self.update()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FiancoGUI()
    ex.show()
    sys.exit(app.exec_())