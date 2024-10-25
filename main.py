import pygame
import sys
from const import *
from game import Game
from move import Move
from square import Square

class Main:
    def __init__(self):
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Fianco')
        self.game = Game()
        self.game_over = False

    def main_loop(self):

        screen = self.screen
        game = self.game
        board = self.game.board
        mover = self.game.mover
        # Game loop
        while True:
            game.show_background(screen)
            game.show_last_move(screen)
            game.show_moves(screen)
            game.show_pieces(screen)
            for event in pygame.event.get():
                # Click Event
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mover.update_mouse(event.pos)
                    clicked_row = mover.mouse_y // SQUARE_SIZE
                    clicked_col = mover.mouse_x // SQUARE_SIZE
                    clicked_square = board.state[clicked_row][clicked_col]

                    if clicked_square.has_piece():
                        game.select_piece(clicked_square.piece, event.pos, clicked_row, clicked_col)
                    if mover.selected:
                        game.move_piece(clicked_row, clicked_col)
                    
                if event.type == pygame.KEYDOWN and event.key == pygame.K_u:
                    print(game.board.last_move)
                    game.unmove_piece()
                    print(game.board.last_move)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                        game.reset()
                        game = self.game
                        board = self.game.board
                        mover = self.game.mover

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            pygame.display.update()

main = Main()
main.main_loop()