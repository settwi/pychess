from ChessLogic.Bishop import Bishop
from ChessLogic.Piece import Piece

from ChessLogic.Rook import Rook


class Queen(Bishop, Rook):
    id = "queens"

    def __init__(self, board, rank, file, color=True):
        Piece.__init__(self, board, rank, file, color)

    def populate_movable(self, _=True):
        self.safe_moves()
        Rook.populate_movable(self, True)
        Bishop.populate_movable(self, True)

    def safe_moves(self):
        Bishop.safe_moves(self)
        self.pinned = False
        Rook.safe_moves(self)

    def attack_spaces(self):
        Bishop.attack_spaces(self)
        Rook.attack_spaces(self)

    def __repr__(self):
        return "Q" if self.color else "q"
