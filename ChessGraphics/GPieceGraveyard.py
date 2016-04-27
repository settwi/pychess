import tkinter as tk
from ChessLogic import ChessLogic

_display_pieces = {
        'queens': '\u265B',   # queen
        'rooks': '\u265C',   # rook
        'bishops': '\u265D',   # bishop
        'knights': '\u265E',   # knight
        'pawns': '\u265F',   # pawn
    }


class GPieceDisplay(tk.Canvas):
    def __init__(self, parent, color, piece_type="", **kw):
        tk.Canvas.__init__(self, parent, **kw)
        self.counter_crd = (int(self['width'])//4, int(self['height'])//2)
        piece_crd = (int(int(self['width']) * 0.75), int(self['height'])//2)
        self.num_pieces = 0
        self.piece_char = _display_pieces.get(piece_type, '?')
        self.font = ["Arial", str(int(int(self['height']) * 0.5))]
        self._piece_id = self.create_text(
            piece_crd,
            text=self.piece_char,
            fill="gray" if color else "black",
            font=self.font
        )
        self.amt_id = self.create_text(
            self.counter_crd,
            text="0",
            fill="gray" if color else "black",
            font=self.font
        )

    def update_difference(self, amt: int):
        if amt < 0 and len(self.font) == 2:
            self.font.append("bold")
        elif amt >= 0 and len(self.font) == 3:
            self.font.pop()
        self.num_pieces = max(amt, 0)
        self.delete(self.amt_id)
        self.amt_id = self.create_text(
            self.counter_crd,
            text=str(self.num_pieces),
            font=self.font,
        )


class GGraveyardFrame(tk.LabelFrame):
    def __init__(self, parent, color, **kw):
        tk.LabelFrame.__init__(self, parent, **kw)
        display_height = self['height']//5.3

        self.piece_displays = {
            key: GPieceDisplay(
                self,
                color=color,
                piece_type=key,
                width=self['width'],
                height=display_height,
                highlightthickness=0
            ) for key in _display_pieces
        }
        for key in ('queens', 'rooks', 'bishops', 'knights', 'pawns'):
            self.piece_displays[key].pack()

    def update_pieces(self, living_pieces: dict) -> None:
        for piece_type, piece_amt in living_pieces.items():
            self.piece_displays[piece_type].update_difference(piece_amt)


class GPieceGraveyard(tk.Frame):
    default_piece_amounts = {
        'pawns': 8,
        'rooks': 2,
        'knights': 2,
        'bishops': 2,
        'queens': 1
    }

    def __init__(self, parent, chess_info: ChessLogic, chessboard_dim: int, **kw):
        kw['width'] = chessboard_dim * 3
        kw['height'] = chessboard_dim * 8
        tk.Frame.__init__(self, parent, **kw)
        self.white_frame = GGraveyardFrame(
            self,
            color=False,
            width=self['width'],
            height=self['height']//2,
            text="White Taken"
        )
        self.black_frame = GGraveyardFrame(
            self,
            color=True,
            width=self['width'],
            height=self['height']//2,
            text="Black Taken"
        )
        self.piece_frames = {
            'white': self.white_frame,
            'black': self.black_frame
        }
        for frame in self.piece_frames.values():
            frame.pack()
        self.dim = chessboard_dim // 3
        self.piece_differences = {
            'white': dict(),
            'black': dict()
        }
        self.update_pieces(chess_info.living_pieces)

    def update_pieces(self, living_pieces: dict) -> None:
        for side in living_pieces:
            for piece_type in living_pieces[side]:
                if piece_type != 'king':
                    other_side = 'white' if side == 'black' else 'black'
                    self.piece_differences[other_side][piece_type] =\
                        self.default_piece_amounts[piece_type] -\
                        len(living_pieces[side][piece_type])

        self.update_graphical_pieces()

    def update_graphical_pieces(self):
        for color in self.piece_frames:
            self.piece_frames[color].update_pieces(self.piece_differences[color])

    def reset(self):
        pass
