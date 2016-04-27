from ChessLogic.Board import Checkmate, Promote, Resign, Draw, Stalemate, EndgameException, Board

from ChessLogic.Bishop import Bishop
from ChessLogic.Rook import Rook
from ChessLogic.King import King
from ChessLogic.Knight import Knight
from ChessLogic.Pawn import Pawn
from ChessLogic.Piece import Piece
from ChessLogic.Player import Player
from ChessLogic.Queen import Queen
from ChessLogic.Space import Take


class PieceError(Exception):
    pass


class ChessLogic:
    def __init__(self, fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
        try:
            self.board = Board(fen=fen)
        except Checkmate:
            self.checkmate = True
            raise
        self.checkmate = False

    @classmethod
    def from_fen(cls, fen_str):
        return cls(fen_str)

    def __getitem__(self, idx):
        return self.board.__getitem__(idx)

    def __iter__(self):
        for rank in self.board.spaces:
            for space in rank:
                yield space

    def undo(self):
        self.board.undo()

    def redo(self):
        self.board.redo()

    def promote(self, piece: Piece, promote_to: str) -> None:
        self.board.promote(piece, promote_to)

    def piece_at(self, crd) -> Piece:
        pc = self.board[crd].piece
        try:
            if self.board.moving_player != pc.color:
                raise PieceError("Wrong color")
            else:
                return pc
        except AttributeError:
            return pc

    def _move_piece(self, fromcrd: tuple, tocrd: tuple) -> None:
        piece = self.piece_at(fromcrd)
        if tocrd not in piece.movable_spaces:
            raise PieceError("Not a movable coordinate")
        self.board.add_undo()
        piece.move(*tocrd)

    def verify_piece(self, fromcrd: tuple) -> None:
        cur_piece = self.board[fromcrd].piece
        if not cur_piece:
            raise PieceError("not cur_piece")

        if self.board.moving_player != cur_piece.color:
            raise PieceError("self.board.moving_player != cur_piece.color")

    def move(self, fromcrd: tuple, tocrd: tuple) -> None:
        refresh_board = True
        try:
            try:
                self.verify_piece(fromcrd)
                self._move_piece(fromcrd, tocrd)
            except PieceError:
                refresh_board = False
                raise
            except Take as t:
                self.board.players[t.taken_piece.color].remove_piece(t.taken_piece)
                raise
            finally:
                if refresh_board:
                    self.board.refresh()
        except EndgameException:
            self.checkmate = True
            raise

    @property
    def moving_player(self):
        return self.board.moving_player

    @property
    def living_pieces(self) -> dict:
        return {
            'white': self.board.players[True].pieces,
            'black': self.board.players[False].pieces,
        }

    def resign(self):
        raise Resign(self.moving_player)


def print_board(chs, piece) -> None:
    for rank in range(7, -1, -1):
        for file in range(8):
            if piece and piece.coordinate == (rank, file):
                print("***", end='')
            elif piece and ((rank, file) in piece.movable_spaces):
                print("{%s}" % (repr(chs[rank, file])[1] if chs[rank, file].piece else "X"), end='')
            else:
                print(chs[rank, file], end='')
        print("")


# todo: stalemate, draw (insufficient material, bare kings)
def chess_game(chs: ChessLogic):
    while True:
        try:
            print_board(chs.board, None)

            try:
                fromcrd = tuple(int(x) for x in input("From: ").split(','))
                cur_piece = chs.piece_at(fromcrd)
                print(cur_piece.movable_spaces)
                print_board(chs.board, cur_piece)
                tocrd = tuple(int(x) for x in input("To: ").split(','))
                chs.move(fromcrd, tocrd)
            except Take as tke:
                print(
                    "{} {} takes {}!".format(
                        "White" if cur_piece.color else "Black",
                        cur_piece, tke.taken_piece)
                )
            except Promote as prmt:
                chs.promote(prmt.which, 'Q')
            except PieceError as pe:
                print(pe)
                continue
            except Checkmate as cm:
                print("{}-{}".format(int(not cm.mated_color), int(cm.mated_color)))
                print("{} wins.".format("White" if cm.mated_color else "Black"))
                print_board(chs, None)
                return
            except (Stalemate, Draw):
                print("1/2-1/2")
                return
        except (ValueError, IndexError) as er:
            print(' | '.join(er.args))
            continue


def move_progressions(chs, moves, color):
    chs.board.moving_player = True
    for move in moves:
        try:
            f, t = move
            print_board(chs.board, chs.piece_at(f))
            chs.move(f, t)
        except Take as t:
            print(t)
            # hi :)
        except Checkmate as cm:
            print("{}-{}".format(int(not cm.mated_color), int(cm.mated_color)))
        except Promote as p:
            print("Promote: " + str(p))

if __name__ == '__main__':
    chs = ChessLogic()
    bishop_moves = (
        ((1, 3), (3, 3)),
        ((6, 4), (4, 4)),
        ((0, 2), (1, 3)),
        ((7, 5), (3, 1)),
    )
    rook_queen_moves = (
        ((1, 4), (3, 4)),
        ((6, 3), (4, 3)),
        ((3, 4), (4, 3)),
        ((6, 4), (5, 4)),
        ((5, 4), (4, 3)),
        ((0, 3), (1, 4)),
        ((7, 3), (6, 4)),
    )
    pawn_promote_moves = (
        ((1, 3), (3, 3)),
        ((6, 4), (5, 4)),
        ((3, 3), (4, 3)),
        ((5, 4), (4, 4)),
        ((4, 3), (5, 3)),
        ((4, 4), (3, 4)),
    )
    en_passant_moves = (
        ((1, 3), (3, 3)),
        ((3, 3), (4, 3)),
        ((6, 4), (4, 4)),
        ((4, 3), (5, 4)),
    )
    kingside_castle_moves = (
        ((1, 4), (3, 4)),
        ((0, 5), (3, 2)),
        ((0, 6), (2, 5)),
    )
    fools_mate = (
        ((1, 5), (3, 5)),
        ((6, 4), (5, 4)),
        ((1, 6), (3, 6)),
    )
    queen_restrict = (
        ((1, 4), (3, 4)),
        ((6, 4), (4, 4)),
        ((1, 3), (3, 3)),
        ((6, 3), (4, 3)),
        ((3, 4), (4, 3)),
        ((4, 4), (3, 3)),
        ((0, 3), (1, 4)),
        ((7, 3), (6, 4)),
        ((1, 4), (2, 4))
    )
    #move_progressions(chs, bishop_moves, True)
    #chess_game(chs)

'''
rank, file
7,0 7,1 7,2 7,3 7,4 7,5 7,6 7,7
6,0 6,1 6,2 6,3 6,4 6,5 6,6 6,7
5,0 5,1 5,2 5,3 5,4 5,5 5,6 5,7
4,0 4,1 4,2 4,3 4,4 4,5 4,6 4,7
3,0 3,1 3,2 3,3 3,4 3,5 3,6 3,7
2,0 2,1 2,2 2,3 2,4 2,5 2,6 2,7
1,0 1,1 1,2 1,3 1,4 1,5 1,6 1,7
0,0 0,1 0,2 0,3 0,4 0,5 0,6 0,7
'''
