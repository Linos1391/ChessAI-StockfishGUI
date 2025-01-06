"""The computer vision of ChessAI. Trainable templates with Pytorch (if installed)."""

import os
import pathlib
import json
from datetime import date

from PIL import Image

from .sub_gui.gui_base import PROJECT_PATH

PYTORCH_AVAILABLE: bool = True
try:
    from .train import TrainModel, LoadModel
except ImportError:
    PYTORCH_AVAILABLE = False

ANALYSE_PATH: str = os.path.join(PROJECT_PATH, 'Templates', 'Analyse.png')

REQUIREMENTS: tuple = (
    'Chessboard.png', 'Info.json', 'Labels.csv', 'Empty_1.png', 'Empty_2.png',
    'Black_Bishop_1.png', 'Black_Bishop_2.png', 'Black_King_1.png', 'Black_King_2.png',
    'Black_Knight_1.png', 'Black_Knight_2.png', 'Black_Pawn_1.png', 'Black_Pawn_2.png',
    'Black_Queen_1.png', 'Black_Queen_2.png', 'Black_Rook_1.png', 'Black_Rook_2.png',
    'White_Bishop_1.png', 'White_Bishop_2.png', 'White_King_1.png', 'White_King_2.png',
    'White_Knight_1.png', 'White_Knight_2.png', 'White_Pawn_1.png', 'White_Pawn_2.png',
    'White_Queen_1.png', 'White_Queen_2.png', 'White_Rook_1.png', 'White_Rook_2.png',
)

