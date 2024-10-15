import os
import pathlib
import json
from datetime import date
from PIL import Image
import pyscreeze
from rembg import remove

PROJECT_PATH: str = pathlib.Path(__file__).parent
ANALYSE_PATH: str = os.path.join(PROJECT_PATH, 'Templates', 'Analyse.png') 

REQUIREMENTS: tuple = ('Chessboard.png', 'Light_Color.png', 'Dark_Color.png', 'Info.json',
    'Black_Bishop.png', 'Black_King.png', 'Black_Knight.png', 'Black_Pawn.png', 'Black_Queen.png', 'Black_Rook.png',
    'White_Bishop.png', 'White_King.png', 'White_Knight.png', 'White_Pawn.png', 'White_Queen.png', 'White_Rook.png',
)

BOARD_DICT: dict = {
    "White_Pawn.png": "P",
    "White_Bishop.png": "B",
    "White_Knight.png": "N",
    "White_Rook.png": "R",
    "White_Queen.png": "Q",
    "White_King.png": "K",
    "Black_Pawn.png": "p",
    "Black_Bishop.png": "b",
    "Black_Knight.png": "n",
    "Black_Rook.png": "r",
    "Black_Queen.png": "q",
    "Black_King.png": "k",
}

def _update_template_path(template_name: str = 'Chesscom'):
    return pathlib.Path(os.path.join(PROJECT_PATH, 'Templates', template_name))

TEMPLATE_PATH: str = _update_template_path()

#———————————Main———————————#

def _screenshot() -> None:
    pyscreeze.screenshot(ANALYSE_PATH)

# Print iterations progress
def _print_progress_bar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

