from ChessLogic.Bishop import Bishop
from ChessLogic.Rook import Rook
from ChessLogic.King import King
from ChessLogic.Knight import Knight
from ChessLogic.Pawn import Pawn
from ChessLogic.Piece import Piece
from ChessLogic.Player import Player
from ChessLogic.Queen import Queen
from ChessLogic.Space import Space

from sys import stderr


class Promote(Exception):
    def __init__(self, promote_piece, *args):
        self.which = promote_piece
        EndgameException.__init__(self, *args)


class EndgameException(Exception):
    pass


class Checkmate(EndgameException):
    def __init__(self, mated_color, *args):
        self.mated_color = mated_color
        EndgameException.__init__(self, "Checkmate\n{}-{}".format(int(not mated_color), int(mated_color)), *args)


class Draw(EndgameException):
    def __init__(self, *args):
        EndgameException.__init__(self, "Draw\n1/2-1/2", *args)


class Stalemate(Draw):
    def __init__(self, *args):
        EndgameException.__init__(self, "Stalemate\n1/2-1/2", *args)


class Resign(EndgameException):
    def __init__(self, resigning_color, *args):
        resigning_name = "White" if resigning_color else "Black"
        EndgameException.__init__(self,
                                  "{} Resigns\n{}-{}".format(
                                      resigning_name, int(not resigning_color), int(resigning_color)), *args)


