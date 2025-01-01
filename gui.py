from const import *
import pygame
from game import Game
from square import Square

class GUI:
    def __init__(self, game: Game):
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((NEW_WIDTH, HEIGHT))
        pygame.display.set_caption('Fianco')
        self.game = game
        self.board = game.board
        self.mover = game.mover

        selected_player = self._show_player_selection_popup(self.screen)
        game.user_player = selected_player

        # Start the game after player selection
        self.game.start_game()
        
    def show_game(self):
        self._show_background(self.screen)
        self._show_last_move(self.screen)
        self._show_moves(self.screen)
        self._show_pieces(self.screen)
        self._show_info_panel(self.screen)
        if self.game.is_over():
            self._show_win_popup(self.screen, self.board.final_state(self.game.player))
    
    def _show_win_popup(self, surface, outcome):
        # Draw popup background
        popup_rect = pygame.Rect((WIDTH - POPUP_WIDTH) // 2, (HEIGHT - POPUP_HEIGHT) // 2, POPUP_WIDTH, POPUP_HEIGHT)
        pygame.draw.rect(surface, WHITE, popup_rect)
        pygame.draw.rect(surface, BLACK, popup_rect, 2)
        
        # Draw popup text
        winner = 'White' if self.game.player == WHITE else 'Black'
        outcome_str = f"{winner} wins!" if outcome == 1 or outcome == -1 else "The game is a draw"
        popup_text = pygame.font.Font(None, 36).render(outcome_str, 0, BLACK)
        text_rect = popup_text.get_rect(center=(WIDTH//2, HEIGHT//2))
        surface.blit(popup_text, text_rect)

    def _show_last_move(self, surface):
        if self.board.last_move:
            initial = self.board.last_move.initial
            final = self.board.last_move.final

            for pos in [initial, final]:
                color = NEON_GREEN if (pos.row + pos.col) % 2 == 0 else DARK_NEON_GREEN
                rect = (pos.col * SQUARE_SIZE, pos.row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                pygame.draw.rect(surface, color, rect)

    def _show_background(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                if (row + col) % 2 == 0:
                    color = LIGHT_GREEN
                else:
                    color = DARK_GREEN
                rect = (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                pygame.draw.rect(surface, color, rect)
        
                # row coordinates
                if col == 0:
                    color = BLACK if row % 2 == 0 else GRAY
                    lbl = pygame.font.SysFont('monospace', 18, bold=True).render(str(ROWS-row), 1, color)
                    lbl_pos = (5, 5 + row * SQUARE_SIZE)
                    surface.blit(lbl, lbl_pos)

                # col coordinates
                if row == 8:
                    # color
                    color = BLACK if (row + col) % 2 == 0 else GRAY
                    # label
                    lbl = pygame.font.SysFont('monospace', 18, bold=True).render(Square.get_alphacol(col), 1, color)
                    lbl_pos = (col * SQUARE_SIZE + SQUARE_SIZE - 20, HEIGHT - 20)
                    # blit
                    surface.blit(lbl, lbl_pos)
    
    def _show_moves(self, surface):
        if self.mover.selected:
            piece = self.mover.piece
            for move in piece.valid_moves:
                color = '#C86464' if (move.final.row + move.final.col) % 2 == 0 else '#C84646'
                rect = (move.final.col * SQUARE_SIZE, move.final.row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                pygame.draw.rect(surface, color, rect)

    def _show_pieces(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                if self.board.state[row][col].has_piece():
                    color = self.board.state[row][col].piece.color
                    center = col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2
                    self._draw_piece(surface, color, center, self.mover.piece == self.board.state[row][col].piece)
    
    def _draw_piece(self, surface, color, center, selected):
        if selected:
            pygame.draw.circle(surface, RED, center, SQUARE_SIZE//2-12)
        elif color == BLACK:
            pygame.draw.circle(surface, GRAY, center, SQUARE_SIZE//2-12)
        elif color == WHITE:
            pygame.draw.circle(surface, BLACK, center, SQUARE_SIZE//2-12)
        pygame.draw.circle(surface, color, center, SQUARE_SIZE//2-15)

    def _show_player_selection_popup(self, surface):
        # Draw popup background
        popup_rect = pygame.Rect((WIDTH - POPUP_WIDTH) // 2, (HEIGHT - POPUP_HEIGHT) // 2, POPUP_WIDTH, POPUP_HEIGHT)
        pygame.draw.rect(surface, WHITE, popup_rect)
        pygame.draw.rect(surface, BLACK, popup_rect, 2)

        # Display instructions
        instruction_text = pygame.font.Font(None, 28).render("Choose Your Player:", True, BLACK)
        instruction_rect = instruction_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
        surface.blit(instruction_text, instruction_rect)

        # Draw buttons
        white_button_rect = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2, 60, 40)
        black_button_rect = pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2, 60, 40)
        pygame.draw.rect(surface, LIGHT_GREEN, white_button_rect)
        pygame.draw.rect(surface, DARK_GREEN, black_button_rect)

        # Add text to buttons
        white_text = pygame.font.Font(None, 24).render("White", True, BLACK)
        black_text = pygame.font.Font(None, 24).render("Black", True, WHITE)
        surface.blit(white_text, white_button_rect.move(10, 5))
        surface.blit(black_text, black_button_rect.move(10, 5))

        pygame.display.flip()

        # Wait for user input
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if white_button_rect.collidepoint(event.pos):
                        return WHITE
                    elif black_button_rect.collidepoint(event.pos):
                        return BLACK

    def _show_info_panel(self, surface):
        # Create a rectangle for the player display
        player_rect = pygame.Rect(WIDTH, 0, EXTRA_WIDTH, HEIGHT)
        pygame.draw.rect(surface, WHITE, player_rect)
        pygame.draw.rect(surface, BLACK, player_rect, 2)

        # Display the current player
        player_text = f"Player to move: {'White' if self.game.player == WHITE else 'Black'}"
        player_display = pygame.font.Font(None, 28).render(player_text, True, BLACK)
        text_rect = player_display.get_rect(center=(WIDTH + EXTRA_WIDTH // 2, 50))
        surface.blit(player_display, text_rect)

        # Display move history
        move_history = self.board.move_history
        history_text = pygame.font.Font(None, 20)

        # Define move history display area
        start_y = 230  # Start below the player display text
        box_height = HEIGHT - start_y - 20  # Leave some padding at the bottom
        line_spacing = 25  # Adjust spacing between moves

        # Calculate the maximum number of moves that can fit in the box
        max_visible_moves = box_height // line_spacing

        # Display the last `max_visible_moves` moves, maintaining absolute move indices
        for i, move in enumerate(move_history[-max_visible_moves:],
                                 start=len(move_history) - len(move_history[-max_visible_moves:])):
            move_text = f"{i + 1}. {move}"  # Use the absolute move number
            move_display = history_text.render(move_text, True, BLACK)
            move_rect = move_display.get_rect(
                topleft=(WIDTH + 10, start_y + (i - (len(move_history) - max_visible_moves)) * line_spacing))
            surface.blit(move_display, move_rect)

        # Display timers for both players
        timer_font = pygame.font.Font(None, 28)
        white_timer_text = f"White Time: {self._format_time(self.game.white_time)}"
        black_timer_text = f"Black Time: {self._format_time(self.game.black_time)}"

        white_timer_display = timer_font.render(white_timer_text, True, BLACK)
        black_timer_display = timer_font.render(black_timer_text, True, BLACK)

        white_timer_rect = white_timer_display.get_rect(center=(WIDTH + EXTRA_WIDTH // 2, 160))
        black_timer_rect = black_timer_display.get_rect(center=(WIDTH + EXTRA_WIDTH // 2, 120))

        self.screen.blit(white_timer_display, white_timer_rect)
        self.screen.blit(black_timer_display, black_timer_rect)

        # Update the current player's timer (not both)
        if self.game.game_started and not self.game.is_over():
            current_time = pygame.time.get_ticks()
            elapsed_time = (current_time - self.game.last_tick) / 1000  # in seconds

            if self.game.player == WHITE and self.game.user_player == WHITE:
                self.game.white_time -= elapsed_time
            elif self.game.player == BLACK and self.game.user_player == BLACK:
                self.game.black_time -= elapsed_time

            self.game.last_tick = current_time  # Update the last tick to the current time

        # End the game if time runs out
        if self.game.white_time <= 0 or self.game.black_time <= 0:
            self.game.running = False
            self.game.winner = 'Black' if self.game.white_time <= 0 else 'White'

    @staticmethod
    def _format_time(seconds):
        """Formats time in seconds to a MM:SS string."""
        minutes = int(seconds) // 60
        seconds = int(seconds) % 60
        return f"{minutes:02}:{seconds:02}"