from ChessLogic.Piece import Piece


class Rook(Piece):
    id = "rooks"

    def __init__(self, board, rank, file, color=True):
        Piece.__init__(self, board, rank, file, color)

    def populate_movable(self, queen=False):
        if not queen:
            self.safe_moves()
        if self.pinned:
            return

        for direction in self.horizvert_from:
            for rank, file in direction:
                if self.b[rank, file].piece:
                    if self.b[rank, file].piece.color != self.color:
                        self.movable_spaces.add((rank, file))
                        break
                    break
                self.movable_spaces.add((rank, file))

    def attack_spaces(self):
        for axis in self.horizvert_from:
            for crd in axis:
                self.attacking_spaces.add(crd)
                if self.b[crd].piece:
                    break
        self.b.attack_spaces(self)

    def safe_moves(self):
        from ChessLogic.Bishop import Bishop
        self.safe_on_axes(self.diagonal_from, Bishop, True, None)
        if self.pinned:
            return

        def rook_pin_gen(king, pinning_piece):
            if king.rank == pinning_piece.rank:
                for f in range(pinning_piece.file, king.file,
                               -1 if king.file < pinning_piece.file else 1):
                    yield (self.rank, f)
            else:
                for r in range(pinning_piece.rank, king.rank,
                               -1 if king.rank < pinning_piece.rank else 1):
                    yield (r, self.file)

        self.safe_on_axes(self.horizvert_from, Rook, False, rook_pin_gen)

    def __repr__(self): return "R" if self.color else "r"
