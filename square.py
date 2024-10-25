class Square:

    ALPHACOLS = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h', 8: 'i'}

    def __init__(self, row, col, piece=None):
        self.row = row
        self.col = col
        self.piece = piece
        self.alphacol = self.ALPHACOLS[col]
    
    def __eq__(self, other):
        return self.row == other.row and self.col == other.col
    
    def has_piece(self):
        return self.piece != None
    
    def is_empty(self):
        return not self.has_piece()

    def has_opponent(self, color):
        # The color must be different to the current players
        return self.has_piece() and self.piece.color != color
    
    def has_team_mate(self, color):
        return self.has_piece() and self.piece.color == color

    def empty_or_opponent(self, color):
        return self.is_empty() or self.has_opponent(color)
    
    @staticmethod
    def in_range(*args):
        # Make sure possible move coordinates are within the board size
        for arg in args:
            if arg < 0 or arg >= 9:
                return False
        return True
    
    @staticmethod
    def get_alphacol(col):
        ALPHACOLS = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h', 8: 'i'}
        return ALPHACOLS[col]
    