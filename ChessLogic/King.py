from ChessLogic.Piece import Piece
from ChessLogic.Bishop import Bishop
from ChessLogic.Rook import Rook


def _king_move_gen(king):
    for r in range(king.rank - 1, king.rank + 2):
        for f in range(king.file - 1, king.file + 2):
            if (r != king.rank or f != king.file) and (0 <= r <= 7 and 0 <= f <= 7):
                yield r, f


class King(Piece):
    id = "king"

    def __init__(self, board, rank, file, color=True):
        Piece.__init__(self, board, rank, file, color)
        self.king_castle_crd = (not color) * 7, 6
        self.queen_castle_crd = (not color) * 7, 2

    @property
    def in_check(self):
        return not all(
            p.color == self.color for
            p in self.b[self.coordinate].under_attack_by
        )

    def populate_movable(self):
        if not self.has_moved:
            can_kingside_castle, can_queenside_castle = self.b.can_castle(self.color)
            if can_kingside_castle:
                self.movable_spaces.add((self.rank, 6))
            if can_queenside_castle:
                self.movable_spaces.add((self.rank, 2))

        for crd in _king_move_gen(self):
            cur_space = self.b[crd]
            not_make_check = all(
                p.color == self.color
                for p in cur_space.under_attack_by
            )
            try:
                if cur_space.piece.color != self.color and not_make_check:
                    self.movable_spaces.add(crd)
            except AttributeError:
                if not_make_check:
                    self.movable_spaces.add(crd)

    def attack_spaces(self):
        for crd in _king_move_gen(self):
            self.attacking_spaces.add(crd)
        self.b.attack_spaces(self)

    def move(self, rank, file):
        Piece.move(self, rank, file)
        if not self.has_moved:
            if (rank, file) == self.king_castle_crd:
                self.b.complete_castle(self.color, 'k', (self.rank, 7))
            if (rank, file) == self.queen_castle_crd:
                self.b.complete_castle(self.color, 'q', (self.rank, 0))

    def restrict_check(self, restrict_piece):
        if not restrict_piece:
            return

        def axis_mod(axis, own_axis):
            return -1 if axis > own_axis else 1
        rank_mod = axis_mod(restrict_piece.rank, self.rank)
        file_mod = axis_mod(restrict_piece.file, self.file)
        restrict_crd = None

        if isinstance(restrict_piece, Bishop):
            # need this so queen doesn't restrict weird moves
            if restrict_piece.rank != self.rank and restrict_piece.file != self.file:
                restrict_rank = self.rank + rank_mod
                restrict_file = self.file + file_mod
                restrict_crd = (restrict_rank, restrict_file)
        if isinstance(restrict_piece, Rook):
            if restrict_piece.rank == self.rank:
                restrict_crd = (
                    self.rank,
                    self.file + file_mod,
                )
            elif restrict_piece.file == self.file:
                restrict_crd = (
                    self.rank + rank_mod,
                    self.file,
                )

        if restrict_crd in self.movable_spaces:
            self.movable_spaces.remove(restrict_crd)

    def __repr__(self): return "K" if self.color else "k"
