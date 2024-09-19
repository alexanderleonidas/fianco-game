from board import Board
from piece import Piece
from constants import *
import pygame
import time
import random

class Game():
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("FIANCO")
        self.board = Board(BOARD_WIDTH, BOARD_HEIGHT)
        self.running = True
        self.selected_piece = None
        self.current_player = WHITE
        self.game_over = False
        self.white_time = 600  # 10 minutes in seconds
        self.black_time = 600
        self.start_time = time.time()
        self.title_font = pygame.font.Font(None, 36)
        self.info_font = pygame.font.Font(None, 24)
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                self.handle_mouse_click(event.pos)

    def handle_mouse_click(self, pos):
        col, row = self.get_square_clicked(pos[0], pos[1])
        if (row, col) != (None, None):
            if self.selected_piece is None:
                if self.board.state[row][col] != EMPTY_SPACE and self.board.state[row][col].color == self.current_player:
                    self.selected_piece = self.board.state[row][col]
                    self.selected_piece.select(True)
                    self.board.highlight_squares = self.board.get_valid_moves(self.selected_piece)
            else:
                valid_moves = self.board.get_valid_moves(self.selected_piece)
                if (row, col) in valid_moves:
                    self.board.move_piece(self.selected_piece, row, col)
                    self.selected_piece.select(False)
                    self.selected_piece = None
                    self.board.highlight_squares = []
                    self.switch_player()
                else:
                    self.selected_piece.select(False)
                    self.selected_piece = None
                    self.board.highlight_squares = []

    def switch_player(self):
        self.current_player = BLACK if self.current_player == WHITE else WHITE
        if self.current_player == BLACK:
            self.computer_move()

    def computer_move(self):
        # Simple AI: randomly choose a valid move
        pieces = [piece for row in self.board.state for piece in row if isinstance(piece, Piece) and piece.color == BLACK]
        random.shuffle(pieces)
        for piece in pieces:
            moves = self.board.get_valid_moves(piece)
            if moves:
                move = random.choice(moves)
                self.board.move_piece(piece, move[0], move[1])
                self.switch_player()
                break

    def update(self):
        if not self.game_over:
            if self.current_player == WHITE:
                self.white_time -= time.time() - self.start_time
            else:
                self.black_time -= time.time() - self.start_time
            self.start_time = time.time()

            if self.white_time <= 0 or self.black_time <= 0:
                self.game_over = True
                return

            if self.board.check_win_condition(WHITE):
                self.game_over = True
                print("White wins!")
            elif self.board.check_win_condition(BLACK):
                self.game_over = True
                print("Black wins!")
            elif self.board.check_threefold_repetition():
                self.game_over = True
                print("Draw by threefold repetition!")
            elif self.board.check_no_moves(self.current_player) or self.board.check_no_pieces(self.current_player):
                self.game_over = True
                print(f"{'Black' if self.current_player == WHITE else 'White'} wins!")

    def draw(self):
        self.screen.fill(WHITE)
        self.board.draw(self.screen)
        self.draw_info_panel()
        pygame.display.flip()

    def draw_info_panel(self):
        info_surface = pygame.Surface((INFO_PANEL_WIDTH, HEIGHT))
        info_surface.fill(LIGHT_BROWN)

        # Draw title
        title = self.title_font.render("FIANCO", True, BLACK)
        info_surface.blit(title, (INFO_PANEL_WIDTH // 2 - title.get_width() // 2, 10))

        # Draw timers
        white_timer = self.info_font.render(f"White: {self.format_time(self.white_time)}", True, BLACK)
        black_timer = self.info_font.render(f"Black: {self.format_time(self.black_time)}", True, BLACK)
        info_surface.blit(white_timer, (10, 60))
        info_surface.blit(black_timer, (10, 90))

        # Draw current player
        current_player = self.info_font.render(f"Current Player: {'White' if self.current_player == WHITE else 'Black'}", True, BLACK)
        info_surface.blit(current_player, (10, 120))

        # Draw move history
        history_title = self.info_font.render("Move History", True, BLACK)
        info_surface.blit(history_title, (10, 160))

        y_offset = 190
        for i, move in enumerate(self.board.move_history[-15:]):  # Show last 15 moves
            color = BLACK if i % 2 == 0 else GRAY
            move_number = len(self.board.move_history) - len(self.board.move_history[-15:]) + i + 1
            if i % 2 == 0:
                text = self.info_font.render(f"{move_number}. {move}", True, color)
            else:
                text = self.info_font.render(f"    {move}", True, color)
            info_surface.blit(text, (10, y_offset))
            y_offset += 25

        self.screen.blit(info_surface, (BOARD_WIDTH, 0))

    def format_time(self, seconds):
        minutes, secs = divmod(int(seconds), 60)
        return f"{minutes:02d}:{secs:02d}"

    def get_square_clicked(self, mousex, mousey):
        if mousex < BOARD_WIDTH:
            col = mousex // SQUARE_SIZE
            row = mousey // SQUARE_SIZE
            if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
                return col, row
        return None, None
    

if __name__ == "__main__":
    game = Game()
    game.run()