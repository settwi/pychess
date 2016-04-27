import tkinter as tk
from ChessLogic import *
from ChessGraphics import GPieceGraveyard
from itertools import product


def _chess_coordinates():
    for rank, file in product(range(8), range(8)):
        yield rank, file


def _mod_move_color(color: tuple) -> str:
    return "#%02x%02x%02x" % (min(color[0]//256 + 50, 255), color[1]//256, 255)


class GPiece:
    piece_codes = {
        King: '\u265A',
        Queen: '\u265B',
        Rook: '\u265C',
        Bishop: '\u265D',
        Knight: '\u265E',
        Pawn: '\u265F',
    }

    def __init__(self, chess_piece=None):
        self.piece_repr = self.piece_codes.get(type(chess_piece))
        self.color = "white" if chess_piece and chess_piece.color else "black"

    def update_piece(self, new_piece):
        self.piece_repr = self.piece_codes.get(type(new_piece))
        self.color = "white" if new_piece and new_piece.color else "black"

    def __bool__(self):
        return self.piece_repr is not None


class GChessSquare(tk.Frame):
    def __init__(self, parent, coordinate=None, piece=None, handler=None, **kwargs):
        assert hasattr(handler, '__call__')
        self.mid = kwargs['width'] // 2
        self.piece_config = ("Arial", int(self.mid * 1.3))

        tk.Frame.__init__(self, parent, **kwargs)
        self.coordinate = coordinate
        self.logical_piece = piece

        self.piece_holster = GPiece(self.logical_piece)
        self.default_background = kwargs.get('bg') or kwargs.get('background') or "red"
        self.selected_color =\
            _mod_move_color(self.winfo_rgb(self.default_background))

        self.canvas = tk.Canvas(
            self,
            width=kwargs.get('width'),
            height=kwargs.get('height'),
            bg=self.default_background,
            highlightthickness=0,   # need this to make the squares flush
        )
        self.canvas.bind("<Button-1>", handler)
        self.canvas.pack()

        self.canvas_piece_id = self.canvas.create_text(
            (self.mid, self.mid),
            text=self.piece_holster.piece_repr,
            fill=self.piece_holster.color,
            font=self.piece_config,
        )

    def update_piece(self, new):
        assert isinstance(new, (type(None), Piece))
        self.logical_piece = new
        self.piece_holster.update_piece(new)
        self.canvas.delete(self.canvas_piece_id)
        self.canvas_piece_id = self.canvas.create_text(
            (self.mid, self.mid),
            text=self.piece_holster.piece_repr,
            fill=self.piece_holster.color,
            font=self.piece_config,
        )


class GChessBoard(tk.Frame):
    def __init__(
            self, parent, chess_info: ChessLogic, square_dim: int,
            on_endgame, on_promote, piece_graveyard: GPieceGraveyard,
            flip_board, **kw):
        kw['width'] = kw['height'] = 8 * square_dim
        tk.Frame.__init__(self, parent, **kw)

        # functions passed in that accept endgame exception
        # or promote exception
        self.endgame_handler = on_endgame
        self.promote_handler = on_promote

        # shows differences in material
        self.piece_graveyard = piece_graveyard

        self.dim = square_dim
        self.flip_board = flip_board
        self.chs = chess_info
        self.root_square = None
        self.squares = []

        for rank, file in product(range(8), range(8)):
            self.squares.append(
                GChessSquare(
                    self,
                    coordinate=(rank, file),
                    piece=self.chs[rank, file].piece,
                    handler=self.square_click_cb,
                    width=self.dim,
                    height=self.dim,
                    bg=("LightGoldenrod4" if rank % 2 == file % 2 else "navajowhite"),
                )
            )

        for rank, file in product(range(8), range(8)):
            self.squares[8*rank + file].grid(row=7-rank, column=file)

        menubar = _create_chess_menu(self)
        self.master['menu'] = menubar
        self.orient_board()

    def _finish_redo_or_undo(self):
        self.uncolor_spaces()
        self.update_piece_positions()
        self.piece_graveyard.update_pieces(self.chs.living_pieces)

    def undo_wrap(self, *_):
        self.chs.undo()
        self._finish_redo_or_undo()

    def redo_wrap(self, *_):
        self.chs.redo()
        self._finish_redo_or_undo()

    def resign_wrap(self, *_):
        try:
            self.chess.resign()
        # this is dumb?
        except EndgameException as end:
            self.at_end(end)

    @property
    def chess(self) -> ChessLogic:
        return self.chs

    def reset(self):
        self.chs = ChessLogic()
        self.update_piece_positions()
        self.orient_board()
        self.piece_graveyard.reset()

    def square_at(self, crd: tuple) -> GChessSquare:
        for sq in self.squares:
            if crd == sq.coordinate:
                return sq
        raise IndexError("index out of bounds")

    def uncolor_spaces(self) -> None:
        for sq in self.squares:
            sq.canvas['bg'] = sq.default_background

    def color_from_square(self, selected_square: GChessSquare) -> None:
        current_piece = selected_square.logical_piece
        if current_piece:
            selected_square.canvas['bg'] = selected_square.selected_color
            for crd in current_piece.movable_spaces:
                self.square_at(crd).canvas['bg'] = self.square_at(crd).selected_color

    def _crd_mod(self, *crd) -> tuple:
        if self.chs.moving_player:
            return crd
        else:
            return 7 - crd[0], 7 - crd[1]

    def orient_board(self):
        if self.flip_board:
            for rank, file in product(range(8), range(8)):
                self.squares[8*rank+file].coordinate = self._crd_mod(rank, file)
            self.update_piece_positions()
        self.uncolor_spaces()

    def update_piece_positions(self):
        for space, crd in zip(self.chs, _chess_coordinates()):
            self.square_at(crd).update_piece(space.piece)

    def clear_root_square(self):
        self.root_square = None
        self.uncolor_spaces()

    def at_end(self, end: EndgameException):
        self.uncolor_spaces()
        self.update_piece_positions()
        self.endgame_handler(self, end)

    def square_click_cb(self, evt):
        if self.chs.checkmate:
            self.uncolor_spaces()
            return

        bounding_sq = evt.widget.master
        if self.root_square is None:
            self.root_square = bounding_sq
            # Make sure it's the right color, etc
            try:
                self.chs.piece_at(self.root_square.coordinate)
            except PieceError:
                self.root_square = None
                return
            self.color_from_square(bounding_sq)
        elif self.root_square == bounding_sq:
            self.clear_root_square()
            return
        elif self.root_square != bounding_sq:
            self.uncolor_spaces()
            self.color_from_square(bounding_sq)

        if self.root_square.logical_piece:
            if self.root_square != bounding_sq:
                current_piece = self.root_square.logical_piece
                if current_piece:
                    if bounding_sq.coordinate in current_piece.movable_spaces:
                        try:
                            self.chs.move(
                                self.root_square.coordinate,
                                bounding_sq.coordinate
                            )
                        except PieceError as e:
                            print(str(e))
                        except Take:
                            self.update_piece_positions()
                            self.orient_board()
                        except Promote as prmt:
                            try:
                                self.update_piece_positions()
                                self.uncolor_spaces()
                                promote_to = self.promote_handler(prmt)
                                self.orient_board()
                                self.chs.promote(prmt.which, promote_to)
                                self.update_piece_positions()
                            except EndgameException as end:
                                self.at_end(end)
                        except EndgameException as end:
                                self.at_end(end)
                        else:
                            self.update_piece_positions()
                            self.orient_board()
                        finally:
                            self.clear_root_square()
                    else:
                        self.clear_root_square()
                        # Now that root_square is cleared, let's
                        # re-call with an "empty" square.
                        self.square_click_cb(evt)

        elif bounding_sq.logical_piece is None:
            self.clear_root_square()

        self.piece_graveyard.update_pieces(self.chs.living_pieces)


def _create_chess_menu(chess_board: GChessBoard) -> tk.Menu:
    chess_logic = chess_board.chess
    root = chess_board.master
    menubar = tk.Menu(root)
    game_menu = tk.Menu(menubar)
    game_menu.add_command(label="Undo", command=chess_board.undo_wrap,
                          accelerator="Command+U")
    game_menu.add_command(label="Redo", command=chess_board.redo_wrap,
                          accelerator="Command+R")
    game_menu.add_command(label="Resign", command=chess_board.resign_wrap)
    game_menu.bind_all("<Command-u>", chess_board.undo_wrap)
    game_menu.bind_all("<Command-r>", chess_board.redo_wrap)

    menubar.add_cascade(label="Game", menu=game_menu)

    return menubar