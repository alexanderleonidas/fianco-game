from const import *
from game import Game
from square import Square
import pygame
import threading

class GUI:
    def __init__(self, game: Game):
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((NEW_WIDTH, HEIGHT))
        self.background_surface = pygame.Surface(self.screen.get_size())
        self._cached_history_surface = None
        pygame.display.set_caption('Fianco')
        self._show_background(self.background_surface)
        self.game = game
        self.board = game.board
        self.mover = game.mover
        self._cached_history = []
        self.ai_thread = None
        self.ai_running = False

        self.font_small = pygame.font.SysFont('monospace', 18, bold=True)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_large = pygame.font.Font(None, 28)
        self.font_extra_large = pygame.font.Font(None, 36)

        selected_player, selected_difficulty = self._show_player_selection_popup(self.screen)
        game.user_player = selected_player
        game.difficulty = selected_difficulty

        # Start the game after player selection
        self.game.start_game()

    def reset(self):
        self.game.reset()
        self.__init__(self.game)

    def _ai_compute_best_move(self):
        """Runs the AI computation."""
        self.ai_running = True
        piece, move = None, None
        try:
            piece, move = self.game.get_ai_move()
        finally:
            self.game.select_piece(piece, move.initial.row, move.initial.col)
            self.game.move_piece(move.final.row, move.final.col)
            self.ai_running = False

    def handle_ai_move(self):
        """Handles the AI's move in a separate thread."""
        if self.ai_thread is None or not self.ai_thread.is_alive():
            self.ai_thread = threading.Thread(target=self._ai_compute_best_move)
            self.ai_thread.start()
        
    def show_game(self):
        self.screen.blit(self.background_surface, (0, 0))
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
            initial_rect = pygame.Rect(
                self.board.last_move.initial.col * SQUARE_SIZE,
                self.board.last_move.initial.row * SQUARE_SIZE,
                SQUARE_SIZE,
                SQUARE_SIZE
            )
            final_rect = pygame.Rect(
                self.board.last_move.final.col * SQUARE_SIZE,
                self.board.last_move.final.row * SQUARE_SIZE,
                SQUARE_SIZE,
                SQUARE_SIZE
            )
            for rect in [initial_rect, final_rect]:
                color = NEON_GREEN if (rect.y // SQUARE_SIZE + rect.x // SQUARE_SIZE) % 2 == 0 else DARK_NEON_GREEN
                pygame.draw.rect(surface, color, rect)

    @staticmethod
    def _show_background(surface):
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

    @staticmethod
    def _draw_piece(surface, color, center, selected):
        if selected:
            pygame.draw.circle(surface, RED, center, SQUARE_SIZE//2-12)
        elif color == BLACK:
            pygame.draw.circle(surface, GRAY, center, SQUARE_SIZE//2-12)
        elif color == WHITE:
            pygame.draw.circle(surface, BLACK, center, SQUARE_SIZE//2-12)
        pygame.draw.circle(surface, color, center, SQUARE_SIZE//2-15)

    @staticmethod
    def _show_player_selection_popup(surface):
        # Draw popup background
        popup_rect = pygame.Rect((WIDTH - POPUP_WIDTH) // 2, (HEIGHT - POPUP_HEIGHT) // 2, POPUP_WIDTH, POPUP_HEIGHT)
        pygame.draw.rect(surface, WHITE, popup_rect)
        pygame.draw.rect(surface, BLACK, popup_rect, 2)

        # Display instructions
        instruction_font = pygame.font.Font(None, 28)
        button_font = pygame.font.Font(None, 24)

        def draw_popup():
            """Redraws the popup and buttons."""
            surface.fill(WHITE)  # Clear the screen
            pygame.draw.rect(surface, WHITE, popup_rect)
            pygame.draw.rect(surface, BLACK, popup_rect, 2)

            # Instruction text
            instruction_text = instruction_font.render("Choose Your Player:", True, BLACK)
            instruction_rect = instruction_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
            surface.blit(instruction_text, instruction_rect)

            # Player buttons
            pygame.draw.rect(surface, LIGHT_GREEN, white_button_rect)
            pygame.draw.rect(surface, DARK_GREEN, black_button_rect)
            white_text = button_font.render("White", True, BLACK)
            black_text = button_font.render("Black", True, WHITE)
            surface.blit(white_text, white_button_rect.move(10, 5))
            surface.blit(black_text, black_button_rect.move(10, 5))

            # Difficulty text
            difficulty_text = instruction_font.render("Choose Difficulty (0-5):", True, BLACK)
            difficulty_rect = difficulty_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
            surface.blit(difficulty_text, difficulty_rect)

            # Difficulty buttons
            for btn_rect, diff in difficulty_buttons:
                color = LIGHT_BLUE if diff % 2 == 0 else DARK_BLUE
                pygame.draw.rect(surface, color, btn_rect)
                button_text = button_font.render(str(diff), True, WHITE)
                surface.blit(button_text, btn_rect.move(10, 5))

            # Highlight selections
            if selected_player == WHITE:
                pygame.draw.rect(surface, RED, white_button_rect, 3)
            elif selected_player == BLACK:
                pygame.draw.rect(surface, RED, black_button_rect, 3)

            if selected_difficulty is not None:
                for btn_rect, diff in difficulty_buttons:
                    if diff == selected_difficulty:
                        pygame.draw.rect(surface, RED, btn_rect, 3)

            pygame.display.flip()

        # Button positions
        white_button_rect = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 - 40, 60, 40)
        black_button_rect = pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2 - 40, 60, 40)
        difficulty_buttons = []
        button_width = 40
        button_spacing = 10
        start_x = (WIDTH - (6 * button_width + 5 * button_spacing)) // 2
        for i in range(6):
            button_rect = pygame.Rect(start_x + i * (button_width + button_spacing), HEIGHT // 2 + 50, button_width, 40)
            difficulty_buttons.append((button_rect, i))

        # Selection variables
        selected_player = None
        selected_difficulty = None

        # Initial drawing
        draw_popup()

        # Wait for user input
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Check for player selection
                    if white_button_rect.collidepoint(event.pos):
                        selected_player = WHITE
                    elif black_button_rect.collidepoint(event.pos):
                        selected_player = BLACK

                    # Check for difficulty selection
                    for button_rect, difficulty in difficulty_buttons:
                        if button_rect.collidepoint(event.pos):
                            selected_difficulty = difficulty

                    # Redraw popup with updated selections
                    draw_popup()

            # Return selections if both are made
            if selected_player is not None and selected_difficulty is not None:
                return selected_player, selected_difficulty

    def _show_info_panel(self, surface):
        # Create a rectangle for the player display
        player_rect = pygame.Rect(WIDTH, 0, EXTRA_WIDTH, HEIGHT)
        pygame.draw.rect(surface, WHITE, player_rect)
        pygame.draw.rect(surface, BLACK, player_rect, 2)

        # Display the current player
        player_text = f"Player to move: {'White' if self.game.player == WHITE else 'Black'}"
        player_display = self.font_large.render(player_text, True, BLACK)
        text_rect = player_display.get_rect(center=(WIDTH + EXTRA_WIDTH // 2, 50))
        surface.blit(player_display, text_rect)

        # Display move history
        # Initialize a cached surface if it doesn't exist
        if self._cached_history_surface is None:
            self._cached_history_surface = pygame.Surface((EXTRA_WIDTH, HEIGHT - 230))

        # Check if the move history has changed
        if self.board.move_history != self._cached_history:
            self._cached_history_surface.fill(WHITE)  # Clear the cached surface
            start_y = 0
            line_spacing = 25
            max_visible_moves = (HEIGHT - 230) // line_spacing

            # Render only the last `max_visible_moves` moves
            visible_moves = self.board.move_history[-max_visible_moves:]
            total_moves = len(self.board.move_history)  # Total number of moves
            for i, move in enumerate(visible_moves):
                # Correctly calculate the absolute move number
                absolute_move_index = total_moves - len(visible_moves) + i + 1
                move_text = f"{absolute_move_index}. {move}"
                move_display = pygame.font.Font(None, 20).render(move_text, True, BLACK)
                self._cached_history_surface.blit(move_display, (10, start_y + i * line_spacing))

            self._cached_history = list(self.board.move_history)  # Update the cached history

        # Blit the cached surface onto the main surface
        surface.blit(self._cached_history_surface, (WIDTH, 230))

        # Display timers for both players
        white_timer_text = f"White Time: {self._format_time(self.game.white_time)}"
        black_timer_text = f"Black Time: {self._format_time(self.game.black_time)}"

        white_timer_display = self.font_large.render(white_timer_text, True, BLACK)
        black_timer_display = self.font_large.render(black_timer_text, True, BLACK)

        white_timer_rect = white_timer_display.get_rect(center=(WIDTH + EXTRA_WIDTH // 2, 160))
        black_timer_rect = black_timer_display.get_rect(center=(WIDTH + EXTRA_WIDTH // 2, 120))

        self.screen.blit(white_timer_display, white_timer_rect)
        self.screen.blit(black_timer_display, black_timer_rect)

        # Update the current player's timer (not both)
        if self.game.game_started and self.game.running and not self.game.is_over():
            current_time = pygame.time.get_ticks()
            elapsed_time = (current_time - self.game.last_tick) / 1000
            if self.game.player == WHITE:
                self.game.white_time -= elapsed_time
            else:
                self.game.black_time -= elapsed_time
            self.game.last_tick = current_time

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