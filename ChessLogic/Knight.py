from ChessLogic.Bishop import Bishop
from ChessLogic.Piece import Piece

from ChessLogic.Rook import Rook


def _knight_move_gen(knight):
    #   0   1
    #  0     1
    #     N
    #  3     2
    #   3   2
    # Make sense? Good.
    move_offsets = (
        (2, -1), (1, -2),
        (2, 1), (1, 2),
        (-2, 1), (-1, 2),
        (-2, -1), (-1, -2)
    )
    for r, f in move_offsets:
        crd = knight.rank + r, knight.file + f
        if all(0 <= c <= 7 for c in crd):
            yield crd


class Knight(Piece):
    id = "knights"

    def populate_movable(self):
        self.safe_moves()
        if self.pinned:
            return

        for crd in _knight_move_gen(self):
            potential_piece = self.b[crd].piece
            if potential_piece is None or potential_piece.color != self.color:
                self.movable_spaces.add(crd)

    def attack_spaces(self):
        for crd in _knight_move_gen(self):
            self.attacking_spaces.add(crd)
        self.b.attack_spaces(self)

    def safe_moves(self):
        self.safe_on_axes(self.diagonal_from, Bishop, True, None)
        if self.pinned:
            return
        self.safe_on_axes(self.horizvert_from, Rook, True, None)

    def __repr__(self): return "N" if self.color else "n"
