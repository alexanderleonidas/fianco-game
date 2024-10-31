import pygame
import sys
from copy import deepcopy
import time
from const import *
from game import Game
from gui import GUI

class Main:
    def __init__(self):
        self.game = Game()
        self.gui = GUI(self.game)

    def main_loop(self):

        clock = pygame.time.Clock()
        gui = self.gui
        game = self.game
        board = self.game.board
        mover = self.game.mover
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

                    # pvp Mode: Both BLACK and WHITE are players
                    # pvc Mode: WHITE is player, BLACK is computer
                    if game.game_mode == 'pvp' or (game.game_mode == 'pvc' and game.player == WHITE):
                        if clicked_square.has_piece():
                            clicked_square.piece.clear_moves()
                            game.select_piece(clicked_square.piece, clicked_row, clicked_col)
                        if mover.selected and clicked_square != board.state[mover.initial_row][mover.initial_col] and clicked_square.is_empty():
                            game.move_piece(clicked_row, clicked_col)
                            gui.show_game()
                            print(board.last_move)

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
                gui.show_game()
                print(board.last_move)
            
            pygame.display.update()
            clock.tick(FPS)

main = Main()
main.main_loop()