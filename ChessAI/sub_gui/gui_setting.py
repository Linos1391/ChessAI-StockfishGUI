"""The setting tab for ChessAI."""

import json
import sys

import tkinter as tk

from .gui_base import PROJECT_PATH
from .gui_vision import ChessAIVision
from .tooltip import Tooltip

class ChessAISetting(ChessAIVision): #inherit
    """The setting tab for ChessAI."""
    def setting__init__(self):
        """__init__ for the Setting tab."""
        self.setting_tooltip()
        self.setting_warning()

        self.builder.tkvariables['Entry_ChessAI_Analyse_Every_Move']\
            .set(str(self.engine.data['ChessAI']['Analyse Every Move']))

        self.builder.get_object('Stockfish_Debug_Log_File')\
            .config(path=self.engine.data['Stockfish']['Debug Log File'])

        self.builder.tkvariables['Entry_Stockfish_UCI_Chess960']\
            .set(str(self.engine.data['Stockfish']['UCI_Chess960']))

        self.builder.tkvariables['Entry_Stockfish_Min_Split_Depth']\
            .set(self.engine.data['Stockfish']['Min Split Depth'])

        self.builder.tkvariables['Entry_Stockfish_Threads'].set(self.engine\
            .data['Stockfish']['Threads'])

        self.builder.tkvariables['Entry_Stockfish_Hash'].set(self.engine\
            .data['Stockfish']['Hash'])

    def setting_tooltip(self):
        """Setting tab's tooltips."""
        Tooltip(self.builder.get_object('Label_ChessAI_Analyse_Every_Move'),\
            "Automatic analyse when you move a piece (not when set up)")

        Tooltip(self.builder.get_object('Label_Stockfish_Debug_Log_File'),\
            "Path to file that save debug log (if needed)")

        Tooltip(self.builder.get_object('Label_Stockfish_UCI_Chess960'),\
            "Able to play Chess960")

        Tooltip(self.builder.get_object('Label_Stockfish_Min_Split_Depth'),\
            "Minimum depth for analyse")

        Tooltip(self.builder.get_object('Label_Stockfish_Threads'),\
            "The number of CPU threads used for searching a position. For best performance, set\
\nthis equal to the number of CPU cores available (min 1 max 1024)")

        Tooltip(self.builder.get_object('Label_Stockfish_Hash'),\
            "The size of the hash table in MB. It is recommended to set Hash after\
\nsetting Threads. (min 1 max 33554432)")

    def setting_data(self, widget_id):
        """
        Create logic for `bool` data but in `str` type. (idk, I just cant fix)

        Args:
            widget_id (Any): widget's id
        """
        match widget_id:
            case 'ChessAI_Analyse_Every_Move':
                if self.builder.tkvariables['Entry_ChessAI_Analyse_Every_Move'].get() == 'True':
                    self.builder.tkvariables['Entry_ChessAI_Analyse_Every_Move'].set('False')
                else:
                    self.builder.tkvariables['Entry_ChessAI_Analyse_Every_Move'].set('True')
            case 'Stockfish_UCI_Chess960':
                if self.builder.tkvariables['Entry_Stockfish_UCI_Chess960'].get() == 'True':
                    self.builder.tkvariables['Entry_Stockfish_UCI_Chess960'].set('False')
                else:
                    self.builder.tkvariables['Entry_Stockfish_UCI_Chess960'].set('True')

    def setting_update_data(self):
        """Update setting data to setting.json file."""
        data = {
            "ChessAI": {
                "Engine": self.engine.data['ChessAI']['Engine'],
                "Analyse Every Move": True if self.builder.tkvariables\
                    ['Entry_ChessAI_Analyse_Every_Move'].get() == 'True' else False,

                "Elo": self.builder.tkvariables['engine_elo'].get(),
                "Current Template": self.engine.data['ChessAI']['Current Template'],
            },
            "Stockfish": {
                "Debug Log File": self.builder.tkvariables['Entry_Stockfish_Debug_Log_File'].get(),
                "UCI_Chess960": True if self.builder.\
                    tkvariables['Entry_Stockfish_UCI_Chess960'].get() == 'True' else False,

                "Min Split Depth": self.builder.\
                    tkvariables['Entry_Stockfish_Min_Split_Depth'].get(),

                "Threads": self.builder.tkvariables['Entry_Stockfish_Threads'].get(),
                "Hash": self.builder.tkvariables['Entry_Stockfish_Hash'].get(),
            },
        }

        if getattr(sys, "frozen", False):
            file_location = 'setting.json'
        else:
            file_location = PROJECT_PATH / 'setting.json'
        with open(file_location, mode="w", encoding="utf-8") as write_file:
            json.dump(data, write_file, indent=4)
            write_file.close()

        self.engine.data = data

    def setting_warning(self) -> None:
        """Warn user if settings are changed."""
        def check(object_name: str, correct_answer: str | int) -> None:
            try:
                answer = self.builder.tkvariables[f'Entry_{object_name}'].get()
                if answer == correct_answer:
                    setattr(self, object_name,\
                        tk.PhotoImage(file=PROJECT_PATH / 'UI_Assets/empty.png'))
                else:
                    setattr(self, object_name,\
                        tk.PhotoImage(file=PROJECT_PATH / 'UI_Assets/warning.png'))
            except KeyError: # if can not find variable, just warning.
                setattr(self, object_name,\
                    tk.PhotoImage(file=PROJECT_PATH / 'UI_Assets/warning.png'))
            finally:
                self.builder.get_object(f'Warning_{object_name}')\
                    .config(image=getattr(self, object_name))

        check('ChessAI_Analyse_Every_Move', str(self.engine.data['ChessAI']['Analyse Every Move']))
        check('Stockfish_Debug_Log_File', self.engine.data['Stockfish']['Debug Log File'])
        check('Stockfish_UCI_Chess960', str(self.engine.data['Stockfish']['UCI_Chess960']))
        check('Stockfish_Min_Split_Depth', self.engine.data['Stockfish']['Min Split Depth'])
        check('Stockfish_Threads', self.engine.data['Stockfish']['Threads'])
        check('Stockfish_Hash', self.engine.data['Stockfish']['Hash'])

        self.mainwindow.after(100, self.setting_warning)
