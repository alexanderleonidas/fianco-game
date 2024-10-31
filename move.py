from const import *
from square import Square

class Move:
    def __init__(self, initial: Square, final: Square):
        # Initial and final squares
        self.initial = initial
        self.final = final
    
    def __str__(self):
        return self.convert_to_notation()

    def __eq__(self, other):
        return self.initial == other.initial and self.final == other.final

    def convert_to_notation(self, capture=False):
         # Convert square coordinates to chess board coordinate notation
        from_square = f"{Square.ALPHACOLS[self.initial.col]}{ROWS - self.initial.row}"
        to_square = f"{Square.ALPHACOLS[self.final.col]}{ROWS - self.final.row}"
        
        if capture:
            self.capture = capture
            return f"{from_square}x{to_square}"
        else:
            return f"{from_square}-{to_square}"
    
    @staticmethod
    def convert_to_move(notation):
        # Check if it's a capture move
        if 'x' in notation:
            from_square, to_square = notation.split('x')
        else:
            from_square, to_square = notation.split('-')
        
        # Create reverse mapping of ALPHACOLS for easy lookup
        COL_NUMS = {v: k for k, v in Square.ALPHACOLS.items()}
        
        # Convert from_square
        initial_col = COL_NUMS[from_square[0]]  # Use mapping to get column number
        initial_row = ROWS - int(from_square[1])   # Convert '1'-'9' to 8-0
        
        # Convert to_square
        final_col = COL_NUMS[to_square[0]]
        final_row = ROWS - int(to_square[1])

        
        return Move(Square(initial_row, initial_col), Square(final_row, final_col))