class Board:
    def __init__(self, fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
        self.moving_player = True
        # white_pieces, black_pieces = dict(), dict()
        self.spaces = [[Space() for _ in range(8)] for _ in range(8)]
        self._undo_moves = []
        self._redo_moves = []
        # this is a dict so referencing players not dependant upon order of True, False
        self.players = {
            False: Player(False, None, self),
            True: Player(True, None, self)
        }

        self._construct_from_fen(fen)

    def __getitem__(self, idx):
        try:
            return self.spaces[idx[0]][idx[1]]
        except IndexError:
            print("getting ChessLogic square", idx, file=stderr)
            raise

    def add_undo(self) -> None:
        self._undo_moves.append(self._to_fen())
        self._redo_moves.clear()

    def undo(self):
        if self._undo_moves:
            last_move = self._undo_moves.pop()
            # need both so that redo can add undo. look below
            self._redo_moves.append(last_move)
            self._redo_moves.append(self._to_fen())
            self._construct_from_fen(last_move)

    # fix this...
    def redo(self):
        if self._redo_moves:
            next_move = self._redo_moves.pop()
            self._undo_moves.append(self._redo_moves.pop())
            self._construct_from_fen(next_move)
        else:
            print("LOLWTF")

    @staticmethod
    def from_alg_crd(alg_crd: str) -> tuple:
        return int(alg_crd[1]) - 1, ord(alg_crd[0]) - ord('a')

    @staticmethod
    def to_alg_crd(internal_crd: tuple) -> str:
        return chr(ord('a') + internal_crd[0]) + str(internal_crd[1] + 1)

    def _to_fen(self) -> str:
        fen_rows = [[] for _ in range(8)]
        for r_idx, row in enumerate(reversed(self.spaces)):
            empty_spaces = 0
            for space in row:
                if space.piece is None:
                    empty_spaces += 1
                else:
                    if empty_spaces != 0:
                        fen_rows[r_idx].append(str(empty_spaces))
                        empty_spaces = 0
                    # uses written __repr__ to return proper string
                    fen_rows[r_idx].append(str(space.piece))
            if empty_spaces != 0:
                fen_rows[r_idx].append(str(empty_spaces))

        final_information = list()
        final_information.append('/'.join(''.join(row) for row in fen_rows))
        final_information.append('w' if self.moving_player else 'b')
        castling_rights = ""
        for color in (True, False):
            color_rights = self.can_castle(color, for_fen=True)
            castling_rights += (("K" if color else "k") if color_rights[0] else '')
            castling_rights += (("Q" if color else "q") if color_rights[1] else '')
        final_information.append(castling_rights)
        for space in self.spaces[4 - int(self.moving_player)]:
            if isinstance(space.piece, Pawn):
                if space.piece.en_passant:
                    final_information.append(self.to_alg_crd(space.piece.coordinate))
                    break
        if len(final_information) != 4:
            final_information.append('-')

        return "{} {} {} {} 0 0".format(*final_information)

    def _construct_from_fen(self, fen):
        self.spaces = [[Space() for _ in range(8)] for _ in range(8)]
        for player in self.players.values():
            player.reset_pieces()

        fen = fen.split(' ')
        # flip this because refresh... flips moving player
        self.moving_player = (fen[1] == 'w')
        castle_rights = (
            'K' not in fen[2], 'Q' not in fen[2],
            'k' not in fen[2], 'q' not in fen[2]
        )
        starting_rook_crds = (
            (0, 0), (0, 7),
            (7, 0), (7, 7)
        )
        pieces = {
            'P': Pawn, 'R': Rook,
            'N': Knight, 'B': Bishop,
            'Q': Queen, 'K': King,
        }

        def format_fen_row(row):
            row = list(row)
            for idx, ch in enumerate(row):
                try:
                    row[idx] = ''.join('_' for _ in range(int(ch)))
                except ValueError:
                    pass
            return ''.join(row)

        for rank, fixed_row in enumerate(map(format_fen_row, reversed(fen[0].split('/')))):
            for file, piece_ch in enumerate(fixed_row):
                if piece_ch == '_':
                    self[rank, file].piece = None
                    continue
                color = piece_ch.isupper()
                piece = pieces[piece_ch.upper()](self, rank, file, color)
                self.players[color].add_piece(piece)
                self[rank, file].piece = piece

        for i, crd in enumerate(starting_rook_crds):
            try:
                self[crd].piece.has_moved = castle_rights[i]
            except AttributeError:
                pass

        if fen[3] != '-':
            ep_crd = ep_rank, ep_file = self.from_alg_crd(fen[3])
            if ep_rank == 5:
                ep_pawn = self[ep_rank-1, ep_file].piece
            else:
                ep_pawn = self[ep_rank+1, ep_file].piece
            ep_pawn.en_passant = ep_pawn.en_passant_last_move = True

            for player in self.players.values():
                for pawn in player.pieces['pawns']:
                    if ep_crd in pawn.attacking_spaces:
                        pawn.add_movable(ep_crd)

        self.refresh(False)

    def attack_spaces(self, piece: Piece) -> None:
        for crd in piece.attacking_spaces:
            self[crd].under_attack_by.add(piece)

    def unattack_spaces(self, piece: Piece) -> None:
        for crd in piece.attacking_spaces:
            if piece in self[crd].under_attack_by:
                self[crd].under_attack_by.remove(piece)

    def refresh(self, switch_color=True) -> None:
        promote_piece = None

        for player in self.players.values():
            for key in player.pieces:
                if key != 'king':
                    for p in player.pieces[key]:
                        if key == 'pawns':
                            if p.en_passant_last_move:
                                p.en_passant_last_move = False
                            elif p.en_passant:
                                p.en_passant = False
                            elif p.promote:
                                promote_piece = p
                        p.refresh()

        for player in self.players.values():
            for p_type in player.pieces:
                if p_type != 'king':
                    for p in player.pieces[p_type]:
                        p.refresh()

        # King moves restricted by attacks, so
        # he gets a separate little loop
        for player in self.players.values():
            player.king.refresh()

        if switch_color:
            self.moving_player = not self.moving_player

        if promote_piece:
            try:
                cur_player = self.players[promote_piece.color]
                cur_player.remove_piece(promote_piece)
            finally:
                raise Promote(promote_piece)

        self.detect_draw_or_stalemate()

    def detect_draw_or_stalemate(self):
        def cmp_to_pcs(p, identifier):
            return len(p.pieces[identifier]) == p.num_pieces - 1

        for cur_player in self.players.values():
            if cur_player.in_check:
                self.handle_check(cur_player.color)
                break

            opp_player = self.players[not cur_player.color]
            if opp_player.num_pieces == 1:
                only_bishops = cmp_to_pcs(cur_player, 'bishops')
                sq_color = cur_player.pieces['bishops'][0].square_color
                if only_bishops:
                    if all(p.square_color == sq_color for p in cur_player.pieces['bishops']):
                        raise Draw("Insufficient material")

                if 1 + len(cur_player['bishops']) + len(cur_player['knights']) == cur_player.num_pieces:
                    raise Draw("Insufficient Material")

                if cur_player.num_pieces == 1 or (
                    sum(len(p.movable_spaces)
                        for piece_list in cur_player.pieces
                        for p in piece_list) == len(cur_player.king.movable_spaces)):
                    if not cur_player.in_check and not cur_player.king.movable_spaces:
                        raise Stalemate

                if opp_player.num_pieces == cur_player.num_pieces == 1:
                    raise Draw("Bare kings")

    def promote(self, piece: Piece, to: str) -> None:
        new_piece = None
        try:
            to = to.upper()
            promote_space = self[piece.coordinate]
            new_piece = ({
                'Q': Queen,
                'R': Rook,
                'B': Bishop,
                'N': Knight,
            }.get(to, Queen).from_piece(piece))
            promote_space.piece = None
            promote_space.piece = new_piece
        finally:
            if new_piece:
                self.players[piece.color].add_piece(new_piece)
            try:
                self.refresh()
            finally:
                self.moving_player = not new_piece.color

    def can_castle(self, color: bool, for_fen=False) -> tuple:
        if self.players[color].in_check:
            return False, False
        if self.players[color].king.has_moved:
            return False, False
        kingside = queenside = False
        side = 7 * (not color)

        for rook in self.players[color].rooks:
            if not rook.has_moved:
                if rook.coordinate == (side, 0):
                    queenside = True
                elif rook.coordinate == (side, 7):
                    kingside = True

        # Kingside coordinates
        for crd in ((side, f) for f in range(5, 7)):
            s = self[crd]
            if not all(p.color == color for p in s.under_attack_by) or (not for_fen and s.piece is not None):
                kingside = False
                break

        # Queenside's
        for crd in ((side, f) for f in range(2, 4)):
            s = self[crd]
            if not all(p.color == color for p in s.under_attack_by) or (not for_fen and s.piece is not None):
                queenside = False
                break

        return kingside, queenside

    def complete_castle(self, color, side, fromcrd):
        rook = next(
            rk for rk in self.players[color].rooks
            if rk.coordinate == fromcrd
        )

        if side == 'q':
            new_rook_crd = (not color) * 7, 3
        elif side == 'k':
            new_rook_crd = (not color) * 7, 5
        else:
            raise ValueError("invalid castle side")
        self[rook.coordinate].piece = None
        self[new_rook_crd].piece = rook
        rook.coordinate = new_rook_crd

    def handle_check(self, color: bool) -> None:
        checked_player = self.players[color]
        checked_king = checked_player.king
        king_space = self[checked_king.coordinate]
        checking_pieces = tuple(
            p for p in king_space.under_attack_by
            if p.color != checked_player.color
        )
        main_check_piece = None
        total_movable_spaces = set()
        for piece in checking_pieces:
            if isinstance(piece, (Bishop, Rook)):
                main_check_piece = piece
                break
        if not main_check_piece:
            main_check_piece = checking_pieces[0]

        checked_king.restrict_check(main_check_piece)

        if len(checking_pieces) == 1:
            check_axis = None
            for axes in (main_check_piece.horizvert_from, main_check_piece.diagonal_from):
                for axis in axes:
                    if checked_king.coordinate in axis:
                        check_axis = set(axis)
                        break
                if check_axis:
                    break

            check_space = self[main_check_piece.coordinate]
            for key, piece_list in checked_player.pieces.items():
                if key != 'king':
                    for piece in piece_list:
                        if isinstance(main_check_piece, Knight):
                            piece.clear_movable()
                        else:
                            piece.movable_spaces &= main_check_piece.attacking_spaces
                            if check_axis:
                                piece.movable_spaces &= check_axis

                        if piece in check_space.under_attack_by:
                            piece.add_movable(main_check_piece.coordinate)

                        total_movable_spaces |= piece.movable_spaces
        else:
            for key, piece_list in checked_player.pieces.items():
                if key != 'king':
                    for piece in piece_list:
                        piece.clear_movable()

        if not total_movable_spaces and not checked_king.movable_spaces:
            raise Checkmate(color)