def count_templates() -> list:
    """
    Find legal templates.
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
    return result

def make_chessboard_template(img: Image.Image, analyse: bool = False) -> Image.Image:
    """
    Try to make to the background one color only.
    """
    # add alpha channel
    img = img.convert('RGBA')
    
    bg_color = img.getpixel((0,0)) # you know... rembg sucks
    
    width, height = img.size
    
    top: int = 0
    down: int = height
    left: int = 0
    right: int = width
    
    # erase all bg color
    for locY in range(height):
        for locX in range(width):
            if img.getpixel((locX, locY)) == bg_color:
                img.putpixel((locX, locY), (0, 0, 0, 0))
    
    # crop to content:
    centerX = int(width / 2)
    centerY = int(height / 2)
    
    # from center to top:
    for locY in range(centerY, 0, -1):
        if img.getpixel((centerX, locY)) == (0, 0, 0, 0):
            top = locY
            break
        
    # from center to down:
    for locY in range(centerY, height):
        if img.getpixel((centerX, locY)) == (0, 0, 0, 0):
            down = locY
            break
    
    # from center to left:
    for locX in range(centerX, 0, -1):
        if img.getpixel((locX, centerY)) == (0, 0, 0, 0):
            left = locX
            break
    
    # from center to right:
    for locX in range(centerX, width):
        if img.getpixel((locX, centerY)) == (0, 0, 0, 0):
            right = locX
            break        

    img = img.crop((left, top, right, down))
    
    # resize the chessboard (is square && able to divided by 8)
    chosen_pixel: int = int(img.size[0]/8) * 8
    img = img.resize((chosen_pixel, chosen_pixel))
    
    return img
                
def make_chesspiece_template(chessboard_image: Image.Image, chess_name: str) -> None:
    """
    We will use the chessboard that made initially.
    
    **Notice:** I used rembg for fast background removal. The correction must be done by hand.
    """
    print('+------------------------------------------------+')
    print('| We will freeze the app so no error will appear |')
    print('+------------------------------------------------+')
    
    width, height = chessboard_image.size
    
    # I have to separate 64 cells
    width_pix = width / 8
    height_pix = height / 8
    
    print('Making chess pieces\' templates:')
    for (locX, locY, name, index) in (
            (7, 0, 'Black_Rook.png', 1), 
            (1, 0, 'Black_Knight.png', 2), 
            (2, 0, 'Black_Bishop.png', 3),
            (3, 0, 'Black_Queen.png', 4),
            (4, 0, 'Black_King.png', 5),
            (1, 1, 'Black_Pawn.png', 6),
            (0, 7, 'White_Rook.png', 7), 
            (6, 7, 'White_Knight.png', 8), 
            (2, 7, 'White_Bishop.png', 9),
            (3, 7, 'White_Queen.png', 10),
            (4, 7, 'White_King.png', 11),
            (1, 6, 'White_Pawn.png', 12),
            (6, 2, 'Light_Color.png', 13),
            (6, 3, 'Dark_Color.png', 14),
        ):
        
        img = chessboard_image.crop((locX * width_pix + 1,
                                     locY * height_pix + 1,
                                     (locX + 1) * width_pix,
                                     (locY + 1) * height_pix,))
        if name not in ('Light_Color.png', 'Dark_Color.png'):
            img = remove(img)
        img.save(TEMPLATE_PATH / name)
        _print_progress_bar(index, 14)
    
    print('+-----------------------------------------------------------------------------------+')
    print('| Create O.P and I.P, will take lots of time. Grab some coffee or do something else |')
    print('+-----------------------------------------------------------------------------------+')
    
    success, OP, IP, pattern = create_OP_and_IP()
    if not success:
        print('OP and IP are not valid, please edit the template. OP and IP will be set to -5 and +10, respectively')
    
    info: dict = {
        "name": chess_name,
        "date": date.today().strftime('%d/%m/%Y'),
        "O.P": f'-{OP}',
        "I.P": f'+{IP}',
        "pattern": pattern
    }
    
    with open(TEMPLATE_PATH / 'Info.json', mode="w", encoding="utf-8") as write_file:
        json.dump(info, write_file, indent=4)
        write_file.close()

def _get_info_value() -> tuple:
    try:
        with open(TEMPLATE_PATH / 'Info.json', mode="r", encoding="utf-8") as read_file:
            info: dict = json.load(read_file)
            read_file.close()
    except:
        raise Exception('Cannot find Info.json file. This should not be possible unless you touched it. Please delete your template and create a new one.')
    
    return (value for value in info.values())
    
def analyse_chess_pieces(img: Image.Image,) -> list[list]:
    """
    Analyse chess pieces through provided chessboard image.
    """
    
    def get_color(name: str, width: int, height: int) -> tuple[Image.Image, tuple]:
        img = Image.open(TEMPLATE_PATH / name)
        img = img.resize((width, height))
        
        return (img, img.getpixel((int(width/2), int(height/2))))
    
    def label_chess_pieces(OP: int, IP: int, img: Image.Image) -> str:
        width, height = img.size
        
        light_cell, light_color = get_color('Light_Color.png', width, height)
        dark_cell, dark_color = get_color('Dark_Color.png', width, height)
        
        if img.getpixel((int(width/2), int(height/2))) in (light_color, dark_color):
            return 'e'
               
        max_same_pattern: list[int, str] = [-100, '']

        for name in REQUIREMENTS[3:]:
            template = Image.open(TEMPLATE_PATH / name)
            template.resize((width, height))
            
            pattern: int = 0
            
            for locY in range(height):
                for locX in range(width):
                    light_color = light_cell.getpixel((locX, locY)) 
                    dark_color = dark_cell.getpixel((locX, locY)) 
                    
                    if img.getpixel((locX, locY)) in (light_color, dark_color) and template.getpixel((locX, locY)) == (0, 0, 0, 0):
                        continue
                    
                    if img.getpixel((locX, locY)) in (light_color, dark_color):
                        pattern += OP # OP is a negative number
                    
                    if img.getpixel((locX, locY)) == template.getpixel((locX, locY)):
                        pattern += IP
                    
            if pattern > max_same_pattern[0]:
                max_same_pattern = [pattern, name]
        return BOARD_DICT[max_same_pattern[1]]
        
    width, height = img.size
    
    # I have to separate 64 cells
    width_pix = width / 8
    height_pix = height / 8

    board: list[list] = []
    
    _, _, OP, IP = _get_info_value()
    
    print('Begin to analyse chessboard')
    for locY in range(8):
        small_board: list = []
        for locX in range(8):
            _print_progress_bar(locX + 8*locY + 1, 64)
            key = label_chess_pieces(OP, IP,
                img.crop((
                    locX * width_pix + 1,
                    locY * height_pix + 1,
                    (locX + 1) * width_pix,
                    (locY + 1) * height_pix,)
                    )
                )
            small_board.append(key)

        board.append(small_board)
    return board

def create_OP_and_IP() -> tuple:
    PIECES: tuple = (
        "White_Pawn.png",
        "White_Bishop.png",
        "White_Knight.png",
        "White_Rook.png",
        "White_Queen.png",
        "White_King.png",
        "Black_Pawn.png",
        "Black_Bishop.png",
        "Black_Knight.png",
        "Black_Rook.png",
        "Black_Queen.png",
        "Black_King.png",
    )
    
    width, height = Image.open(TEMPLATE_PATH / PIECES[0]).size
    lookalike_pattern: dict = {} # there might be those pieces that look the same. We will skip that (At lease can edit chessboard by our own hand)
    
    exit: bool = False
    IP: int  = 0
    while IP < 50 and not exit:
        for OP in range(IP):
            if exit:
                break
            
            max_same_pattern: list[int, str] = [-100000, '']
            
            for main_piece in PIECES:
                img = Image.open(TEMPLATE_PATH / main_piece)
                
                for template_piece in PIECES:
                    template = Image.open(TEMPLATE_PATH / template_piece)
                    
                    pattern: int = 0
                    
                    for locY in range(height):
                        for locX in range(width):

                            if (0, 0, 0, 0) in (img.getpixel((locX, locY)), template.getpixel((locX, locY))):
                                continue
                            
                            if template.getpixel((locX, locY)) != (0, 0, 0, 0):
                                pattern -= OP # OP is not a negative number yet

                            if img.getpixel((locX, locY)) == template.getpixel((locX, locY)):
                                pattern += IP

                    if pattern > max_same_pattern[0]:
                        max_same_pattern = [pattern, template_piece]
                                 
                if main_piece == "Black_King.png": # it has reach the end -> success
                    exit = True
                    break
                
                if main_piece != max_same_pattern[1]:
                    check_lookalike = f'{main_piece}_{max_same_pattern[1]}'
                    
                    try:
                        if lookalike_pattern[check_lookalike] == 25:
                            continue
                    except:
                        pass # ignore them
                    
                    if check_lookalike in lookalike_pattern.keys():
                        lookalike_pattern.update({check_lookalike: lookalike_pattern[check_lookalike]+1})
                    else:
                        lookalike_pattern.update({check_lookalike: 1})
                    
                    OP_write: str = f'{OP}' if OP > 9 else f' {OP}' 
                    IP_write: str = f'{IP}' if IP > 9 else f' {IP}' 
                    print(f'OP: {OP_write}, IP: {IP_write}. Result: Fail')
                    max_same_pattern: list[int, str] = [-100000, '']
                    break 
                
             
        IP += 1
    
    pattern: dict = {}
    
    for key, value in lookalike_pattern.items():
        if value < 25:
            continue
        
        piece_1_before, piece_1_after, piece_2_before, piece_2_after = key.split('_')
        piece_1 = ' '.join([piece_1_before, piece_1_after])[:-4]
        piece_2 = ' '.join([piece_2_before, piece_2_after])[:-4]
        print(f'In the process, find "{piece_1}" and "{piece_2}" has the same pattern.')
        pattern.update({piece_1: piece_2})
    
    if IP == 50:
        return (False, 5, 10, pattern)
    OP_write: str = f'{OP}' if OP > 9 else f' {OP}' 
    IP_write: str = f'{IP}' if IP > 9 else f' {IP}' 
    print(f'OP: {OP_write}, IP: {IP_write}. Result: Success')
    return (True, OP, IP, pattern)

if __name__ == '__main__':
    print('Use "main.py" dude')
