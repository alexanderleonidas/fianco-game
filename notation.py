from typing import Tuple

def convert_notation_to_move(notation: str) -> Tuple[int, int, int, int]:
    # Convert algebraic notation to board coordinates
    start, end = notation.split()
    start_col, start_row = ord(start[0]) - ord('A'), int(start[1]) - 1
    end_col, end_row = ord(end[0]) - ord('A'), int(end[1]) - 1
    return (8 - start_row, start_col, 8 - end_row, end_col)

def convert_move_to_notation(move: Tuple[int, int, int, int]) -> str:
    # Convert board coordinates to algebraic notation
    start_i, start_j, end_i, end_j = move
    start = chr(start_j + ord('A')) + str(9 - start_i)
    end = chr(end_j + ord('A')) + str(9 - end_i)
    return f"{start} {end}"