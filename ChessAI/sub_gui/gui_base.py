"""Base module for sub-tabs."""

import os
import pathlib

import tkinter as tk
from PIL import Image, ImageTk
import pygubu

from .movements import Movement, ALPHABET_DICT
from .tooltip import Tooltip

PROJECT_PATH: str = pathlib.Path(__file__).parent.parent

FEN_DICT: dict = {
    "P": "white_pawn.png",
    "B": "white_bishop.png",
    "N": "white_knight.png",
    "R": "white_rook.png",
    "Q": "white_queen.png",
    "K": "white_king.png",
    "p": "black_pawn.png",
    "b": "black_bishop.png",
    "n": "black_knight.png",
    "r": "black_rook.png",
    "q": "black_queen.png",
    "k": "black_king.png",
    "e": "empty.png",
}

MOVE_DICT: dict = {
    "x": "empty.png",
    " ": "empty.png",
    ".": "move.png",
    "o": "kill.png",
}

class ChessAIBase(Movement):
    """Base module for sub-tabs. (Or you might see as Home tab)"""
    def __init__(self):
        super().__init__()

        self.builder = pygubu.Builder()
        self.fen: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1" # default fen

        #dummy attributes
        self.advance_key = None
        self.chessboard = None
        self.move = None
        self.K = None
        self.Q = None
        self.k = None
        self.q = None
        self.mainwindow = None
        self.advance_dialog = None

    def fen_analyse(self, _: object):
        """Dummy function right now."""
        return

    def prepare_chessboard(self) -> None:
        """Yeah... Just dont want __init__ too complicated."""
        panel = self.builder.get_object('chessboard')

        # chessboard image setup
        img = Image.open(PROJECT_PATH / "UI_Assets/white_chessboard.png")
        # avoid to be deleted
        self.chessboard = ImageTk.PhotoImage(img)
        panel.create_image(0, 0, image=self.chessboard, anchor="nw")

        self.fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1" # default FEN
        self.update_chessboard()
        self.reset_moves()

        # for mouse moving with pieces
        self.update_image('select', 'chessboard', 0, 0)

        # for little checkboxes (castle)
        for p in ('K', 'Q', 'k', 'q'):
            setattr(self, p, self.builder.get_object('castle_' + FEN_DICT[p][:-4]))
            getattr(self, p).select()
            setattr(self, f'var_{p}', self.builder.get_variable(f'castle_{p}'))

        self.update_stats()

    def prepare_hover(self) -> None:
        """Some tooltips."""
        Tooltip(self.K, "If white can castle king side")
        Tooltip(self.Q, "If white can castle queen side")
        Tooltip(self.k, "If black can castle king side")
        Tooltip(self.q, "If black can castle queen side")
        Tooltip(self.builder.get_object('flip'), "Flip the board")
        Tooltip(self.builder.get_object('white_side'), "Change to white's turn")
        Tooltip(self.builder.get_object('black_side'), "Change to black's turn")
        Tooltip(self.builder.get_object('stat_type'), "'cp': centipawn (already convert), \
'mate': checkmate in")
        Tooltip(self.builder.get_object('stat_value'), "Positive for white, negative for black")
        Tooltip(self.builder.get_object('analyse'), "Analyse the chessboard")
        Tooltip(self.builder.get_object('elo'), "The elo rating")
        Tooltip(self.builder.get_object('halfmove'), "Halfmove clock: The number of halfmoves \
since the last capture\nor pawn advance, used for the fifty-move rule")
        Tooltip(self.builder.get_object('fullmove'), "Fullmove number: The number of the \
full moves. It starts at 1 and\nis incremented after Black's move")
        Tooltip(self.builder.get_object('top1'), "Get the first best move (from here to there)")
        Tooltip(self.builder.get_object('top2'), "Get the second best move (from here to there)")
        Tooltip(self.builder.get_object('deselect'), "Remove a piece from chessboard")
        Tooltip(self.builder.get_object('undo'), "Undo the move on the chessboard")
        Tooltip(self.builder.get_object('redo'), "Redo the move on the chessboard")

    def update_image(
        self,
        widget_id: str,
        parent_id: str,
        x: int,
        y: int,
        img_name: str = "empty.png",
        path: str = PROJECT_PATH / "UI_Assets",
    ) -> None:
        """Update the image using object's id. Used for moving pieces."""
        panel = self.builder.get_object(parent_id)
        aux = Image.open(path / img_name)

        # avoid to be deleted. Image will be saved at self.widget_id
        setattr(self, widget_id, ImageTk.PhotoImage(aux))
        panel.create_image(x, y, image=getattr(self, widget_id), anchor="nw")

    def update_chessboard(self) -> None:
        """Update the chessboard though self.fen"""
        self.board: tuple[tuple[str]] = self.fen_to_board(self.fen)

        # Use some 2D array methods for the value inside.
        for loc_y, small_board in enumerate(self.board):
            for loc_x, value in enumerate(small_board):
                # update chess piece in that exact location
                loc_id: str = f"loc{loc_y}_{loc_x}"
                x: int = 1+32*loc_x
                y: int = 1+32*loc_y
                self.update_image(loc_id, 'chessboard', x, y, FEN_DICT[value])

    def fen_to_board(
        self,
        fen: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    ) -> list[list[str]]:
        """Turn fen to board."""
        board: list[list[str]] = []
        chunk: tuple[str] = fen.split(" ")[0].split("/")

        for small_chunk in chunk:

            new_chunk: list = []
            # modified the chunk so that number will turn to 'e'
            if self.black_side:
                small_chunk = small_chunk[::-1]

            for value in small_chunk:
                try:
                    int_value: int = int(value)
                    for _ in range(int_value):
                        new_chunk.append('e')
                except ValueError:
                    new_chunk.append(value)

            board.append(new_chunk)

        if self.black_side:
            return board[::-1]
        return board

    def board_to_fen(self, board: tuple[tuple[str]]|None = None):
        """
        Turn board to fen. IMPORTANT: convert 'Halfmove clock' and 'Fullmove number' to 0 and 1.
        """
        if board is None: # better visual
            board = [['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
                     ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
                     ['e', 'e', 'e', 'e', 'e', 'e', 'e', 'e'],
                     ['e', 'e', 'e', 'e', 'e', 'e', 'e', 'e'],
                     ['e', 'e', 'e', 'e', 'e', 'e', 'e', 'e'],
                     ['e', 'e', 'e', 'e', 'e', 'e', 'e', 'e'],
                     ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
                     ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']]

        fen_front: str = ''
        fen_sliced: str = self.fen.split(" ", 4)

        for index, small_board in enumerate(board):
            if self.is_black:
                small_board = small_board[::-1]

            count: int = 0
            for small_index, value in enumerate(small_board):
                if value == 'e':
                    count += 1
                    if small_index == 7:
                        fen_front += str(count)
                    continue

                if count != 0:
                    fen_front += str(count)
                fen_front += value
                count = 0

            if index != 7:
                fen_front += '/'

        if self.is_black:
            fen_sliced[0] = fen_front[::-1]
        fen_sliced[0] = fen_front
        fen_sliced[4] = '0 1'
        return ' '.join(fen_sliced)

    def update_stats(self) -> None:
        """Update stat to app."""
        stat  = self.engine.get_stats()
        self.builder.get_object('stat_type').config(text=stat['type'])
        final: str = str(stat['value'])
        if stat['type'] == 'cp':
            final = str(stat['value']/100)
        if float(final) >= 0:
            final = '+' + final
        self.builder.get_object('stat_value').config(text=final)

    def update_moves(self) -> None:
        """Update 'Halfmove clock' and 'Fullmove number'"""
        engine_halfmove = self.builder.get_variable('engine_halfmove').get()
        engine_fullmove = self.builder.get_variable('engine_fullmove').get()

        self.fen = f'{self.fen[:-4]} {engine_halfmove} {engine_fullmove}'

    def show_moves(self) -> None:
        """Actually show them on chessboard."""
        for loc_y, small_board in enumerate(self.move_board):
            for loc_x, value in enumerate(small_board):
                # update chess piece in that exact location
                move_id: str = f"move{loc_y}_{loc_x}"
                x: int = 1+32*loc_x
                y: int = 1+32*loc_y
                self.update_image(move_id, 'chessboard', x, y, MOVE_DICT[value])

    def move_piece(self, last_x: int, last_y: int, x: int, y: int) -> None:
        """Move piece on the app."""
        if self.move_board[y][x] == ' ' or self.move_board[y][x] == 'x':
            self.reset_moves()
            self.show_moves()
            self.move_ready = False
            return

        if self.black_side:
            last_move: str = f'{ALPHABET_DICT[str(7 - last_x)]}{last_y + 1}'
            move: str = f'{ALPHABET_DICT[str(7 - x)]}{y + 1}'
        else:
            last_move: str = f'{ALPHABET_DICT[str(last_x)]}{8 - last_y}'
            move: str = f'{ALPHABET_DICT[str(x)]}{8 - y}'

        # for pawn promotion
        if self.board[last_y][last_x].lower() == 'p'\
            and ((self.forward and y == 0) or (not self.forward and y == 7)):

            self.advance_dialog.show()
            self.mainwindow.wait_variable(self.advance_key)

            if self.advance_key.get() == '':
                return

            move += self.advance_key.get()[0]
            self.advance_key = tk.StringVar(self.mainwindow)

        self.reset_moves()
        self.show_moves()
        self.move_ready = False
        self.engine.move([last_move + move])

        self.fen = self.engine.get_fen()
        self.move_last = ''

        sliced_fen: tuple[str] = self.fen.split(' ')

        if sliced_fen[1] == 'w':
            self.builder.get_object('white_side').config(background='#888888')
            self.builder.get_object('black_side').config(background='')
            self.is_black = False
        if sliced_fen[1] == 'b':
            self.builder.get_object('white_side').config(background='')
            self.builder.get_object('black_side').config(background='#888888')
            self.is_black = True

        for p in ('K', 'Q', 'k', 'q'):
            self.builder.get_object(f'castle_{FEN_DICT[p][:-4]}').deselect()

        for p in sliced_fen[2]:
            if p == '-':
                break
            self.builder.get_object(f'castle_{FEN_DICT[p][:-4]}').select()

        self.builder.tkvariables['engine_halfmove'].set(sliced_fen[4])
        self.builder.tkvariables['engine_fullmove'].set(sliced_fen[5])

        self.update_chessboard()
        if self.engine.data['ChessAI']['Analyse Every Move']:
            self.fen_analyse(object)

        if self.move is not None:
            self.builder.get_object('chessboard').delete(self.move)
            self.move = None
        self.builder.get_object('top1').config(relief='flat', background='')
        self.builder.get_object('top2').config(relief='flat', background='')

    def on_closing(self):
        """Close the app."""
        if os.path.isfile(PROJECT_PATH / 'history.json'):
            os.remove(PROJECT_PATH / 'history.json')
        self.mainwindow.destroy()
        print('')
