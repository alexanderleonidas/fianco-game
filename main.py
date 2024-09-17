from fianco_game import FiancoGame
from fianco_ai import FiancoAI
from player import Player
from notation import convert_move_to_notation, convert_notation_to_move
import time

def main():
    # Main game loop
    game = FiancoGame()
    ai = FiancoAI()
    print("Welcome to Fianco!")
    ai_color = Player.WHITE if input("Choose AI color (W/B): ").upper() == 'W' else Player.BLACK
    human_player = Player.BLACK if ai_color == Player.WHITE else Player.WHITE

    print("Initial board state:")
    game.print_board()

    game_start_time = time.time()

    while not game.is_terminal():
        if game.current_player == human_player:
            # Human player's turn
            while True:
                move_notation = input("Enter your move (e.g., A1 A2): ").upper()
                move = convert_notation_to_move(move_notation)
                if game.validate_move(move):
                    game.make_move(move)
                    break
                else:
                    print("Invalid move. Try again.")
        else:
            # AI player's turn
            print("AI is thinking...")
            ai_move_start_time = time.time()
            best_move = ai.get_ai_move(game, depth=3)
            ai_move_end_time = time.time()
            ai_move_duration = ai_move_end_time - ai_move_start_time
            game.ai_time += ai_move_duration

            ai_move_notation = convert_move_to_notation(best_move)
            print(f"AI played: {ai_move_notation}")
            print(f"Time for this move: {ai_move_duration:.2f} seconds")
            game.make_move(best_move)

        # Print game state after each move
        print("\nBoard state after move:")
        game.print_board()
        print(f"Move count: {game.move_count}")
        print(f"Total AI thinking time: {game.ai_time:.2f} seconds")

        current_game_duration = time.time() - game_start_time
        print(f"Total game duration: {current_game_duration:.2f} seconds")

    # Game over
    print("Game over!")
    winner = game.get_winner()
    if winner:
        print(f"{'White' if winner == Player.WHITE else 'Black'} wins!")
    else:
        print("It's a draw due to threefold repetition!")

    final_game_duration = time.time() - game_start_time
    print(f"Final game duration: {final_game_duration:.2f} seconds")
    print(f"Final AI total thinking time: {game.ai_time:.2f} seconds")

if __name__ == "__main__":
    main()