"""The vision tab for ChessAI."""

import json
import sys
import shutil
import os

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import pyscreeze


from .gui_base import ChessAIBase, PROJECT_PATH
from .tooltip import Tooltip

from ..vision import Vision, ANALYSE_PATH, PYTORCH_AVAILABLE

vision_ext = Vision()

class ChessAIVision(ChessAIBase): #inherit
    """The setting tab for ChessAI."""
    def __init__(self):
        super().__init__()
        self.vision_black_side: bool = False
        self.crop_for_analyse: bool = False
        self.vision_crop_rect = None
        self.delete_template = None

        # for measuring image to add into canvas.
        self.vision_original_width: int = 0
        self.vision_original_height: int = 0
        self.vision_x: int = 0
        self.vision_y: int = 0
        self.vision_width: int = 0
        self.vision_height: int = 0

        # image storage (so that wont be deleted automatically)
        self.vision_add_image = None
        self.vision_side_image = None
        self.vision_crop_canva = None

        #dummy attributes
        self.white_king_exist: int = 1
        self.black_king_exist: int = 1
        self.cropping_dialog = None
        self.delete_dialog = None
        self.template_dialog = None
        self.info_dialog = None

    def set_fen(self) -> None:
        """Dummy function right now."""
        return

    def warning(self, _: str) -> None:
        """Dummy function right now."""
        return

    def vision__init__(self):
        """__init__ for the Vision tab"""
        self.vision_tooltip()
        self.vision_check_templates()

    def vision_warn_no_torch(self):
        """Warn user if doesn't have PyTorch installed."""
        if not PYTORCH_AVAILABLE:
            self.warning('Training features are not allowed, to unlock this feature, please visit \
https://github.com/Linos1391/ChessAI-StockfishGUI/blob/main/TRAINING.md')

    def vision_choose(self, event: object):
        """Choose a template."""
        template = event.widget._name[7:]

        if self.engine.data['ChessAI']['Current Template'] == template:
            return

        self.engine.data['ChessAI']['Current Template'] = template

        if getattr(sys, "frozen", False):
            file_location = 'setting.json'
        else:
            file_location = PROJECT_PATH / 'setting.json'
        with open(file_location, mode="w", encoding="utf-8") as write_file:
            json.dump(self.engine.data, write_file, indent=4)
            write_file.close()

        vision_ext.update_template_path(template)

        self.vision_check_templates()

    def vision_add(self):
        """Show dialog that help adding new template."""
        self.vision_warn_no_torch()

        if PYTORCH_AVAILABLE:
            self.template_dialog.show()

    def vision_add_screenshot(self):
        """Add new template through screenshot."""
        self.template_dialog.close()

        pyscreeze.screenshot(ANALYSE_PATH)
        self.crop_for_analyse = False
        self.vision_crop()

    def vision_add_choose_file(self, event: object):
        """Add new tempate through choosing file."""
        self.template_dialog.close()

        img = Image.open(event.widget.cget(key="path"))
        img.save(ANALYSE_PATH)
        self.crop_for_analyse = False
        self.vision_crop()

    def vision_delete_ask(self, event: object):
        """Ask for comfirmation of deleting a template."""
        self.delete_template = event.widget._name[7:]
        self.delete_dialog.show()

    def vision_delete(self):
        """Delete the template."""
        self.delete_dialog.close()

        if self.delete_template is None:
            return

        shutil.rmtree(os.path.join(PROJECT_PATH, 'Templates', self.delete_template))
        self.delete_template = None

        self.vision_check_templates()

    def vision_info(self, event: object):
        """Show template's info."""
        template = event.widget._name[5:]
        vision_ext.update_template_path(template)

        vision_name, vision_date, vision_accuracy = vision_ext.get_info_value()

        self.builder.tkvariables['vision_name'].set(vision_name)
        self.builder.tkvariables['vision_date'].set(vision_date)
        self.builder.tkvariables['vision_accuracy_var'].set(vision_accuracy)

        self.info_dialog.show()

    def vision_info_update(self):
        """Re-train model."""
        self.vision_warn_no_torch()

        self.info_dialog.close()
        if not PYTORCH_AVAILABLE:
            return

        vision_ext.remake_chesspiece_template()

    def vision_check_templates(self):
        """Check all valid templates and show them."""
        # Only some are valid
        templates: tuple = vision_ext.count_templates()

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
                chessboard = Image.open(\
                    os.path.join(PROJECT_PATH, 'Templates', template, 'Chessboard.png'))
                chessboard = chessboard.resize((70, 70))
                setattr(self, f'vision_item{index+1}_chessboard', ImageTk.PhotoImage(chessboard))
                chessboard = tk.Label(master=frame, image=\
                    getattr(self, f'vision_item{index+1}_chessboard'), background='#d9d9d9')
                chessboard.place(x=2, y=2, width=72, height=72)

                # for template's name:
                label = tk.Label(master=frame, text=template, background='#d9d9d9', wraplength=107)
                label.place(x=80, y=23)

                # for info button:
                info = Image.open(os.path.join(PROJECT_PATH, 'UI_Assets', 'vision_info.png'))
                setattr(self, f'vision_item{index+1}_info', ImageTk.PhotoImage(info))
                info = tk.Label(master=frame, name=f'info_{template}', image=\
                    getattr(self, f'vision_item{index+1}_info'), background='#d9d9d9')
                info.bind('<ButtonPress-1>', self.vision_info)
                Tooltip(info, 'Click to see template\'s info')
                info.place(x=209, y=21, width=34, height=34)

                # for choose button:
                if template == chosen_template:
                    choose_option = Image.open(\
                        os.path.join(PROJECT_PATH, 'UI_Assets', 'vision_choose.png'))
                else:
                    choose_option = Image.open(\
                        os.path.join(PROJECT_PATH, 'UI_Assets', 'vision_unchoose.png'))

                setattr(self, f'vision_item{index+1}_choose', ImageTk.PhotoImage(choose_option))
                choose_option = tk.Label(master=frame, name=f'choose_{template}', image=\
                    getattr(self, f'vision_item{index+1}_choose'), background='#d9d9d9')
                choose_option.bind('<ButtonPress-1>', self.vision_choose)
                Tooltip(choose_option, 'Click to select template')
                choose_option.place(x=245, y=21, width=34, height=34)

                # for delete button
                delete = Image.open(os.path.join(PROJECT_PATH, 'UI_Assets', 'deselect.png'))
                setattr(self, f'vision_item{index+1}_delete', ImageTk.PhotoImage(delete))
                delete = tk.Label(master=frame, name=f'delete_{template}', image=\
                    getattr(self, f'vision_item{index+1}_delete'), background='#d9d9d9')
                delete.bind('<ButtonPress-1>', self.vision_delete_ask)
                Tooltip(delete, 'Click to delete template')
                delete.place(x=281, y=21, width=34, height=34)

        add = Image.open(os.path.join(PROJECT_PATH, 'UI_Assets', 'vision_add.png'))
        self.vision_add_image = ImageTk.PhotoImage(add)
        add = ttk.Button(master=panel.innerframe, image=\
            self.vision_add_image, command=self.vision_add)
        Tooltip(add, 'Click to add custom template')
        add.pack(padx=1, fill='x')

    def vision_tooltip(self):
        """vision tab's tooltip."""
        Tooltip(self.builder.get_object('Vision_side'),\
            'Change the side (User are black or white)')
        Tooltip(self.builder.get_object('vision_change_points'),\
            'Re-train model using PyTorch')
        Tooltip(self.builder.get_object('vision_accuracy'),\
            'Model\'s accuracy')

    def vision_side(self, _: object):
        """Change chessboard's side."""
        if self.vision_black_side:
            self.vision_side_image = ImageTk.PhotoImage(Image.open(\
                os.path.join(PROJECT_PATH, 'UI_Assets', 'vision_white.png')))
            self.vision_black_side = False
        else:
            self.vision_side_image = ImageTk.PhotoImage(Image.open(\
                os.path.join(PROJECT_PATH, 'UI_Assets', 'vision_black.png')))
            self.vision_black_side = True
        self.builder.get_object('Vision_side').config(image=self.vision_side_image)

    def vision_screenshot(self):
        """Screenshot for analyzing the chessboard."""
        self.vision_warn_no_torch()
        if not PYTORCH_AVAILABLE:
            return

        pyscreeze.screenshot(ANALYSE_PATH)
        self.crop_for_analyse = True
        self.vision_crop()

    def vision_choose_file(self, event: object):
        """Choose file for analyzing the chessboard."""
        self.vision_warn_no_torch()
        if not PYTORCH_AVAILABLE:
            return

        img = Image.open(event.widget.cget(key="path"))
        img.save(ANALYSE_PATH)
        self.crop_for_analyse = True
        self.vision_crop()

    def vision_crop(self):
        """Open the crop system."""
        img = Image.open(ANALYSE_PATH)
        self.vision_original_width, self.vision_original_height = img.size

        width = int(self.vision_original_width * 200 / self.vision_original_height)

        img = img.resize((width, 200))
        self.vision_crop_canva = ImageTk.PhotoImage(img)

        self.builder.tkvariables['vision_var_width'].set(self.vision_original_width)
        self.builder.tkvariables['vision_var_height'].set(self.vision_original_height)
        self.builder.get_object('vision_crop').config(width = width)
        self.builder.get_object('vision_crop')\
            .create_image(0, 0, image=self.vision_crop_canva, anchor="nw")
        self.vision_crop_image()
        self.cropping_dialog.show()

    def vision_crop_image(self):
        """Function to crop the image."""
        # 1 <= vision_x < self.vision_original_width
        vision_x: int = self.builder.tkvariables['vision_var_x']
        if vision_x.get() >= self.vision_original_width:
            x = int((self.vision_original_width-1) * 200 / self.vision_original_height)
            vision_x.set(self.vision_original_width - 1)
        elif vision_x.get() < 1:
            x = 0
            vision_x.set(1)
        else:
            x = int(vision_x.get() * 200 / self.vision_original_height)

        # 1 <= vision_y < self.vision_original_height
        vision_y: int = self.builder.tkvariables['vision_var_y']
        if vision_y.get() >= self.vision_original_height:
            y = int((self.vision_original_height-1) * 200 / self.vision_original_height)
            vision_y.set(self.vision_original_height - 1)
        elif vision_y.get() < 1:
            y = 0
            vision_y.set(1)
        else:
            y = int(vision_y.get() * 200 / self.vision_original_height)

        # vision_x < vision_width+vision_x <= self.vision_original_width
        vision_width: int = self.builder.tkvariables['vision_var_width']
        if vision_width.get() + x > self.vision_original_width:
            width = int((\
                self.vision_original_width-vision_x.get()) * 200 / self.vision_original_height)
            vision_width.set(self.vision_original_width - vision_x.get())
        elif vision_width.get() < 1:
            width = 1
            vision_width.set(1)
        else:
            width = int(vision_width.get() * 200 / self.vision_original_height)

        # vision_y < vision_height+vision_y <= self.vision_original_height
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

        self.vision_x = vision_x.get()
        self.vision_y = vision_y.get()
        self.vision_width = vision_width.get()
        self.vision_height = vision_height.get()

        self.vision_crop_rect = self.builder.get_object('vision_crop')\
            .create_rectangle(x, y, x+width-1, y+height-1, outline='red')

    def vision_crop_submit(self):
        """Submit cropped image."""
        self.cropping_dialog.close()
        img = Image.open(ANALYSE_PATH)
        img = img.crop((self.vision_x, self.vision_y, self.vision_x\
            +self.vision_width, self.vision_x+self.vision_height))

        try:
            img = vision_ext.make_chessboard_template(img=img)
        except Exception as err:
            print(f'{err}\nVision error code: 1')
            self.warning('Please crop better or choose\nanother file / screenshot again.')
            return

        if self.crop_for_analyse:
            img.save(ANALYSE_PATH)

            try:
                self.board = vision_ext.analyse_chess_pieces(img)
            except Exception as err:
                print(f'{err}\nVision error code: 2')
                self.warning('Please crop better or choose\nanother file / screenshot again.')
                return

            self.fen = self.board_to_fen(self.board)

            self.white_king_exist = self.fen.split()[0].count('K')
            self.black_king_exist = self.fen.split()[0].count('k')

            try:
                with open(PROJECT_PATH / 'history.json', mode="r", encoding="utf-8") as read_file:
                    existed_data: dict = json.load(read_file)
                    read_file.close()
            except FileNotFoundError as err:
                raise FileNotFoundError('Cannot access history.json file') from err

            data: dict = {
                str(self.engine.current_move): {
                    "fen": self.fen
                }
            }

            for _id in range(self.engine.current_move, len(existed_data)):
                existed_data.pop(str(_id))

            existed_data.update(data)

            with open(PROJECT_PATH / 'history.json', mode="w", encoding="utf-8") as write_file:
                json.dump(existed_data, write_file, indent=4)
                write_file.close()

            self.set_fen()
            self.update_chessboard()

            if self.vision_black_side:
                self.builder.get_object('black_side').config(background='#888888')
                self.builder.get_object('white_side').config(background='')
                self.is_black = True

                sliced_fen: tuple[str] = self.fen.split(" ", 2)
                sliced_fen[1] = 'b'
                self.fen = ' '.join(sliced_fen)
                self.set_fen()
            else:
                self.builder.get_object('white_side').config(background='#888888')
                self.builder.get_object('black_side').config(background='')
                self.is_black = False

                sliced_fen: tuple[str] = self.fen.split(" ", 2)
                sliced_fen[1] = 'w'
                self.fen = ' '.join(sliced_fen)
                self.set_fen()

        else:
            name = self.builder.tkvariables['template_name'].get()

            if name == '':
                name = 'Untitled'
            try:
                os.mkdir(os.path.join(PROJECT_PATH, 'Templates', name))
            except FileExistsError:
                pass # maybe you created it then

            vision_ext.update_template_path(name)

            img.save(vision_ext.template_path / 'Chessboard.png')

            try:
                vision_ext.make_chesspiece_template(img, name)
            except Exception as err:
                print(f'{err}\nVision error code: 3')
                return

            self.vision_check_templates()

        self.crop_for_analyse = None
        os.remove(ANALYSE_PATH)

    def vision_crop_hovering(self, event: object):
        """
        Show current x, y location on canvas.
        """
        cur_x: int = int(event.x/200 * self.vision_original_height)
        cur_y: int = int(event.y/200 * self.vision_original_height)

        self.builder.tkvariables['vision_crop_hovering_var'].set(f'x = {cur_x}, y = {cur_y}')
