"""The GUI of ChessAI, using pygubu."""

import os
import json

import tkinter as tk
from tkinter import ttk
import pygubu
from PIL import Image, ImageTk

from .sub_gui.gui_base import PROJECT_PATH, ALPHABET_DICT, FEN_DICT
from .sub_gui.gui_setting import ChessAISetting

from .engine import Engine

PROJECT_UI: str = os.path.join(PROJECT_PATH, 'sub_gui', 'ChessAI.ui')

NUMBER_DICT: dict = {k: v for v, k in ALPHABET_DICT.items()}
BOARD_DICT: dict = {k[:-4]: v for v, k in FEN_DICT.items()}

class ChessAIApp(ChessAISetting): # inherit
    """
    An app that using pygubu.
    
    Just go `.run()` and you got everything.
    """
    def __init__(self, data: dict, master=None):
        super().__init__()
        self.pieces_selected: str = "empty"

        self.engine = Engine(data=data)

        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(PROJECT_PATH)

        builder.add_from_file(PROJECT_UI)

        self.mainwindow = builder.get_object('title', master)
        self.mainwindow.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.advance_dialog = builder.get_object('advance', self.mainwindow)
        self.cropping_dialog = builder.get_object('cropping', self.mainwindow)
        self.warning_dialog = builder.get_object('warning', self.mainwindow)
        self.delete_dialog = builder.get_object('delete', self.mainwindow)
        self.template_dialog = builder.get_object('template', self.mainwindow)
        self.info_dialog = builder.get_object('info', self.mainwindow)
        builder.connect_callbacks(self)

        self.mainwindow.wm_attributes('-topmost', True)
        self.advance_dialog.toplevel.wm_attributes('-topmost', True)
        self.cropping_dialog.toplevel.wm_attributes('-topmost', True)
        self.delete_dialog.toplevel.wm_attributes('-topmost', True)
        self.template_dialog.toplevel.wm_attributes('-topmost', True)
        self.info_dialog.toplevel.wm_attributes('-topmost', True)
        self.builder.get_object('warning', self.mainwindow).toplevel.wm_attributes('-topmost', True)
        self.theme = ttk.Style()
        self.theme.theme_use('default')

        self.prepare_chessboard()
        self.prepare_hover()

        self.engine.set_elo(self.engine.data['ChessAI']['Elo'])
        self.builder.tkvariables['engine_elo'].set(self.engine.data['ChessAI']['Elo'])

        self.vision__init__()
        self.setting__init__()

    def run(self) -> None:
        """Run the app."""
        self.mainwindow.mainloop()

    def set_fen(self) -> None:
        """Set the fen."""
        self.engine.restart_engine()
        self.engine.engine.set_fen_position(self.fen)

    def warning(self, message: str) -> None:
        """Show warning."""
        self.builder.get_object('warning_message').config(text=message)
        self.warning_dialog.show()

    # select purpose
    def select_pieces(self, event: object) -> None:
        """Select piece on the left side panel."""
        widget = event.widget

        # if user presses twice, deselect it
        if self.pieces_selected == widget._name:
            self.pieces_selected = 'empty'
            widget.config(relief='flat', background='')
            self.update_image('select', 'chessboard', 0, 0)
            return

        # deselect the last selected piece
        if self.pieces_selected != 'empty':
            self.builder.get_object(self.pieces_selected).config(relief='flat', background='')

        # let the selected pieces globally
        self.pieces_selected = widget._name

        # display purpose
        widget.config(relief='sunken', background='#888888')

    # things going on chessboard
    def chessboard_hover(self, event: object) -> None:
        """Create hover effect on chessboard. (selected piece go with mouse)"""
        if self.pieces_selected == 'empty':
            return
        self.update_image('select', 'chessboard', \
            event.x - 16, event.y - 16, self.pieces_selected + '.png')

    def chessboard_unhover(self, _: object) -> None:
        """Remove hover effect."""
        if self.pieces_selected == 'empty':
            return
        self.update_image('select', 'chessboard', 0, 0)

    def chessboard_press(self, event: object) -> None:
        """When user press on chessboard."""
        #FIXME - I tried to made use able to drag but <Motion> and <B1-Motion> not working together.

        loc_x: int = int((event.x - 1) / 32)
        loc_y: int = int((event.y - 1) / 32)
        # update chessboard
        loc_id: str = f"loc{loc_y}_{loc_x}"
        x: int = 1+32*loc_x
        y: int = 1+32*loc_y

        if self.pieces_selected != 'empty':
            if self.pieces_selected == 'deselect':
                if self.board[loc_y][loc_x] == 'K':
                    self.white_king_exist -= 1

                if self.board[loc_y][loc_x] == 'k':
                    self.black_king_exist -= 1

                self.update_image(loc_id, 'chessboard', x, y)
                self.board[loc_y][loc_x] = 'e'

            else:
                if self.pieces_selected == 'white_king':
                    self.white_king_exist += 1

                if self.pieces_selected == 'black_king':
                    self.black_king_exist += 1

                self.update_image(loc_id, 'chessboard', x, y, self.pieces_selected + '.png')
                self.board[loc_y][loc_x] = BOARD_DICT[self.pieces_selected]

            self.fen = self.board_to_fen(self.board)
            if self.white_king_exist == 1 and self.black_king_exist == 1:
                self.set_fen()

            self.reset_moves()
            self.show_moves()
            return

        if self.white_king_exist != 1 or self.black_king_exist != 1:
            self.warning(f'There must be 1 king each side. (There are \
{self.white_king_exist} white king(s) and {self.black_king_exist} black king(s))')
            return

        # playable chessboard
        if not self.move_ready\
             or (self.board[loc_y][loc_x] != 'e' and self.move_board[loc_y][loc_x] == ' '):

            self.set_moves(loc_x, loc_y)
            self.show_moves()
        else:
            self.move_piece(self.move_last[0], self.move_last[1], loc_x, loc_y)

    # up and release effect:
    def object_click(self, event: object) -> None:
        """When got clicked"""
        event.widget.config(background='#888888')

    def object_unclick(self, event: object) -> None:
        """When got unclicked"""
        event.widget.config(background='#d9d9d9')

    # fen config
    def fen_castle(self, event: object) -> None:
        """Edit the castle info in fen."""
        name = event.widget._name

        # get the current one
        castle: str = ''
        for p in ('K', 'Q', 'k', 'q'):
            if (getattr(self, f'var_{p}').get() and BOARD_DICT[name[7:]] != p)\
                 or(not getattr(self, f'var_{p}').get() and BOARD_DICT[name[7:]] == p):
                castle += p

        # new fen
        sliced_fen: tuple[str] = self.fen.split(" ", 3)
        sliced_fen[2] = castle
        self.fen = ' '.join(sliced_fen)

    def fen_flip(self, _: object) -> None:
        """Edit the flip the side in the app."""
        chessboard: str = ''

        if self.black_side:
            self.black_side = False
            chessboard = "white_chessboard.png"
        else:
            self.black_side = True
            chessboard = "black_chessboard.png"

        panel = self.builder.get_object('chessboard')

        # chessboard image setup
        img = Image.open(PROJECT_PATH / "UI_Assets" / chessboard)
        # avoid to be deleted
        self.chessboard = ImageTk.PhotoImage(img)
        panel.create_image(0, 0, image=self.chessboard, anchor="nw")

        self.update_chessboard()

    def fen_white_side(self, event: object) -> None:
        """Edit the change side to white in fen."""
        if not self.is_black:
            return

        event.widget.config(background='#888888')
        self.builder.get_object('black_side').config(background='')
        self.is_black = False

        sliced_fen: tuple[str] = self.fen.split(" ", 2)
        sliced_fen[1] = 'w'
        self.fen = ' '.join(sliced_fen)
        self.set_fen()

    def fen_black_side(self, event: object) -> None:
        """Edit the change side to black in fen."""
        if self.is_black:
            return

        event.widget.config(background='#888888')
        self.builder.get_object('white_side').config(background='')
        self.is_black = True

        sliced_fen: tuple[str] = self.fen.split(" ", 2)
        sliced_fen[1] = 'b'
        self.fen = ' '.join(sliced_fen)
        self.set_fen()

    def fen_analyse(self, _: object) -> None:
        """Analyse and give top moves."""
        if self.white_king_exist != 1 or self.black_king_exist != 1:
            self.warning(f'There must be 1 king each side. (There are \
{self.white_king_exist} white king(s) and {self.black_king_exist} black king(s))')
            return

        self.set_fen()
        self.update_stats()
        self.update_moves()

        engine_top = self.engine.get_top_moves()
        engine_top1 = engine_top[0]
        try:
            engine_top2 = engine_top[1]
        except IndexError:
            engine_top2 = ''

        self.builder.tkvariables['var_top1'].set(engine_top1)
        self.builder.tkvariables['var_top2'].set(engine_top2)

        engine_elo = int(self.builder.get_variable('engine_elo').get())
        self.engine.set_elo(engine_elo)

        if self.move is not None:
            self.builder.get_object('chessboard').delete(self.move)
            self.move = None
        self.builder.get_object('top1').config(relief='flat', background='')
        self.builder.get_object('top2').config(relief='flat', background='')

    def fen_top1(self, event: object) -> None:
        """Edit the top 1 in the app."""
        widget = event.widget

        widget.config(relief='flat', background='')
        self.builder.get_object('top2').config(relief='flat', background='')

        if self.move is not None:
            self.builder.get_object('chessboard').delete(self.move)
            self.move = None

        text = self.builder.tkvariables['var_top1'].get()
        if text == '':
            return

        widget.config(relief='sunken', background='#888888')

        if self.black_side:
            last_x: int = 32 * (7.5 - int(NUMBER_DICT[text[0]]))
            last_y: int = 32 * (int(text[1]) - 0.5)
            x: int = 32 * (7.5 - int(NUMBER_DICT[text[2]]))
            y: int = 32 * (int(text[3]) - 0.5)
        else:
            last_x: int = 32 * (int(NUMBER_DICT[text[0]]) + 0.5)
            last_y: int = 32 * (8.5 - int(text[1]))
            x: int = 32 * (int(NUMBER_DICT[text[2]]) + 0.5)
            y: int = 32 * (8.5 - int(text[3]))

        self.move = self.builder.get_object('chessboard')\
            .create_line(last_x, last_y, x, y, arrow=tk.LAST)

    def fen_top2(self, event: object) -> None:
        """Edit the top 2 in the app."""
        widget = event.widget

        widget.config(relief='flat', background='')
        self.builder.get_object('top1').config(relief='flat', background='')

        if self.move is not None:
            self.builder.get_object('chessboard').delete(self.move)
            self.move = None

        text = self.builder.tkvariables['var_top2'].get()
        if text == '':
            return

        widget.config(relief='sunken', background='#888888')

        if self.black_side:
            last_x: int = 32 * (7.5 - int(NUMBER_DICT[text[0]]))
            last_y: int = 32 * (int(text[1]) - 0.5)
            x: int = 32 * (7.5 - int(NUMBER_DICT[text[2]]))
            y: int = 32 * (int(text[3]) - 0.5)
        else:
            last_x: int = 32 * (int(NUMBER_DICT[text[0]]) + 0.5)
            last_y: int = 32 * (8.5 - int(text[1]))
            x: int = 32 * (int(NUMBER_DICT[text[2]]) + 0.5)
            y: int = 32 * (8.5 - int(text[3]))

        self.move = self.builder.get_object('chessboard')\
            .create_line(last_x, last_y, x, y, arrow=tk.LAST)

    # when the pawn reach the end
    def advance_submit(self) -> None:
        """Submit which piece the advanced pawn become."""
        self.advance_key.set(self.builder.get_variable('advance_key').get())
        if self.advance_key == '':
            return
        self.builder.get_object('advance', self.mainwindow).close()

    # Undo and redo with history
    def board_undo(self, _: object):
        """Undo chessboard."""
        with open(PROJECT_PATH / 'history.json', mode="r", encoding="utf-8") as read_file:
            data: dict = json.load(read_file)
            read_file.close()

        self.engine.current_move -= 1

        if self.engine.current_move == -1:
            self.engine.current_move = 0
            return

        if self.engine.current_move == len(data) - 1:
            self.engine.current_move = len(data)
            return

        self.fen = data[str(self.engine.current_move)]['fen']
        self.set_fen()
        self.update_chessboard()

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

    def board_redo(self, _: object):
        """Redo chessboard."""
        with open(PROJECT_PATH / 'history.json', mode="r", encoding="utf-8") as read_file:
            data: dict = json.load(read_file)
            read_file.close()

        self.engine.current_move += 1

        if self.engine.current_move == -1:
            self.engine.current_move = 0
            return

        if self.engine.current_move == len(data):
            self.engine.current_move = len(data) - 1
            return

        self.fen = data[str(self.engine.current_move)]['fen']
        self.set_fen()
        self.update_chessboard()

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

if __name__ == '__main__':
    pass
