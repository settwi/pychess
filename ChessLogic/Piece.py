class Piece:
    id = "ERROR: PIECE IS ABSTRACT"

    def __init__(self, board, rank, file, color):
        self.rank = rank
        self.file = file
        self.starting_coordinate = (rank, file)
        self.color = color
        self.b = board
        self.pinned = False
        self.movable_spaces = set()
        self.attacking_spaces = set()

    @classmethod
    def from_piece(cls, piece):
        return cls(piece.b, piece.rank, piece.file, piece.color)

    def populate_movable(self) -> None:
        raise NotImplementedError

    def clear_movable(self):
        self.movable_spaces.clear()

    def add_movable(self, crd: tuple):
        self.movable_spaces.add(crd)

    def attack_spaces(self) -> None:
        self.attacking_spaces.update(self.movable_spaces)
        self.b.attack_spaces(self, self.attacking_spaces)

    def unattack_spaces(self) -> None:
        self.b.unattack_spaces(self)
        self.attacking_spaces.clear()

    def refresh(self):
        self.pinned = False
        self.unattack_spaces()
        self.clear_movable()
        self.populate_movable()
        self.attack_spaces()

    @property
    def diagonal_from(self) -> tuple:
        # 0    3
        #
        # 1    2
        return (
            tuple(zip(range(self.rank + 1, 8), range(self.file - 1, -1, -1))),
            tuple(zip(range(self.rank - 1, -1, -1), range(self.file - 1, -1, -1))),
            tuple(zip(range(self.rank - 1, -1, -1), range(self.file + 1, 8))),
            tuple(zip(range(self.rank + 1, 8), range(self.file + 1, 8))),
        )

    @property
    def horizvert_from(self) -> tuple:
        # horizontal, vertical
        #   1
        # 0   2
        #   3
        return (
            tuple((self.rank, file) for file in range(self.file - 1, -1, -1)),
            tuple((rank, self.file) for rank in range(self.rank + 1, 8)),
            tuple((self.rank, file) for file in range(self.file + 1, 8)),
            tuple((rank, self.file) for rank in range(self.rank - 1, -1, -1)),
        )

    @property
    def coordinate(self) -> tuple:
        return self.rank, self.file

    @coordinate.setter
    def coordinate(self, new: tuple) -> None:
        assert isinstance(new, tuple)
        self.rank, self.file = new[0], new[1]

    @property
    def has_moved(self):
        return self.coordinate != self.starting_coordinate

    def safe_moves(self) -> None:
        raise NotImplementedError

    def _king_piece_intersect(self, axes, idx, attacking_piece_type, piece, king):
        return piece.color != self.color and isinstance(piece, attacking_piece_type) and (
            piece.coordinate in axes[idx] or piece.coordinate in axes[(idx+2)%4]) and (
            king.coordinate in axes[idx] or king.coordinate in axes[(idx+2)%4]
        )

    def safe_on_axes(self, axes, attacking_piece_type, absolute_pin, pinned_gen) -> None:
        king = self.b.players[self.color].king
        attacking_pieces = frozenset(
            p for p in self.b[self.coordinate].under_attack_by
            if p.color != self.color
        )

        for i, axis in enumerate(axes):
            for crd in axis:
                cur_piece = self.b[crd].piece
                if cur_piece and cur_piece != king:
                    break
                elif cur_piece == king:
                    for piece in attacking_pieces:
                        if self._king_piece_intersect(axes, i, attacking_piece_type, piece, king):
                            if not absolute_pin:
                                self.pinned = True
                                self.movable_spaces |= set(c for c in pinned_gen(king, piece))
                                return
                            else:
                                self.pinned = True
                                return

    def move(self, rank: int, file: int) -> None:
        if (rank, file) in self.movable_spaces:
            old_crd = self.coordinate
            self.b[self.coordinate].piece = None
            self.rank, self.file = rank, file
            self.b[self.coordinate].piece = self

    def __repr__(self):
        return "WTF"
