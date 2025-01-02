class Mover:
    def __init__(self):
        self.mouse_x = 0
        self.mouse_y = 0
        self.initial_row = 0
        self.initial_col = 0
        self.piece = None
        self.selected = False
    
    def update_mouse(self, pos):
        # Coordinates of mouse on the surface
        self.mouse_x, self.mouse_y = pos

    def save_initial(self, row, col):
        self.initial_col = col
        self.initial_row = row

    def pick_piece(self, piece):
        self.piece = piece
        self.selected = True
    
    def unpick_piece(self):
        self.piece = None
        self.selected = False