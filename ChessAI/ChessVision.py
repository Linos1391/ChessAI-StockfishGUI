import pathlib
import sys
import os
import shutil
import tkinter as tk
import tkinter.ttk as ttk
import pygubu
from PIL import Image, ImageTk
import json
from idlelib.tooltip import Hovertip
from ChessEngine import Engine
import ChessVision

# For safety... don't read it. It just randomly works.

PROJECT_PATH: str = pathlib.Path(__file__).parent
PROJECT_UI: str = PROJECT_PATH / "ChessGUI.ui"

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

BOARD_DICT: dict = {k[:-4]: v for v, k in FEN_DICT.items()}

MOVE_DICT: dict = {
    "x": "empty.png",
    " ": "empty.png",
    ".": "move.png",
    "o": "kill.png",
}

ALPHABET_DICT: dict = {
    "0": "a",
    "1": "b",
    "2": "c",
    "3": "d",
    "4": "e",
    "5": "f",
    "6": "g",
    "7": "h",
}

NUMBER_DICT: dict = {k: v for v, k in ALPHABET_DICT.items()}

# Shoutout to idlelib.tooltip
class Tooltip(Hovertip):
    def __init__(self, anchor_widget, text):
        super().__init__(anchor_widget, text, hover_delay=10)
        
    def showtip(self):
        """display the tooltip"""
        if self.tipwindow:
            return
        self.tipwindow = tw = tk.Toplevel(self.anchor_widget)
        # show no border on the top level window
        tw.wm_overrideredirect(1)
        # make it on top
        tw.wm_attributes("-topmost", True)
        try:
            # This command is only needed and available on Tk >= 8.4.0 for OSX.
            # Without it, call tips intrude on the typing process by grabbing
            # the focus.
            tw.tk.call("::tk::unsupported::MacWindowStyle", "style", tw._w,
                       "help", "noActivates")
        except tk.TclError:
            pass

        self.position_window()
        self.showcontents()
        self.tipwindow.update_idletasks()  # Needed on MacOS -- see #34275.
        self.tipwindow.lift()  # work around bug in Tk 8.5.18+ (issue #24570)

