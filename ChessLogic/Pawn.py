from ChessLogic.Piece import Piece
from ChessLogic.Bishop import Bishop
from ChessLogic.Rook import Rook

from ChessLogic.Space import Take


class Pawn(Piece):
    id = "pawns"

    def __init__(self, board, rank, file, color=True):
        Piece.__init__(self, board, rank, file, color)
        self.en_passant = False
        self.en_passant_last_move = False
        self.ep_take = False
        self.promote = False

    @property
    def first_move(self):
        if self.color:
            return self.rank == 1
        else:
            return self.rank == 6

    def _rank_offset(self, num) -> int:
        return self.rank + (num if self.color else -num)

    def populate_movable(self) -> None:
        self.safe_moves()
        if self.pinned:
            return

        r_by_1 = self._rank_offset(1)
        if r_by_1 < 0 or r_by_1 > 7:
            return

        if self.first_move:
            r_by_2 = self._rank_offset(2)
            if 0 <= r_by_2 <= 7:
                try:
                    if not self.b[r_by_2, self.file].piece and not self.b[r_by_1, self.file].piece:
                        self.movable_spaces.add((r_by_2, self.file))
                except AttributeError:
                    self.movable_spaces.add((r_by_2, self.file))

        if not self.b[r_by_1, self.file].piece and (
            0 <= r_by_1 <= 7 and 0 <= self.file <= 7
        ):
            self.movable_spaces.add((r_by_1, self.file))

        for attack_f in (self.file + 1, self.file - 1):
            if 0 <= attack_f <= 7:
                atk_piece = self.b[r_by_1, attack_f].piece
                adj_piece = self.b[self.rank, attack_f].piece
                if (atk_piece and atk_piece.color != self.color) or (
                    hasattr(adj_piece, 'en_passant') and adj_piece.en_passant
                ):
                    self.movable_spaces.add((r_by_1, attack_f))
                self.attacking_spaces.add((r_by_1, attack_f))

    def attack_spaces(self) -> None:
        # movable exclusive from attacking for pawns
        self.b.attack_spaces(self)

    def safe_moves(self) -> None:
        def rook_gen(king, piece):
            if king.file == piece.file:
                if self.first_move:
                    max_offset = 2
                else:
                    max_offset = 1

                max_rank = (max if self.color else min)(
                        king.rank,
                        self._rank_offset(max_offset)
                )
                for move_rank in range(
                        self.rank,
                        max_rank + (-1 if max_rank < self.rank else 1),
                        (-1 if max_rank < self.rank else 1)
                ):
                    if not self.b[move_rank, self.file].piece:
                        yield move_rank, self.file
            else:
                return ()

        self.safe_on_axes(self.horizvert_from, Rook, False, rook_gen)
        if self.pinned:
            return

        def bishop_gen(_, piece):
            off_rank = self._rank_offset(1)
            if piece.coordinate == (off_rank, self.file + 1):
                yield (off_rank, self.file + 1)
            if piece.coordinate == (off_rank, self.file - 1):
                yield (off_rank, self.file - 1)
            return ()

        # if self.pinned is False, then we're golden to generate moves.
        # else, we need to just return
        self.safe_on_axes(self.diagonal_from, Bishop, self.pinned, bishop_gen)

    def move(self, rank: int, file: int) -> None:
        old_rank = self.rank
        self.ep_take = False
        try:
            # There might be a better way to do this,
            # but this is the best I can think of atm.
            self.ep_take = (
                (rank, file) in self.attacking_spaces and
                self.b[rank, file].piece is None
            )
            self._pawn_move(rank, file)
        finally:
            if self.rank == (7 if self.color else 0):
                self.promote = True
            if self._rank_offset(-2) == old_rank:
                self.en_passant_last_move = self.en_passant = True

    def _pawn_move(self, rank: int, file: int) -> None:
        if (rank, file) in self.movable_spaces:
            old_crd = self.coordinate
            self.b[self.coordinate].piece = None
            self.coordinate = rank, file
            self.b[self.coordinate].piece = self
            if self.ep_take:
                ep_pawn = self.b[old_crd[0], file].piece
                self.b[old_crd[0], file].piece = None
                raise Take(ep_pawn)

    def __repr__(self): return "P" if self.color else "p"
