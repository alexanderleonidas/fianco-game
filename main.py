import pygame
import sys
from const import *
from game import Game

class Main:
    def __init__(self):
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Fianco')
        self.game = Game()

    def main_loop(self):

        screen = self.screen
        game = self.game
        board = self.game.board
        mover = self.game.mover
        # Game loop
        while True:
            game.show_game(screen)
            for event in pygame.event.get():
                # Click Event
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mover.update_mouse(event.pos)
                    clicked_row = mover.mouse_y // SQUARE_SIZE
                    clicked_col = mover.mouse_x // SQUARE_SIZE
                    clicked_square = board.state[clicked_row][clicked_col]

                    # pvp Mode: Both BLACK and WHITE are players
                    # pvc Mode: WHITE is player, BLACK is computer
                    if game.game_mode == 'pvp' or (game.game_mode == 'pvc' and game.player == WHITE):
                        if clicked_square.has_piece():
                            clicked_square.piece.clear_moves()
                            game.select_piece(clicked_square.piece, clicked_row, clicked_col)
                        if mover.selected and clicked_square != board.state[mover.initial_row][mover.initial_col] and clicked_square.is_empty():
                            game.move_piece(clicked_row, clicked_col)
                            game.show_game(screen)

                elif event.type == pygame.KEYDOWN and event.key == pygame.K_u:
                    game.unmove_piece()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    game.reset()
                    game = self.game
                    board = self.game.board
                    mover = self.game.mover
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if game.game_mode == 'pvc' and game.player == BLACK and game.running == True:
                pygame.display.update()

                game.make_ai_move()
                game.show_game(screen)
            
            pygame.display.update()

main = Main()
main.main_loop()