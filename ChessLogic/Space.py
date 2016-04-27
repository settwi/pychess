class Take(Exception):
    def __init__(self, taken_piece, *args, **kwargs):
        self.taken_piece = taken_piece
        Exception.__init__(self, str(taken_piece) + " taken", *args, **kwargs)


class Space:
    def __init__(self, piece=None):
        self.under_attack_by = set()
        self._piece = piece

    @property
    def piece(self):
        return self._piece

    @piece.setter
    def piece(self, new=None) -> None:
        if self._piece and new:
            old_piece = self._piece
            self._piece = new
            old_piece.unattack_spaces()
            raise Take(old_piece)
        self._piece = new
    
    def __repr__(self):
        return "[_]" if not self.piece else repr(self.piece)
