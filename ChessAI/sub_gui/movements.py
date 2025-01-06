"""To define clearly pieces' movements"""

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

class Movement:
    """For better movement visual."""
    def __init__(self):
        self.is_black: bool = False # white side by default
        self.black_side: bool = False
        self.board: list[list[str]] = []

        # main movement ideas.
        self.move_ready: bool = False
        self.move_last: list[int] = []
        self.move_board: list[list[str]] = []
        self.forward: bool = True

        # dummy attributes
        self.engine = None

    def reset_moves(self) -> None:
        """Reset move."""
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
        for loc_y in range(8):
            for loc_x in range(8):
                self.move_board[loc_y][loc_x] = ' '

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
                    loc_x: int = x + index_x - 1
                    loc_y: int
                    if self.is_black:
                        if self.black_side:
                            loc_y = y + index_y - 2
                            self.forward = True
                        else:
                            loc_y = y - index_y + 2
                            self.forward = False
                    else:
                        if self.black_side:
                            loc_y = y - index_y + 2
                            self.forward = False
                        else:
                            loc_y = y + index_y - 2
                            self.forward = True

                    if not 0 <= loc_x <= 7:
                        continue
                    if not 0 <= loc_y <= 7:
                        continue

                    if self.black_side:
                        last_move: str = f'{ALPHABET_DICT[str(7 - x)]}{y + 1}'
                        move: str = f'{ALPHABET_DICT[str(7 - loc_x)]}{loc_y + 1}'
                    else:
                        last_move: str = f'{ALPHABET_DICT[str(x)]}{8 - y}'
                        move: str = f'{ALPHABET_DICT[str(loc_x)]}{8 - loc_y}'

                    if (self.forward and loc_y == 0) or (not self.forward and loc_y == 7):
                        move += 'q'

                    if not self.engine.check_move([last_move + move]):
                        continue

                    if index_y == 0 and index_x == 1:
                        self.move_board[loc_y][loc_x] = '.'

                    if index_y == 1 and (index_x == 0 or index_x == 2):
                        self.move_board[loc_y][loc_x] = 'o'

                    if index_y == 1 and index_x == 1:
                        self.move_board[loc_y][loc_x] = '.'
            return

        # bishop move
        elif self.board[y][x].lower() == 'b':
            for loc_y in range(8):
                if loc_y == y:
                    continue

                # you know... square triangle...
                distant: int = loc_y - y

                for loc_x in (x - distant, x + distant):
                    if not 0 <= loc_x <= 7:
                        continue

                    if self.black_side:
                        last_move: str = f'{ALPHABET_DICT[str(7 - x)]}{y + 1}'
                        move: str = f'{ALPHABET_DICT[str(7 - loc_x)]}{loc_y + 1}'
                    else:
                        last_move: str = f'{ALPHABET_DICT[str(x)]}{8 - y}'
                        move: str = f'{ALPHABET_DICT[str(loc_x)]}{8 - loc_y}'

                    if not self.engine.check_move([last_move + move]):
                        continue

                    if self.board[loc_y][loc_x] == 'e':
                        self.move_board[loc_y][loc_x] = '.'
                        continue
                    self.move_board[loc_y][loc_x] = 'o'
            return

        # knight move
        elif self.board[y][x].lower() == 'n':
            knight_pattern = ((-2, -1),(-2, 1),(-1, -2),(-1, 2),(1, -2),(1, 2),(2, -1),(2, 1))
            for index_x, index_y in knight_pattern:
                loc_x = index_x + x
                loc_y = index_y + y

                if not 0 <= loc_x <= 7 or not 0 <= loc_y <= 7:
                    continue

                if self.black_side:
                    last_move: str = f'{ALPHABET_DICT[str(7 - x)]}{y + 1}'
                    move: str = f'{ALPHABET_DICT[str(7 - loc_x)]}{loc_y + 1}'
                else:
                    last_move: str = f'{ALPHABET_DICT[str(x)]}{8 - y}'
                    move: str = f'{ALPHABET_DICT[str(loc_x)]}{8 - loc_y}'

                if not self.engine.check_move([last_move + move]):
                    continue

                if self.board[loc_y][loc_x] == 'e':
                    self.move_board[loc_y][loc_x] = '.'
                    continue
                self.move_board[loc_y][loc_x] = 'o'
            del knight_pattern
            return

        # rook move
        elif self.board[y][x].lower() == 'r':
            for loc_x in range(8):
                if self.black_side:
                    last_move: str = f'{ALPHABET_DICT[str(7 - x)]}{y + 1}'
                    move: str = f'{ALPHABET_DICT[str(7 - loc_x)]}{y + 1}'
                else:
                    last_move: str = f'{ALPHABET_DICT[str(x)]}{8 - y}'
                    move: str = f'{ALPHABET_DICT[str(loc_x)]}{8 - y}'

                if not self.engine.check_move([last_move + move]):
                    continue

                if self.board[y][loc_x] == 'e':
                    self.move_board[y][loc_x] = '.'
                    continue
                self.move_board[y][loc_x] = 'o'

            for loc_y in range(8):
                if self.black_side:
                    last_move: str = f'{ALPHABET_DICT[str(7 - x)]}{y + 1}'
                    move: str = f'{ALPHABET_DICT[str(7 - x)]}{loc_y + 1}'
                else:
                    last_move: str = f'{ALPHABET_DICT[str(x)]}{8 - y}'
                    move: str = f'{ALPHABET_DICT[str(x)]}{8 - loc_y}'

                if not self.engine.check_move([last_move + move]):
                    continue

                if self.board[loc_y][x] == 'e':
                    self.move_board[loc_y][x] = '.'
                    continue
                self.move_board[loc_y][x] = 'o'
            return

        # queen move
        elif self.board[y][x].lower() == 'q':
            for loc_y in range(8):
                if loc_y == y:
                    continue

                # you know... square triangle...
                distant: int = loc_y - y

                for loc_x in (x - distant, x + distant):
                    if not 0 <= loc_x <= 7:
                        continue

                    if self.black_side:
                        last_move: str = f'{ALPHABET_DICT[str(7 - x)]}{y + 1}'
                        move: str = f'{ALPHABET_DICT[str(7 - loc_x)]}{loc_y + 1}'
                    else:
                        last_move: str = f'{ALPHABET_DICT[str(x)]}{8 - y}'
                        move: str = f'{ALPHABET_DICT[str(loc_x)]}{8 - loc_y}'

                    if not self.engine.check_move([last_move + move]):
                        continue

                    if self.board[loc_y][loc_x] == 'e':
                        self.move_board[loc_y][loc_x] = '.'
                        continue
                    self.move_board[loc_y][loc_x] = 'o'

            for loc_x in range(8):
                if self.black_side:
                    last_move: str = f'{ALPHABET_DICT[str(7 - x)]}{y + 1}'
                    move: str = f'{ALPHABET_DICT[str(7 - loc_x)]}{y + 1}'
                else:
                    last_move: str = f'{ALPHABET_DICT[str(x)]}{8 - y}'
                    move: str = f'{ALPHABET_DICT[str(loc_x)]}{8 - y}'

                if not self.engine.check_move([last_move + move]):
                    continue

                if self.board[y][loc_x] == 'e':
                    self.move_board[y][loc_x] = '.'
                    continue
                self.move_board[y][loc_x] = 'o'

            for loc_y in range(8):
                if self.black_side:
                    last_move: str = f'{ALPHABET_DICT[str(7 - x)]}{y + 1}'
                    move: str = f'{ALPHABET_DICT[str(7 - x)]}{loc_y + 1}'
                else:
                    last_move: str = f'{ALPHABET_DICT[str(x)]}{8 - y}'
                    move: str = f'{ALPHABET_DICT[str(x)]}{8 - loc_y}'

                if not self.engine.check_move([last_move + move]):
                    continue

                if self.board[loc_y][x] == 'e':
                    self.move_board[loc_y][x] = '.'
                    continue
                self.move_board[loc_y][x] = 'o'
            return

        # king move
        else:
            for index_y in range(2):
                for index_x in range(3):
                    loc_x: int = x + index_x - 1
                    loc_y: int = y + 2 * index_y - 1

                    if not 0 <= loc_x <= 7 or not 0 <= loc_y <= 7:
                        continue

                    # check if the king can move
                    if self.black_side:
                        last_move: str = f'{ALPHABET_DICT[str(7 - x)]}{y + 1}'
                        move: str = f'{ALPHABET_DICT[str(7 - loc_x)]}{loc_y + 1}'
                    else:
                        last_move: str = f'{ALPHABET_DICT[str(x)]}{8 - y}'
                        move: str = f'{ALPHABET_DICT[str(loc_x)]}{8 - loc_y}'

                    if not self.engine.check_move([last_move + move]):
                        continue

                    if self.board[loc_y][loc_x] == 'e':
                        self.move_board[loc_y][loc_x] = '.'
                        continue

                    self.move_board[loc_y][loc_x] = 'o'

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