class ChessGUIApp:
    FEN: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1" # default FEN
    is_black: bool = False # white side by default
    black_side: bool = False
    pieces_selected: str = "empty"
    
    white_king_exist: int = 1
    black_king_exist: int = 1
    
    board: list[list[str]] = []
    move_board: list[list[str]] = []
    move_ready: bool = False
    move_last: list[int] = []
    
    move = None
    forward = True
    
    def __init__(self, data: dict, master=None):
        self.engine = Engine(data=data)
        
        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(PROJECT_PATH)

        builder.add_from_file(PROJECT_UI)

        self.mainwindow = builder.get_object('title', master)
        self.mainwindow.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.advance_dialog = self.builder.get_object('advance', self.mainwindow)
        self.cropping_dialog = self.builder.get_object('cropping', self.mainwindow)
        self.warning_dialog = self.builder.get_object('warning', self.mainwindow)
        self.delete_dialog = self.builder.get_object('delete', self.mainwindow)
        self.template_dialog = self.builder.get_object('template', self.mainwindow)
        self.info_dialog = self.builder.get_object('info', self.mainwindow)
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
        
        self.advance_key = tk.StringVar(self.mainwindow)
        
        self.vision__init__()
        self.setting__init__()
        
    def run(self) -> None:
        self.mainwindow.mainloop()
        
    def set_FEN(self) -> None:
        self.engine.restart_engine()    
        self.engine.engine.set_fen_position(self.FEN)
        
    def warning(self, message: str) -> None:
        """
        Show warning
        """
        
        self.builder.get_object('warning_message').config(text=message)
        self.warning_dialog.show()
        
    # +------------------------------------------------+
    # | some sub-function                              |
    # +------------------------------------------------+
                
    def prepare_chessboard(self) -> None:
        """
        Yeah... Just dont want __init__ too complicated.
        """
        
        panel = self.builder.get_object('chessboard')
        
        # chessboard image setup
        img = Image.open(PROJECT_PATH / "GUI/white_chessboard.png") 
        # avoid to be deleted
        self.chessboard = ImageTk.PhotoImage(img)
        panel.create_image(0, 0, image=self.chessboard, anchor="nw")
        
        self.FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1" # default FEN
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
        """
        Some tooltips.
        """
             
        Tooltip(self.K, "If white can castle king side")
        Tooltip(self.Q, "If white can castle queen side")
        Tooltip(self.k, "If black can castle king side")
        Tooltip(self.q, "If black can castle queen side")
        Tooltip(self.builder.get_object('flip'), "Flip the board")
        Tooltip(self.builder.get_object('white_side'), "Change to white's turn")
        Tooltip(self.builder.get_object('black_side'), "Change to black's turn")
        Tooltip(self.builder.get_object('stat_type'), "'cp': centipawn (already convert), 'mate': checkmate in")
        Tooltip(self.builder.get_object('stat_value'), "Positive for white, negative for black")
        Tooltip(self.builder.get_object('analyse'), "Analyse the chessboard")
        Tooltip(self.builder.get_object('elo'), "The elo rating")
        Tooltip(self.builder.get_object('halfmove'), "Halfmove clock: The number of halfmoves since the last capture\nor pawn advance, used for the fifty-move rule")
        Tooltip(self.builder.get_object('fullmove'), "Fullmove number: The number of the full moves. It starts at 1 and\nis incremented after Black's move")
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
        path: str = PROJECT_PATH / "GUI",
    ) -> None:
        """
        Update the image using object's id. Used for moving pieces.
        
        """
        
        panel = self.builder.get_object(parent_id)
        fpath = path / img_name
        aux = Image.open(fpath)
        
        # avoid to be deleted. Image will be saved at self.widget_id
        setattr(self, widget_id, ImageTk.PhotoImage(aux))
        panel.create_image(x, y, image=getattr(self, widget_id), anchor="nw")

    def update_chessboard(self) -> None:
        """
        Update the chessboard though self.FEN
        """
        
        self.board: tuple[tuple[str]] = self.FEN_to_board(self.FEN)
        
        # Use some 2D array methods for the value inside.
        for locY, small_board in enumerate(self.board):
            for locX, value in enumerate(small_board):
                # update chess piece in that exact location
                loc_id: str = f"loc{locY}_{locX}"
                x: int = 1+32*locX
                y: int = 1+32*locY
                self.update_image(loc_id, 'chessboard', x, y, FEN_DICT[value])
                
    def FEN_to_board(
        self,
        FEN: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    ) -> list[list[str]]:
        """
        Turn FEN to board.
        """
        
        board: list[list[str]] = []
        chunk: tuple[str] = FEN.split(" ")[0].split("/")
        
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
                except:
                    new_chunk.append(value)
                    
            board.append(new_chunk)
                    
        if self.black_side:
            return board[::-1]
        return board

    def board_to_FEN(
        self,
        board: tuple[tuple[str]] = [['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'], 
                                    ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'], 
                                    ['e', 'e', 'e', 'e', 'e', 'e', 'e', 'e'], 
                                    ['e', 'e', 'e', 'e', 'e', 'e', 'e', 'e'], 
                                    ['e', 'e', 'e', 'e', 'e', 'e', 'e', 'e'], 
                                    ['e', 'e', 'e', 'e', 'e', 'e', 'e', 'e'], 
                                    ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'], 
                                    ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']]
    ):
        """
        Turn board to FEN. IMPORTANT: convert 'Halfmove clock' and 'Fullmove number' to 0 and 1.
        """
        
        FEN_front: str = ''
        FEN_sliced: str = self.FEN.split(" ", 4)
        
        for index, small_board in enumerate(board):
    
            if self.is_black:
                small_board = small_board[::-1]
            
            count: int = 0
            for small_index, value in enumerate(small_board):
                if value == 'e':
                    count += 1
                    if small_index == 7:
                        FEN_front += str(count)
                    continue
    
                if count != 0:
                    FEN_front += str(count)
                FEN_front += value
                count = 0
            
            if index != 7:
                FEN_front += '/'
                    
        if self.is_black:
            FEN_sliced[0] = FEN_front[::-1]
        FEN_sliced[0] = FEN_front
        FEN_sliced[4] = '0 1'
        return ' '.join(FEN_sliced)
        
    def update_stats(self) -> None:
        
        stat  = self.engine.get_stats()
        self.builder.get_object('stat_type').config(text=stat['type'])
        final: str = str(stat['value'])
        if stat['type'] == 'cp':
            final = str(stat['value']/100)
        if float(final) >= 0:
            final = '+' + final
        self.builder.get_object('stat_value').config(text=final)
        
    def update_moves(self) -> None:
        """
        Update 'Halfmove clock' and 'Fullmove number'
        """
        
        engine_halfmove = self.builder.get_variable('engine_halfmove').get()
        engine_fullmove = self.builder.get_variable('engine_fullmove').get()
        
        self.FEN = f'{self.FEN[:-4]} {engine_halfmove} {engine_fullmove}'
        
    def reset_moves(self) -> None:
        self.move_board = [
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        ]
        
    def set_moves(self, x: int, y: int) -> None:
        """
        Show the playable moves on chessboard through self.move_board.\n
        ' ': empty\n
        '.': moven\n
        'o': kill\n
        'x': current position
        """
        
        if self.move_board[y][x] == 'x':
            return
        
        # remove previous moves
        for locY in range(8):
            for locX in range(8):
                self.move_board[locY][locX] = ' '   
                
        if self.board[y][x] == 'e':
            return 
        
        if self.is_black and self.board[y][x].isupper():
            return
            
        if not self.is_black and self.board[y][x].islower():
            return
        
        self.move_ready = True
        self.move_last = [x, y]
        
        self.move_board[y][x] = 'x'
        
        # pawn move
        if self.board[y][x].lower() == 'p':
            for index_y in range(2):
                for index_x in range(3):
                    locX: int = x + index_x - 1
                    locY: int
                    if self.is_black:
                        if self.black_side:
                            locY = y + index_y - 2
                            self.forward = True
                        else:
                            locY = y - index_y + 2
                            self.forward = False
                    else:
                        if self.black_side:
                            locY = y - index_y + 2
                            self.forward = False
                        else:
                            locY = y + index_y - 2
                            self.forward = True
                                 
                    if not 0 <= locX <= 7:
                        continue
                    if not 0 <= locY <= 7:
                        continue
                    
                    if self.black_side:
                        last_move: str = f'{ALPHABET_DICT[str(7 - x)]}{y + 1}'
                        move: str = f'{ALPHABET_DICT[str(7 - locX)]}{locY + 1}'
                    else:
                        last_move: str = f'{ALPHABET_DICT[str(x)]}{8 - y}'
                        move: str = f'{ALPHABET_DICT[str(locX)]}{8 - locY}'
                    
                    if (self.forward and locY == 0) or (not self.forward and locY == 7):
                        move += 'q'

                    if not self.engine.check_move([last_move + move]):
                        continue
                                      
                    if index_y == 0 and index_x == 1:
                        self.move_board[locY][locX] = '.'
                    
                    if index_y == 1 and (index_x == 0 or index_x == 2):
                        self.move_board[locY][locX] = 'o'
                            
                    if index_y == 1 and index_x == 1:
                        self.move_board[locY][locX] = '.'
            return           

        # bishop move
        elif self.board[y][x].lower() == 'b':
            for locY in range(8):
                if locY == y:
                    continue
                
                # you know... square triangle...
                distant: int = locY - y
                
                for locX in (x - distant, x + distant):
                    if not 0 <= locX <= 7:
                        continue
                    
                    if self.black_side:
                        last_move: str = f'{ALPHABET_DICT[str(7 - x)]}{y + 1}'
                        move: str = f'{ALPHABET_DICT[str(7 - locX)]}{locY + 1}'
                    else:
                        last_move: str = f'{ALPHABET_DICT[str(x)]}{8 - y}'
                        move: str = f'{ALPHABET_DICT[str(locX)]}{8 - locY}'
                    
                    if not self.engine.check_move([last_move + move]):
                        continue
                    
                    if self.board[locY][locX] == 'e':
                        self.move_board[locY][locX] = '.'
                        continue
                    self.move_board[locY][locX] = 'o'
            return
                                
        # knight move
        elif self.board[y][x].lower() == 'n':
            for index_x, index_y in ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)):
                locX = index_x + x
                locY = index_y + y
                
                if not 0 <= locX <= 7 or not 0 <= locY <= 7:
                    continue
                
                if self.black_side:
                    last_move: str = f'{ALPHABET_DICT[str(7 - x)]}{y + 1}'
                    move: str = f'{ALPHABET_DICT[str(7 - locX)]}{locY + 1}'
                else:
                    last_move: str = f'{ALPHABET_DICT[str(x)]}{8 - y}'
                    move: str = f'{ALPHABET_DICT[str(locX)]}{8 - locY}'
                
                if not self.engine.check_move([last_move + move]):
                    continue
                
                if self.board[locY][locX] == 'e':
                    self.move_board[locY][locX] = '.'
                    continue
                self.move_board[locY][locX] = 'o'
            return
            
        # rook move
        elif self.board[y][x].lower() == 'r':
            for locX in range(8):
                if self.black_side:
                    last_move: str = f'{ALPHABET_DICT[str(7 - x)]}{y + 1}'
                    move: str = f'{ALPHABET_DICT[str(7 - locX)]}{y + 1}'
                else:
                    last_move: str = f'{ALPHABET_DICT[str(x)]}{8 - y}'
                    move: str = f'{ALPHABET_DICT[str(locX)]}{8 - y}'
                
                if not self.engine.check_move([last_move + move]):
                    continue
                
                if self.board[y][locX] == 'e':
                    self.move_board[y][locX] = '.'
                    continue
                self.move_board[y][locX] = 'o'
                
            for locY in range(8):
                if self.black_side:
                    last_move: str = f'{ALPHABET_DICT[str(7 - x)]}{y + 1}'
                    move: str = f'{ALPHABET_DICT[str(7 - x)]}{locY + 1}'
                else:
                    last_move: str = f'{ALPHABET_DICT[str(x)]}{8 - y}'
                    move: str = f'{ALPHABET_DICT[str(x)]}{8 - locY}'
                
                if not self.engine.check_move([last_move + move]):
                    continue
                
                if self.board[locY][x] == 'e':
                    self.move_board[locY][x] = '.'
                    continue
                self.move_board[locY][x] = 'o'
            return
                
        # queen move
        elif self.board[y][x].lower() == 'q':
            for locY in range(8):
                if locY == y:
                    continue
                
                # you know... square triangle...
                distant: int = locY - y
                
                for locX in (x - distant, x + distant):
                    if not 0 <= locX <= 7:
                        continue
                    
                    if self.black_side:
                        last_move: str = f'{ALPHABET_DICT[str(7 - x)]}{y + 1}'
                        move: str = f'{ALPHABET_DICT[str(7 - locX)]}{locY + 1}'
                    else:
                        last_move: str = f'{ALPHABET_DICT[str(x)]}{8 - y}'
                        move: str = f'{ALPHABET_DICT[str(locX)]}{8 - locY}'
                    
                    if not self.engine.check_move([last_move + move]):
                        continue
                    
                    if self.board[locY][locX] == 'e':
                        self.move_board[locY][locX] = '.'
                        continue
                    self.move_board[locY][locX] = 'o'
                    
            for locX in range(8):
                if self.black_side:
                    last_move: str = f'{ALPHABET_DICT[str(7 - x)]}{y + 1}'
                    move: str = f'{ALPHABET_DICT[str(7 - locX)]}{y + 1}'
                else:
                    last_move: str = f'{ALPHABET_DICT[str(x)]}{8 - y}'
                    move: str = f'{ALPHABET_DICT[str(locX)]}{8 - y}'
                
                if not self.engine.check_move([last_move + move]):
                    continue
                
                if self.board[y][locX] == 'e':
                    self.move_board[y][locX] = '.'
                    continue
                self.move_board[y][locX] = 'o'
                
            for locY in range(8):
                if self.black_side:
                    last_move: str = f'{ALPHABET_DICT[str(7 - x)]}{y + 1}'
                    move: str = f'{ALPHABET_DICT[str(7 - x)]}{locY + 1}'
                else:
                    last_move: str = f'{ALPHABET_DICT[str(x)]}{8 - y}'
                    move: str = f'{ALPHABET_DICT[str(x)]}{8 - locY}'
                
                if not self.engine.check_move([last_move + move]):
                    continue
                
                if self.board[locY][x] == 'e':
                    self.move_board[locY][x] = '.'
                    continue
                self.move_board[locY][x] = 'o'
            return
            
        # king move
        else:
            for index_y in range(2):
                for index_x in range(3):
                    locX: int = x + index_x - 1
                    locY: int = y + 2 * index_y - 1
                    
                    if not 0 <= locX <= 7 or not 0 <= locY <= 7:
                        continue
                    
                    # check if the king can move
                    if self.black_side:
                        last_move: str = f'{ALPHABET_DICT[str(7 - x)]}{y + 1}'
                        move: str = f'{ALPHABET_DICT[str(7 - locX)]}{locY + 1}'
                    else:
                        last_move: str = f'{ALPHABET_DICT[str(x)]}{8 - y}'
                        move: str = f'{ALPHABET_DICT[str(locX)]}{8 - locY}'
                    
                    if not self.engine.check_move([last_move + move]):
                        continue
                    
                    if self.board[locY][locX] == 'e':
                        self.move_board[locY][locX] = '.'
                        continue
                    
                    self.move_board[locY][locX] = 'o'

            for index_x in range(8):
                
                # check if the king can move
                if self.black_side:
                    last_move: str = f'{ALPHABET_DICT[str(7 - x)]}{y + 1}'
                    move: str = f'{ALPHABET_DICT[str(7 - index_x)]}{y + 1}'
                else:
                    last_move: str = f'{ALPHABET_DICT[str(x)]}{8 - y}'
                    move: str = f'{ALPHABET_DICT[str(index_x)]}{8 - y}'
                
                if not self.engine.check_move([last_move + move]):
                    continue
                
                if self.board[y][index_x] == 'e':
                    self.move_board[y][index_x] = '.'
                    continue
                    
                self.move_board[y][index_x] = 'o'
            return
                                    
    def show_moves(self) -> None:  
        """
        Actually show them on chessboard.
        """
        for locY, small_board in enumerate(self.move_board):
            for locX, value in enumerate(small_board):
                # update chess piece in that exact location
                move_id: str = f"move{locY}_{locX}"
                x: int = 1+32*locX
                y: int = 1+32*locY
                self.update_image(move_id, 'chessboard', x, y, MOVE_DICT[value])
        
    def move_piece(self, last_x: int, last_y: int, x: int, y: int) -> None:
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
        if self.board[last_y][last_x].lower() == 'p' and ((self.forward and y == 0) or (not self.forward and y == 7)):
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
        
        self.FEN = self.engine.get_FEN()
        self.move_last = ''
        
        sliced_FEN: tuple[str] = self.FEN.split(' ')
        
        if sliced_FEN[1] == 'w':
            self.builder.get_object('white_side').config(background='#888888')
            self.builder.get_object('black_side').config(background='')
            self.is_black = False
        if sliced_FEN[1] == 'b':
            self.builder.get_object('white_side').config(background='')
            self.builder.get_object('black_side').config(background='#888888')
            self.is_black = True
            
        for p in ('K', 'Q', 'k', 'q'):
            self.builder.get_object(f'castle_{FEN_DICT[p][:-4]}').deselect()
            
        for p in sliced_FEN[2]:
            if p == '-':
                break
            self.builder.get_object(f'castle_{FEN_DICT[p][:-4]}').select()
        
        self.builder.tkvariables['engine_halfmove'].set(sliced_FEN[4])
        self.builder.tkvariables['engine_fullmove'].set(sliced_FEN[5])
        
        self.update_chessboard()
        if self.engine.data['ChessAI']['Analyse Every Move']:
            self.FEN_analyse(object)
            
        if self.move is not None:
            self.builder.get_object('chessboard').delete(self.move)
            self.move = None
        self.builder.get_object('top1').config(relief='flat', background='')
        self.builder.get_object('top2').config(relief='flat', background='')

    def on_closing(self):
        if os.path.isfile(PROJECT_PATH / 'history.json'):
            os.remove(PROJECT_PATH / 'history.json')
        self.mainwindow.destroy()
    
    # +------------------------------------------------+
    # | event handler                                  |
    # +------------------------------------------------+
    
    # select purpose
    def select_pieces(self, event: object) -> None:
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
        if self.pieces_selected == 'empty':
            return
        
        self.update_image('select', 'chessboard', event.x - 16, event.y - 16, self.pieces_selected + '.png')
        
    def chessboard_unhover(self, event: object) -> None:
        if self.pieces_selected == 'empty':
            return
        
        self.update_image('select', 'chessboard', 0, 0)
        
    def chessboard_press(self, event: object) -> None:
        #TODO: I tried to made use able to drag but <Motion> and <B1-Motion> not working together. 
        
        locX: int = int((event.x - 1) / 32)
        locY: int = int((event.y - 1) / 32)
        # update chessboard
        loc_id: str = f"loc{locY}_{locX}"
        x: int = 1+32*locX
        y: int = 1+32*locY
        
        if self.pieces_selected != 'empty':    
            if self.pieces_selected == 'deselect':
                if self.board[locY][locX] == 'K':
                    self.white_king_exist -= 1
                    
                if self.board[locY][locX] == 'k':
                    self.black_king_exist -= 1
                
                self.update_image(loc_id, 'chessboard', x, y)
                self.board[locY][locX] = 'e' 

            else:
                if self.pieces_selected == 'white_king':
                    self.white_king_exist += 1
                    
                if self.pieces_selected == 'black_king':
                    self.black_king_exist += 1
                
                self.update_image(loc_id, 'chessboard', x, y, self.pieces_selected + '.png')
                self.board[locY][locX] = BOARD_DICT[self.pieces_selected] 

            self.FEN = self.board_to_FEN(self.board)
            if self.white_king_exist == 1 and self.black_king_exist == 1:
                self.set_FEN()
            
            self.reset_moves()
            self.show_moves()
            return
        
        if self.white_king_exist != 1 or self.black_king_exist != 1:
            self.warning('There must be 1 king each side.')
            return
        
        # playable chessboard
        if not self.move_ready or (self.board[locY][locX] != 'e' and self.move_board[locY][locX] == ' '):
            self.set_moves(locX, locY)
            self.show_moves()
        else:
            self.move_piece(self.move_last[0], self.move_last[1], locX, locY)

    # up and release effect:
    def object_click(self, event: object) -> None:
        event.widget.config(background='#888888')

    def object_unclick(self, event: object) -> None:
        event.widget.config(background='#d9d9d9')

    # FEN config
    def FEN_castle(self, event: object) -> None:
        name = event.widget._name
        
        # get the current one
        castle: str = ''
        for p in ('K', 'Q', 'k', 'q'):
            if (getattr(self, f'var_{p}').get() and BOARD_DICT[name[7:]] != p) or (not getattr(self, f'var_{p}').get() and BOARD_DICT[name[7:]] == p):
                castle += p
                
        # new FEN
        sliced_FEN: tuple[str] = self.FEN.split(" ", 3)
        sliced_FEN[2] = castle
        self.FEN = ' '.join(sliced_FEN)
    
    def FEN_flip(self, event: object) -> None:
        chessboard: str = ''
        
        if self.black_side:
            self.black_side = False
            chessboard = "white_chessboard.png"
        else:
            self.black_side = True
            chessboard = "black_chessboard.png"     
            
        panel = self.builder.get_object('chessboard')
        
        # chessboard image setup
        img = Image.open(PROJECT_PATH / "GUI" / chessboard) 
        # avoid to be deleted
        self.chessboard = ImageTk.PhotoImage(img)
        panel.create_image(0, 0, image=self.chessboard, anchor="nw")
    
        self.update_chessboard()
        
    def FEN_white_side(self, event: object) -> None:
        if not self.is_black:
            return
        
        event.widget.config(background='#888888')
        self.builder.get_object('black_side').config(background='')
        self.is_black = False
        
        sliced_FEN: tuple[str] = self.FEN.split(" ", 2)
        sliced_FEN[1] = 'w'
        self.FEN = ' '.join(sliced_FEN)
        self.set_FEN()
        
    def FEN_black_side(self, event: object) -> None:
        if self.is_black:
            return
        
        event.widget.config(background='#888888')
        self.builder.get_object('white_side').config(background='')
        self.is_black = True
        
        sliced_FEN: tuple[str] = self.FEN.split(" ", 2)
        sliced_FEN[1] = 'b'
        self.FEN = ' '.join(sliced_FEN)
        self.set_FEN()
        
    def FEN_analyse(self, event: object) -> None:

        if self.white_king_exist != 1 or self.black_king_exist != 1:
            self.warning('There must be 1 king each side.')
            return
        
        self.set_FEN()
        self.update_stats()
        self.update_moves()
        
        engine_top = self.engine.get_top_moves()
        engine_top1 = engine_top[0]
        try:
            engine_top2 = engine_top[1]
        except:
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
        
    def FEN_top1(self, event: object) -> None:
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
            
        self.move = self.builder.get_object('chessboard').create_line(last_x, last_y, x, y, arrow=tk.LAST)
           
    def FEN_top2(self, event: object) -> None:
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
            
        self.move = self.builder.get_object('chessboard').create_line(last_x, last_y, x, y, arrow=tk.LAST)
    
    # when the pawn reach the end
    def advance_submit(self) -> None:
        self.advance_key.set(self.builder.get_variable('advance_key').get())
        if self.advance_key == '':
            return
        self.builder.get_object('advance', self.mainwindow).close()

    # Undo and redo with history
    def board_undo(self, event: object):
        
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
            
        self.FEN = data[str(self.engine.current_move)]['fen']
        self.set_FEN()
        self.update_chessboard()
        
        sliced_FEN: tuple[str] = self.FEN.split(' ')
        
        if sliced_FEN[1] == 'w':
            self.builder.get_object('white_side').config(background='#888888')
            self.builder.get_object('black_side').config(background='')
            self.is_black = False
        if sliced_FEN[1] == 'b':
            self.builder.get_object('white_side').config(background='')
            self.builder.get_object('black_side').config(background='#888888')
            self.is_black = True
            
        for p in ('K', 'Q', 'k', 'q'):
            self.builder.get_object(f'castle_{FEN_DICT[p][:-4]}').deselect()
            
        for p in sliced_FEN[2]:
            if p == '-':
                break
            self.builder.get_object(f'castle_{FEN_DICT[p][:-4]}').select()
        
        self.builder.tkvariables['engine_halfmove'].set(sliced_FEN[4])
        self.builder.tkvariables['engine_fullmove'].set(sliced_FEN[5])
    
    def board_redo(self, event: object):    
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
            
        self.FEN = data[str(self.engine.current_move)]['fen']
        self.set_FEN()
        self.update_chessboard()
        
        sliced_FEN: tuple[str] = self.FEN.split(' ')
        
        if sliced_FEN[1] == 'w':
            self.builder.get_object('white_side').config(background='#888888')
            self.builder.get_object('black_side').config(background='')
            self.is_black = False
        if sliced_FEN[1] == 'b':
            self.builder.get_object('white_side').config(background='')
            self.builder.get_object('black_side').config(background='#888888')
            self.is_black = True
            
        for p in ('K', 'Q', 'k', 'q'):
            self.builder.get_object(f'castle_{FEN_DICT[p][:-4]}').deselect()
            
        for p in sliced_FEN[2]:
            if p == '-':
                break
            self.builder.get_object(f'castle_{FEN_DICT[p][:-4]}').select()
        
        self.builder.tkvariables['engine_halfmove'].set(sliced_FEN[4])
        self.builder.tkvariables['engine_fullmove'].set(sliced_FEN[5])

    # +------------------------------------------------+
    # | vision handler                                 |
    # +------------------------------------------------+

    def vision__init__(self):
        """
        __init__ for the Vision tab
        """
        
        self.vision_tooltip()
        
        self.vision_check_templates()
        
        self.vision_black_side: bool = False
        self.vision_crop_rect = None
        self.crop_for_analyse = None
        
    def vision_choose(self, event: object):
        template = event.widget._name[7:]
        
        if self.engine.data['ChessAI']['Current Template'] == template:
            return
        
        self.engine.data['ChessAI']['Current Template'] = template
        with open("setting.json" if getattr(sys, "frozen", False) else PROJECT_PATH / 'setting.json', mode="w", encoding="utf-8") as write_file:
            json.dump(self.engine.data, write_file, indent=4)
            write_file.close()
        
        ChessVision.TEMPLATE_PATH = ChessVision._update_template_path(template)
        
        self.vision_check_templates()
    
    def vision_add(self):
        self.template_dialog.show()
    
    def vision_add_screenshot(self):
        self.template_dialog.close()

        ChessVision._screenshot()
        self.crop_for_analyse = False
        self.vision_crop()
    
    def vision_add_choose_file(self, event: object):
        self.template_dialog.close()

        img = Image.open(event.widget.cget(key="path"))
        img.save(ChessVision.ANALYSE_PATH)
        self.crop_for_analyse = False
        self.vision_crop()
    
    def vision_delete_ask(self, event: object):
        self.delete_template = event.widget._name[7:]
        self.delete_dialog.show()
    
    def vision_delete(self):
        self.delete_dialog.close()
        
        if self.delete_template is None:
            return

        shutil.rmtree(os.path.join(PROJECT_PATH, 'Templates', self.delete_template))
        self.delete_template = None
        
        self.vision_check_templates()  
        
    def vision_info(self, event: object):
        name, date, OP, IP, pattern = ChessVision._get_info_value()
        self.builder.tkvariables['vision_name'].set(name)
        self.builder.tkvariables['vision_date'].set(date)
        self.builder.tkvariables['vision_OP_var'].set(OP)
        self.builder.tkvariables['vision_IP_var'].set(IP)
        real_pattern: str = ''
        for key, value in pattern.items():
            real_pattern += f'{key} == {value}\n'
        self.builder.tkvariables['vision_pattern_var'].set(real_pattern)
        
        self.info_dialog.show()
    
    def vision_info_update(self):
        self.info_dialog.close()
        
        print('+-----------------------------------------------------------------------------------+')
        print('| Create O.P and I.P, will take lots of time. Grab some coffee or do something else |')
        print('+-----------------------------------------------------------------------------------+')
        
        success, OP, IP, pattern = ChessVision.create_OP_and_IP()
        if not success:
            print('OP and IP are not valid, please edit the template. OP and IP will be set to -0.5 and +1, respectively')
    
        name, date, _, _, _ = ChessVision._get_info_value()
        
        info: dict = {
            "name": name,
            "date": date,
            "O.P": f'-{OP}',
            "I.P": f'+{IP}',
            "pattern": pattern,
        }

        with open(ChessVision.TEMPLATE_PATH / 'Info.json', mode="w", encoding="utf-8") as write_file:
            json.dump(info, write_file, indent=4)
            write_file.close()
        
    def vision_check_templates(self):
        # Only some are valid
        templates: tuple = ChessVision.count_templates()
        
        no_templates_left: bool = False
        if len(templates) == 0:
            no_templates_left = True
        panel = self.builder.get_object('vision_templates')
        
        # destroy previous panel
        for widget in panel.innerframe.winfo_children():
            widget.destroy()
        
        if not no_templates_left:
            
            chosen_template = templates[0]
            _current_template = self.engine.data['ChessAI']['Current Template'] 
            if _current_template != "" and _current_template in templates:
                chosen_template = _current_template
            del _current_template # Im a beginner, just a practise.
            
            for index, template in enumerate(templates):  
                frame = ttk.Frame(master=panel.innerframe, height=76, width=316, relief='raised')
                frame.pack(padx=1, pady=1)
                
                # for chessboard templates:
                chessboard = Image.open(os.path.join(PROJECT_PATH, 'Templates', template, 'Chessboard.png'))
                chessboard = chessboard.resize((70, 70))
                setattr(self, f'vision_item{index+1}_chessboard', ImageTk.PhotoImage(chessboard))
                chessboard = tk.Label(master=frame, image=getattr(self, f'vision_item{index+1}_chessboard'), background='#d9d9d9')
                chessboard.place(x=2, y=2, width=72, height=72)
                
                # for template's name:
                label = tk.Label(master=frame, text=template, background='#d9d9d9', wraplength=107)
                label.place(x=80, y=23)
                
                # for info button:
                info = Image.open(os.path.join(PROJECT_PATH, 'GUI', 'vision_info.png'))
                setattr(self, f'vision_item{index+1}_info', ImageTk.PhotoImage(info))
                info = tk.Label(master=frame, name=f'info_{template}', image=getattr(self, f'vision_item{index+1}_info'), background='#d9d9d9')
                info.bind('<ButtonPress-1>', self.vision_info)
                Tooltip(info, 'Click to see template\'s info')
                info.place(x=209, y=21, width=34, height=34)
                
                # for choose button:        
                if template == chosen_template:
                    choose_option = Image.open(os.path.join(PROJECT_PATH, 'GUI', 'vision_choose.png'))
                else:
                    choose_option = Image.open(os.path.join(PROJECT_PATH, 'GUI', 'vision_unchoose.png'))
                
                setattr(self, f'vision_item{index+1}_choose', ImageTk.PhotoImage(choose_option))
                choose_option = tk.Label(master=frame, name=f'choose_{template}', image=getattr(self, f'vision_item{index+1}_choose'), background='#d9d9d9')
                choose_option.bind('<ButtonPress-1>', self.vision_choose)
                Tooltip(choose_option, 'Click to select template')
                choose_option.place(x=245, y=21, width=34, height=34)
                
                # for delete button
                delete = Image.open(os.path.join(PROJECT_PATH, 'GUI', 'deselect.png'))
                setattr(self, f'vision_item{index+1}_delete', ImageTk.PhotoImage(delete))
                delete = tk.Label(master=frame, name=f'delete_{template}', image=getattr(self, f'vision_item{index+1}_delete'), background='#d9d9d9')
                delete.bind('<ButtonPress-1>', self.vision_delete_ask)
                Tooltip(delete, 'Click to delete template')
                delete.place(x=281, y=21, width=34, height=34)
                
        add = Image.open(os.path.join(PROJECT_PATH, 'GUI', 'vision_add.png'))
        self.vision_add_image = ImageTk.PhotoImage(add)
        add = ttk.Button(master=panel.innerframe, image=self.vision_add_image, command=self.vision_add)
        Tooltip(add, 'Click to add custom template')
        add.pack(padx=1, fill='x')

    def vision_tooltip(self):
        Tooltip(self.builder.get_object('Vision_side'), 'Change the side (User are black or white)')
        Tooltip(self.builder.get_object('vision_change_points'), 'Automatically update O.P and I.P')
        Tooltip(self.builder.get_object('vision_OP'), 'Outside points: If pieces\' template got extend outside, decrease the points (Not count the background)')
        Tooltip(self.builder.get_object('vision_IP'), 'Inside points: If pieces\' template got exactly color, increase the point')
        Tooltip(self.builder.get_object('vision_created'), 'The date template was created (dd/mm/yy)')
        Tooltip(self.builder.get_object('vision_pattern'), 'The chess pieces that have same patterns (at least O.P and I.P cannot solve them)')
    
    def vision_side(self, event: object):
        if self.vision_black_side:
            self.vision_side_image = ImageTk.PhotoImage(Image.open(os.path.join(PROJECT_PATH, 'GUI', 'vision_white.png')))
            self.vision_black_side = False
        else:
            self.vision_side_image = ImageTk.PhotoImage(Image.open(os.path.join(PROJECT_PATH, 'GUI', 'vision_black.png')))
            self.vision_black_side = True
        self.builder.get_object('Vision_side').config(image=self.vision_side_image)
    
    def vision_screenshot(self):
        ChessVision._screenshot()
        self.crop_for_analyse = True
        self.vision_crop()
    
    def vision_choose_file(self, event: object):
        img = Image.open(event.widget.cget(key="path"))
        img.save(ChessVision.ANALYSE_PATH)
        self.crop_for_analyse = True
        self.vision_crop()
        
    def vision_crop(self):
        img = Image.open(ChessVision.ANALYSE_PATH)
        self.vision_original_width, self.vision_original_height = img.size
        
        width = int(self.vision_original_width * 200 / self.vision_original_height)
        
        img = img.resize((width, 200))
        self.vision_crop_canva = ImageTk.PhotoImage(img)
        
        self.builder.tkvariables['vision_var_width'].set(self.vision_original_width)
        self.builder.tkvariables['vision_var_height'].set(self.vision_original_height)
        self.builder.get_object('vision_crop').config(width = width)
        self.builder.get_object('vision_crop').create_image(0, 0, image=self.vision_crop_canva, anchor="nw")
        self.vision_crop_image()
        self.cropping_dialog.show()
        
    def vision_crop_image(self):
        # 1 <= vision_x < self.vision_width
        vision_x: int = self.builder.tkvariables['vision_var_x']
        if vision_x.get() >= self.vision_original_width:
            x = int((self.vision_original_width-1) * 200 / self.vision_original_height)
            vision_x.set(self.vision_original_width - 1)
        elif vision_x.get() < 1:
            x = 0
            vision_x.set(1)
        else:    
            x = int(vision_x.get() * 200 / self.vision_original_height)
        
        # 1 <= vision_y < self.vision_height
        vision_y: int = self.builder.tkvariables['vision_var_y']
        if vision_y.get() >= self.vision_original_height:
            y = int((self.vision_height-1) * 200 / self.vision_original_height)
            vision_y.set(self.vision_original_height - 1)
        elif vision_y.get() < 1:
            y = 0
            vision_y.set(1)
        else:    
            y = int(vision_y.get() * 200 / self.vision_original_height)
        
        # vision_x < vision_width+vision_x <= self.vision_width
        vision_width: int = self.builder.tkvariables['vision_var_width']
        if vision_width.get() + x > self.vision_original_width:
            width = int((self.vision_original_width-vision_x.get()) * 200 / self.vision_original_height)
            vision_width.set(self.vision_original_width - vision_x.get())
        elif vision_width.get() < 1:
            width = 1
            vision_width.set(1)
        else:    
            width = int(vision_width.get() * 200 / self.vision_original_height)
        
        # vision_y < vision_height+vision_y <= self.vision_height
        vision_height: int = self.builder.tkvariables['vision_var_height']
        if vision_height.get() + y > self.vision_original_height:
            height = 200
            vision_height.set(self.vision_original_height - vision_y.get())
        elif vision_height.get() < 1:
            height = 1
            vision_height.set(1)
        else:    
            height = int(vision_height.get() * 200 / self.vision_original_height)
        
        if self.vision_crop_rect is not None:
            self.builder.get_object('vision_crop').delete(self.vision_crop_rect)
            self.vision_crop_rect = None
        
        self.vision_x: int = vision_x.get()
        self.vision_y: int = vision_y.get()
        self.vision_width: int = vision_width.get()
        self.vision_height: int = vision_height.get()
        
        self.vision_crop_rect = self.builder.get_object('vision_crop').create_rectangle(x, y, x+width-1, y+height-1, outline='red')
    
    def vision_crop_submit(self):
        self.cropping_dialog.close()
        
        img = Image.open(ChessVision.ANALYSE_PATH)
        img = img.crop((self.vision_x, self.vision_y, self.vision_x+self.vision_width, self.vision_x+self.vision_height))

        try:
            img = ChessVision.make_chessboard_template(img)
        except:
            self.warning('Please crop better or choose\nanother file / screenshot again.')
            return
        
        if self.crop_for_analyse:   
            img.save(ChessVision.ANALYSE_PATH)
            
            try:
                self.board = ChessVision.analyse_chess_pieces(img)
            except:
                self.warning('Please crop better or choose\nanother file / screenshot again.')
                return

            self.FEN = self.board_to_FEN(self.board)
            
            try:
                with open(PROJECT_PATH / 'history.json', mode="r", encoding="utf-8") as read_file:
                    existed_data: dict = json.load(read_file)
                    read_file.close()
            except:
                raise Exception('Cannot access history.json file')

            data: dict = {
                str(self.engine.current_move): {
                    "fen": self.FEN
                }
            }
            
            for id in range(self.engine.current_move, len(existed_data)):
                existed_data.pop(str(id))

            existed_data.update(data)

            with open(PROJECT_PATH / 'history.json', mode="w", encoding="utf-8") as write_file:
                json.dump(existed_data, write_file, indent=4)
                write_file.close()

            self.set_FEN()
            self.update_chessboard()

            if self.vision_black_side:
                self.builder.get_object('black_side').config(background='#888888')
                self.builder.get_object('white_side').config(background='')
                self.is_black = True

                sliced_FEN: tuple[str] = self.FEN.split(" ", 2)
                sliced_FEN[1] = 'b'
                self.FEN = ' '.join(sliced_FEN)
                self.set_FEN()
            else:
                self.builder.get_object('white_side').config(background='#888888')
                self.builder.get_object('black_side').config(background='')
                self.is_black = False

                sliced_FEN: tuple[str] = self.FEN.split(" ", 2)
                sliced_FEN[1] = 'w'
                self.FEN = ' '.join(sliced_FEN)
                self.set_FEN()
                
        else:
            name = self.builder.tkvariables['template_name'].get()

            if name == '':
                name = 'Untitled'
            try:
                os.mkdir(os.path.join(PROJECT_PATH, 'Templates', name))
            except:
                pass # maybe you created it then
            
            ChessVision.TEMPLATE_PATH = ChessVision._update_template_path(name)
            
            img.save(ChessVision.TEMPLATE_PATH / 'Chessboard.png')
            
            try:
                ChessVision.make_chesspiece_template(img, name)
            except Exception as e:
                # FIXME - find the exception
                print(e)
                self.warning('Please crop better or choose\nanother file / screenshot again.')
                return
            
            self.vision_check_templates()
        
        self.crop_for_analyse = None
        os.remove(ChessVision.ANALYSE_PATH)
         
    # +------------------------------------------------+
    # | setting handler                                |
    # +------------------------------------------------+

    def setting__init__(self):
        """
        __init__ for the Setting tab
        """
        
        self.setting_tooltip()
        
        self.setting_warning()
        
        self.builder.tkvariables['Entry_ChessAI_Analyse_Every_Move'].set(str(self.engine.data['ChessAI']['Analyse Every Move']))
        self.builder.get_object('Stockfish_Debug_Log_File').config(path=self.engine.data['Stockfish']['Debug Log File'])
        self.builder.tkvariables['Entry_Stockfish_UCI_Chess960'].set(str(self.engine.data['Stockfish']['UCI_Chess960']))
        self.builder.tkvariables['Entry_Stockfish_Min_Split_Depth'].set(self.engine.data['Stockfish']['Min Split Depth'])
        self.builder.tkvariables['Entry_Stockfish_Threads'].set(self.engine.data['Stockfish']['Threads'])
        self.builder.tkvariables['Entry_Stockfish_Hash'].set(self.engine.data['Stockfish']['Hash'])
    
    def setting_tooltip(self):
        Tooltip(self.builder.get_object('Label_ChessAI_Analyse_Every_Move'), "Automatic analyse when you move a piece (not when set up)")
        Tooltip(self.builder.get_object('Label_Stockfish_Debug_Log_File'), "Path to file that save debug log (if needed)")
        Tooltip(self.builder.get_object('Label_Stockfish_UCI_Chess960'), "Able to play Chess960")
        Tooltip(self.builder.get_object('Label_Stockfish_Min_Split_Depth'), "Minimum depth for analyse")
        Tooltip(self.builder.get_object('Label_Stockfish_Threads'), "The number of CPU threads used for searching a position. For best performance, set\nthis equal to the number of CPU cores available (min 1 max 1024)")
        Tooltip(self.builder.get_object('Label_Stockfish_Hash'), "The size of the hash table in MB. It is recommended to set Hash after\nsetting Threads. (min 1 max 33554432)")
    
    def setting_data(self, widget_id):        
        if widget_id == 'ChessAI_Analyse_Every_Move':  
            if self.builder.tkvariables['Entry_ChessAI_Analyse_Every_Move'].get() == 'True':
                self.builder.tkvariables['Entry_ChessAI_Analyse_Every_Move'].set('False')
            else:
                self.builder.tkvariables['Entry_ChessAI_Analyse_Every_Move'].set('True')
            return
        
        if widget_id == 'Stockfish_UCI_Chess960':           
            if self.builder.tkvariables['Entry_Stockfish_UCI_Chess960'].get() == 'True':
                self.builder.tkvariables['Entry_Stockfish_UCI_Chess960'].set('False')
            else:
                self.builder.tkvariables['Entry_Stockfish_UCI_Chess960'].set('True')
            return
        
    def setting_update_data(self):
        data = {
            "ChessAI": {
                "Engine": self.engine.data['ChessAI']['Engine'],
                "Analyse Every Move": True if self.builder.tkvariables['Entry_ChessAI_Analyse_Every_Move'].get() == 'True' else False,
                "Elo": self.builder.tkvariables['engine_elo'].get(),
                "Current Template": self.engine.data['ChessAI']['Current Template'],
            },             
            "Stockfish": {
                "Debug Log File": self.builder.tkvariables['Entry_Stockfish_Debug_Log_File'].get(),
                "UCI_Chess960": True if self.builder.tkvariables['Entry_Stockfish_UCI_Chess960'].get() == 'True' else False,
                "Min Split Depth": self.builder.tkvariables['Entry_Stockfish_Min_Split_Depth'].get(),
                "Threads": self.builder.tkvariables['Entry_Stockfish_Threads'].get(),
                "Hash": self.builder.tkvariables['Entry_Stockfish_Hash'].get(),
            },
        }
        
        with open("setting.json" if getattr(sys, "frozen", False) else PROJECT_PATH / 'setting.json', mode="w", encoding="utf-8") as write_file:
            json.dump(data, write_file, indent=4)
            write_file.close()
            
        self.engine.data = data
        
    def setting_warning(self) -> None:
        def check(object_name: str, correct_answer: str | int) -> None:
            try:
                answer = self.builder.tkvariables[f'Entry_{object_name}'].get()
                if answer == correct_answer:
                    setattr(self, object_name, tk.PhotoImage(file=PROJECT_PATH / 'GUI/empty.png'))
                else:
                    setattr(self, object_name, tk.PhotoImage(file=PROJECT_PATH / 'GUI/warning.png'))
            except:
                setattr(self, object_name, tk.PhotoImage(file=PROJECT_PATH / 'GUI/warning.png'))
                
            self.builder.get_object(f'Warning_{object_name}').config(image=getattr(self, object_name))
            
        check('ChessAI_Analyse_Every_Move', str(self.engine.data['ChessAI']['Analyse Every Move']))
        check('Stockfish_Debug_Log_File', self.engine.data['Stockfish']['Debug Log File'])
        check('Stockfish_UCI_Chess960', str(self.engine.data['Stockfish']['UCI_Chess960']))
        check('Stockfish_Min_Split_Depth', self.engine.data['Stockfish']['Min Split Depth'])
        check('Stockfish_Threads', self.engine.data['Stockfish']['Threads'])
        check('Stockfish_Hash', self.engine.data['Stockfish']['Hash'])
        
        self.mainwindow.after(100, self.setting_warning)

if __name__ == '__main__':
    print('Use "main.py" dude')
