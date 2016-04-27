import tkinter as tk
import tkinter.messagebox

from ChessGraphics import *
from ChessLogic import *
from functools import partial


def handle_endgame(board: GChessBoard, end: EndgameException):
    again = tk.messagebox.askyesno(
        "Game Over",
        str(end) + "\nWould you like to play again?"
    )
    if again:
        board.reset()


# todo: values and keys might be backwards
def handle_promote(_: Promote) -> str:
    promote_pieces = {
        '\u265B': 'Q',   # queen
        '\u265C': 'R',   # rook
        '\u265D': 'B',   # bishop
        '\u265E': 'N',   # knight
    }

    def _set_promote_to(pce: str, _: tk.Event):
        nonlocal promote_root, promote_to
        promote_root.quit()
        promote_root.destroy()
        promote_to = promote_pieces.get(pce, 'Q')

    def _color_bg(widget: tk.Widget, color: str, _: tk.Event):
        widget['bg'] = color

    promote_to = None
    promote_root = tk.Tk()
    promote_root.title("Promote")
    promote_root.resizable(False, False)

    for i, piece in enumerate(promote_pieces):
        piece_l = tk.Label(promote_root, text=piece, fg="blue", font=("Arial", 80))
        piece_l.bind("<Enter>", partial(_color_bg, piece_l, "gray"))
        piece_l.bind("<Leave>", partial(_color_bg, piece_l, "white"))
        piece_l.bind("<Button-1>", partial(_set_promote_to, piece))
        piece_l.grid(row=i//2, column=i%2)

    promote_root.mainloop()
    return promote_to or 'Q'


# todo: draw by insufficient material, rest of the interface,
if __name__ == '__main__':
    dim = 80
    chess_logic = ChessLogic()
    root = tk.Tk()
    root.title("Chess")
    graveyard = GPieceGraveyard(
        parent=root,
        chess_info=chess_logic,
        chessboard_dim=dim,
    )
    chess_board = GChessBoard(
        parent=root,
        chess_info=chess_logic,
        square_dim=dim,
        on_endgame=handle_endgame,
        on_promote=handle_promote,
        piece_graveyard=graveyard,
        flip_board=False,
    )
    chess_board.grid(row=0, column=0)
    graveyard.grid(row=0, column=1)
    root.resizable(False, False)
    root.mainloop()