class Vision:
    """
    Main computer vision of ChessAI.
    """
    def __init__(self):
        self.labels_map: dict = {
            0: 'Black Bishop',
            1: 'Black King',
            2: 'Black Knight',
            3: 'Black Pawn',
            4: 'Black Queen',
            5: 'Black Rook',
            6: 'White Bishop',
            7: 'White King',
            8: 'White Knight',
            9: 'White Pawn',
            10: 'White Queen',
            11: 'White Rook',
            12: 'Black Empty', # I do 'Black' -> `.lower()`
        }

        self.update_template_path()

    def update_template_path(self, template_name: str = 'Chesscom'):
        """
        Update template path.

        Args:
            template_name (str, optional): template's name. Defaults to 'Chesscom'.
        """
        self.template_path = pathlib.Path(os.path.join(PROJECT_PATH, 'Templates', template_name))

    def get_info_value(self) -> tuple:
        """
        Get all values from Info.json file.

        Raises:
            FileNotFoundError: Cannot find the file.

        Returns:
            tuple: list of info's values.
        """
        try:
            with open(self.template_path / 'Info.json', mode="r", encoding="utf-8") as read_file:
                info: dict = json.load(read_file)
                read_file.close()
        except FileNotFoundError as err:
            raise FileNotFoundError('Cannot find Info.json file. Without it, a template is \
                considered as broken. Please recreate the template again.') from err
        return (value for value in info.values())

    @staticmethod
    def count_templates() -> tuple:
        """
        Find legal templates.

        Returns:
            tuple: list of legal templates.
        """
        def check_valid(path: str) -> bool:
            """
            The templates must fit the requirements.
            """
            for _, _, files in os.walk(path):
                for file in REQUIREMENTS:
                    try:
                        files.remove(file)
                    except ValueError:
                        return False
                return True

        result: list = []
        for item in os.scandir(PROJECT_PATH / 'Templates'):
            if item.is_file():
                continue

            if check_valid(item.path):
                result.append(item.name)
        return tuple(result)

    @staticmethod
    def make_chessboard_template(img: Image.Image) -> Image.Image:
        """
        Try to make to the background one color only.

        Args:
            img (Image.Image): provided image.

        Returns:
            Image.Image: converted image.
        """
        # You know... sometimes by hand is better.
        img = img.convert('RGB')
        bg_color = img.getpixel((0,0))

        width, height = img.size

        top: int = 0
        down: int = height
        left: int = 0
        right: int = width

        # erase all bg color
        for loc_y in range(height):
            for loc_x in range(width):
                if img.getpixel((loc_x, loc_y)) == bg_color:
                    img.putpixel((loc_x, loc_y), (0, 0, 0))

        # crop to content:
        center_x = int(width / 2)
        center_y = int(height / 2)

        # from center to top:
        for loc_y in range(center_y, 0, -1):
            if img.getpixel((center_x, loc_y)) == (0, 0, 0):
                top = loc_y
                break

        # from center to down:
        for loc_y in range(center_y, height):
            if img.getpixel((center_x, loc_y)) == (0, 0, 0):
                down = loc_y
                break

        # from center to left:
        for loc_x in range(center_x, 0, -1):
            if img.getpixel((loc_x, center_y)) == (0, 0, 0):
                left = loc_x
                break

        # from center to right:
        for loc_x in range(center_x, width):
            if img.getpixel((loc_x, center_y)) == (0, 0, 0):
                right = loc_x
                break

        img = img.crop((left, top, right, down))

        # resize the chessboard (is square && able to divided by 8)
        chosen_pixel: int = int(img.size[0]/8) * 8
        img = img.resize((chosen_pixel, chosen_pixel))

        return img

    def make_chesspiece_template(self, chessboard_image: Image.Image, chess_name: str) -> None:
        """
        We will use the chessboard that made initially.
        *Notice:* I used rembg for fast background removal. The correction must be done by hand.

        Args:
            chessboard_image (Image.Image): provided chessboard image.
            chess_name (str): chessboard's name.
        """
        # create template's images.
        width, height = chessboard_image.size

        # I have to separate 64 cells.
        width_pix = width / 8
        height_pix = height / 8

        # those on board.
        for (loc_x, loc_y, name) in (
                (0, 0, 'Black_Rook_1.png'),
                (7, 0, 'Black_Rook_2.png'),
                (6, 0, 'Black_Knight_1.png'),
                (1, 0, 'Black_Knight_2.png'),
                (2, 0, 'Black_Bishop_1.png'),
                (5, 0, 'Black_Bishop_2.png'),
                (3, 0, 'Black_Queen_2.png'),
                (4, 0, 'Black_King_1.png'),
                (1, 1, 'Black_Pawn_1.png'),
                (0, 1, 'Black_Pawn_2.png'),
                (7, 7, 'White_Rook_1.png'),
                (0, 7, 'White_Rook_2.png'),
                (1, 7, 'White_Knight_1.png'),
                (6, 7, 'White_Knight_2.png'),
                (2, 7, 'White_Bishop_1.png'),
                (5, 7, 'White_Bishop_2.png'),
                (3, 7, 'White_Queen_1.png'),
                (4, 7, 'White_King_2.png'),
                (0, 6, 'White_Pawn_1.png'),
                (1, 6, 'White_Pawn_2.png'),
                (0, 2, 'Empty_1.png'),
                (1, 2, 'Empty_2.png'),
            ):

            img = chessboard_image.crop((loc_x * width_pix + 1,
                                         loc_y * height_pix + 1,
                                         (loc_x + 1) * width_pix,
                                         (loc_y + 1) * height_pix,))
            img.save(self.template_path / name)

        # those not
        empty_1 = Image.open(self.template_path / 'Empty_1.png').convert('RGB')
        empty_2 = Image.open(self.template_path / 'Empty_2.png').convert('RGB')

        for name in ('Black_King_2.png',
                     'Black_Queen_1.png',
                     'White_King_1.png',
                     'White_Queen_2.png',):
            mode: str = name[-5]
            if mode == '1':
                opposite_name: str = name[:-5] + '2.png'
                img = Image.open(self.template_path / opposite_name).convert('RGB')
                opposite_width, opposite_mode_height = img.size

                for loc_x in range(opposite_width):
                    for loc_y in range(opposite_mode_height):
                        if img.getpixel((loc_x, loc_y)) == empty_2.getpixel((loc_x, loc_y)):
                            img.putpixel((loc_x, loc_y), empty_1.getpixel((loc_x, loc_y)))

            elif mode == '2':
                opposite_name: str = name[:-5] + '1.png'
                img = Image.open(self.template_path / opposite_name).convert('RGB')
                opposite_width, opposite_mode_height = img.size

                for loc_x in range(opposite_width):
                    for loc_y in range(opposite_mode_height):
                        if img.getpixel((loc_x, loc_y)) == empty_1.getpixel((loc_x, loc_y)):
                            img.putpixel((loc_x, loc_y), empty_2.getpixel((loc_x, loc_y)))

            img.save(self.template_path / name)

        # make labels map and save as Labels.csv file.
        labels: str = """\
Black_Bishop_1.png, 0
Black_Bishop_2.png, 0
Black_King_1.png, 1
Black_King_2.png, 1
Black_Knight_1.png, 2
Black_Knight_2.png, 2
Black_Pawn_1.png, 3
Black_Pawn_2.png, 3
Black_Queen_1.png, 4
Black_Queen_2.png, 4
Black_Rook_1.png, 5
Black_Rook_2.png, 5
White_Bishop_1.png, 6
White_Bishop_2.png, 6
White_King_1.png, 7
White_King_2.png, 7
White_Knight_1.png, 8
White_Knight_2.png, 8
White_Pawn_1.png, 9
White_Pawn_2.png, 9
White_Queen_1.png, 10
White_Queen_2.png, 10
White_Rook_1.png, 11
White_Rook_2.png, 11
Empty_1.png, 12
Empty_2.png, 12
"""
        with open(self.template_path / 'Labels.csv', mode="w", encoding="utf-8") as write_file:
            write_file.write(labels)
            write_file.close()

        train_model_process = TrainModel(self.template_path / 'Labels.csv', self.template_path)

        info: dict = {
            "name": chess_name,
            "date": date.today().strftime('%d/%m/%Y'),
            "accuracy": f'{(train_model_process.hardcore_train()*100):>0.1f}%',
        }

        train_model_process.save(self.template_path)

        with open(self.template_path / 'Info.json', mode="w", encoding="utf-8") as write_file:
            json.dump(info, write_file, indent=4)
            write_file.close()

    def remake_chesspiece_template(self):
        """Re-train the model."""
        train_model_process = \
            TrainModel(self.template_path / 'Labels.csv', self.template_path)

        info: dict = {
            "name": pathlib.Path(self.template_path).name,
            "date": date.today().strftime('%d/%m/%Y'),
            "accuracy": f'{(train_model_process.hardcore_train()*100):>0.1f}%',
        }

        train_model_process.save(self.template_path)

        with open(self.template_path / 'Info.json', mode="w", encoding="utf-8") as write_file:
            json.dump(info, write_file, indent=4)
            write_file.close()

    def analyse_chess_pieces(self, chessboard_image: Image.Image) -> list[list[str]]:
        """
        Analyse provided chessboard and return board format.

        Args:
            chessboard_image (Image.Image): provided chessboard.

        Returns:
            list[list[str]]: board format.
        """
        load_model_process = LoadModel(self.template_path)

        # create template's images.
        width, height = chessboard_image.size

        # I have to separate 64 cells.
        width_pix = width / 8
        height_pix = height / 8

        board: list[list[str]] = []
        for loc_y in range(8):
            row: list[str] = []
            for loc_x in range(8):
                img = chessboard_image.crop((loc_x * width_pix + 1,
                                             loc_y * height_pix + 1,
                                             (loc_x + 1) * width_pix,
                                             (loc_y + 1) * height_pix,))
                color, piece = load_model_process.predict(\
                    tuple(self.labels_map.values()), img).split()

                piece = piece[0]
                if color == 'Black':
                    piece = piece.lower()

                row.append(piece)
            board.append(row)
        return board

if __name__ == '__main__':
    pass
