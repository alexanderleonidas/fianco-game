import pygame
import sys
from const import *
from game import Game
from gui import GUI

class Main:
    def __init__(self):
        self.game = Game()
        self.gui = GUI(self.game)
        self.game.start_ai()

    def main_loop(self):
        clock = pygame.time.Clock()
        gui = self.gui
        game = self.game
        board = self.game.board
        mover = self.game.mover
        ai_move_done = False  # Flag to track AI move status

        # Game loop
        while True:
            gui.show_game()
            for event in pygame.event.get():
                # Click Event
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mover.update_mouse(event.pos)
                    clicked_row = mover.mouse_y // SQUARE_SIZE
                    clicked_col = mover.mouse_x // SQUARE_SIZE
                    clicked_square = board.state[clicked_row][clicked_col]

                    if game.game_mode == 'pvp' or (game.game_mode == 'pvc' and game.player == game.user_player):
                        if clicked_square.has_piece():
                            clicked_square.piece.clear_moves()
                            game.select_piece(clicked_square.piece, clicked_row, clicked_col)
                        if mover.selected and clicked_square != board.state[mover.initial_row][mover.initial_col] and clicked_square.is_empty():
                            game.move_piece(clicked_row, clicked_col)
                            gui.show_game()
                            print(self.game.user_player, board.last_move)
                            ai_move_done = False

                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    game.reset()
                    game = self.game
                    board = self.game.board
                    mover = self.game.mover
                    ai_move_done = False  # Reset AI move flag

                elif game.game_mode == 'pvc' and game.player == game.ai_player and game.running == True:
                    if not ai_move_done:
                        pygame.display.update()
                        gui.handle_ai_move()
                        gui.show_game()
                        ai_move_done = True  # Mark AI move as done
                        print(self.game.ai_player, board.last_move)

                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.update()
            clock.tick(FPS)

main = Main()
main.main_loop()