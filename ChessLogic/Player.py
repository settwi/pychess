class Player:
    def __init__(self, color, input_pieces=None, board=None,):
        self.color = color
        self.b = board
        self.num_pieces = 0
        self.pieces = None
        self.init_pieces()
        if input_pieces:
            assert len(input_pieces['king']) == 1
            for key in self.pieces:
                self.pieces[key] = list(p for p in input_pieces[key])
                self.num_pieces += len(self.pieces[key])

    def add_piece(self, piece):
        self.pieces[piece.id].append(piece)
        self.num_pieces += 1

    def remove_piece(self, piece):
        try:
            self.pieces[piece.id].remove(piece)
        except:
            print("error removing piece:", piece.id)
            raise
        finally:
            self.num_pieces -= 1

    def init_pieces(self):
        self.reset_pieces()

    def reset_pieces(self):
        self.pieces = {
            'pawns': [],
            'rooks': [],
            'knights': [],
            'bishops': [],
            'queens': [],
            'king': [],
        }

    @property
    def rooks(self):
        return tuple(self.pieces['rooks'])

    @property
    def king(self):
        return self.pieces['king'][0]

    @property
    def in_check(self):
        return not all(
            p.color == self.color for
            p in self.b[self.king.coordinate].under_attack_by
        )
