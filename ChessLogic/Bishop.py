from ChessLogic.Piece import Piece
from ChessLogic.Rook import Rook


class Bishop(Piece):
    id = "bishops"

    def populate_movable(self, queen=False) -> None:
        if not queen:
            self.safe_moves()
        if self.pinned:
            return

        # Coordinate pair zip objects for all possible moves
        # to be tested
        # Order of generation: left and up, left and down,
        # right and up, right and down
        for diag in self.diagonal_from:
            for crd in diag:
                if self.b[crd].piece:
                    if self.b[crd].piece and self.b[crd].piece.color != self.color:
                        self.movable_spaces.add(crd)
                        break
                    break
                self.movable_spaces.add(crd)

    def attack_spaces(self):
        for axis in self.diagonal_from:
            for crd in axis:
                self.attacking_spaces.add(crd)
                if self.b[crd].piece:
                    break
        self.b.attack_spaces(self)

    def safe_moves(self) -> None:
        self.safe_on_axes(self.horizvert_from, Rook, True, None)
        if self.pinned:
            return

        def bishop_pin_gen(king, pinning_piece):
            for coordinate in zip(
                        range(
                          king.rank + (1 if king.rank < self.rank else -1),
                          pinning_piece.rank + (-1 if pinning_piece.rank < self.rank else 1),
                          1 if king.rank < self.rank else -1
                        ),
                        range(
                          king.file + (1 if king.file < self.file else -1),
                          pinning_piece.file + (-1 if pinning_piece.file < self.file else 1),
                          1 if king.file < self.file else -1
                        )
                    ):
                if coordinate != self.coordinate:
                    yield coordinate

        self.safe_on_axes(self.diagonal_from, Bishop, False, bishop_pin_gen)

    @property
    def square_color(self) -> bool:
        return self.rank % 2 != self.file % 2

    def __repr__(self):
        return "B" if self.color else "b"
