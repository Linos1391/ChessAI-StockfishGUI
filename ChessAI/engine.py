"""The engine of ChessAI, using stockfish."""

import json
import pathlib
import os

from stockfish import Stockfish, StockfishException

PROJECT_PATH: str = pathlib.Path(__file__).parent

# R.I.P the legend himself o7
class ModifiedStockfish(Stockfish):
    """
    Modified stockfish module so that it can print out commands.

    Args:
        ... (Stockfish's default arguments)
        print_command (bool): whether to print commands to the terminal. Default is True.
    """
    print_command: bool = False # initialize the attribute

    # My code:
    def __init__(self, *args, print_command: bool = True, **kwargs):
        super().__init__(*args, **kwargs)

        self.crashed: bool = False
        self.print_command: bool = print_command
    # so the credit is given

    def _put(self, command: str) -> None:
        if not self._stockfish.stdin:
            raise BrokenPipeError()
        if self._stockfish.poll() is None and not self._has_quit_command_been_sent:
            # My code:
            if self.print_command:
                print(f'\r{(os.get_terminal_size().columns) * ' '}', end='') # clear line
                print(f'\rLast Input: {command}', end='')
                if command == 'quit':
                    print('')
            # so the credit is given
            self._stockfish.stdin.write(f"{command}\n")
            self._stockfish.stdin.flush()
            if command == "quit":
                self._has_quit_command_been_sent = True

    def _read_line(self) -> str:
        if not self._stockfish.stdout:
            raise BrokenPipeError()
        if self._stockfish.poll() is not None:
            # My code:
            self.crashed = True
            #
            raise StockfishException("The Stockfish process has crashed")
        return self._stockfish.stdout.readline().strip()

class Engine:
    """
    Main engine of ChessAI, it connects to Stockfish.

    Raises:
        FileNotFoundError: Cannot find history.json file. For `move()` and `restart_engine()`.
    """

    current_move: int = 0

    def __init__(self, data):
        self.data = data

        self.engine: object = ModifiedStockfish(path=self.data['ChessAI']['Engine'],
                                                parameters={'UCI_LimitStrength': True})

        self.engine.update_engine_parameters(self.data['Stockfish'])

        with open(PROJECT_PATH / 'history.json', mode="w", encoding="utf-8") as write_file:
            data: dict = {
                '0': {
                    'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
                }
            }
            json.dump(data, write_file, indent=4)
            write_file.close()

    def restart_engine(self) -> None:
        """
        Automatically restart Stockfish when notified as crashed.

        Raises:
            FileNotFoundError: Cannot find history.json file.
        """
        # exit if not crashed.
        if not self.engine.crashed:
            return

        self.engine = ModifiedStockfish(self.data['ChessAI']['Engine'],
                                        parameters={'UCI_LimitStrength': True})

        self.engine.update_engine_parameters(self.data['Stockfish'])

        try:
            with open(PROJECT_PATH / 'history.json', mode="r", encoding="utf-8") as read_file:
                data: dict = json.load(read_file)
                read_file.close()
        except FileNotFoundError as err:
            raise FileNotFoundError('Cannot access history.json file') from err

        if len(data) == 1:
            self.engine.set_fen_position(data['0']['fen'])
        else:
            self.engine.set_fen_position(data[str(len(data) - 2)]['fen'])

        print('Complete restart Stockfish. Used the previous position.')


    def get_stats(self) -> dict:
        """
        Get current evaluation.

        Returns:
            dict: the evaluation.
        """
        self.restart_engine()

        return self.engine.get_evaluation()

    def get_top_moves(self) -> tuple[str]:
        """
        Get 2 best moves.

        Returns:
            tuple[str]: tuple of best move.
        """
        self.restart_engine()

        top1, top2, *etc = self.engine.get_top_moves(2)
        del etc # if something goes wrong.

        return (top1['Move'], top2['Move'])

    def settings(self, parameters: dict | None) -> None:
        """
        Update the engine's setting.

        Args:
            parameters (dict | None): the parameters of Stockfish.
        """
        self.restart_engine()

        self.engine.update_engine_parameters(parameters)

    def set_elo(self, elo: int=1350) -> None:
        """
        Set the elo playing as.

        Args:
            elo (int, optional): min goes 1320, max goes 3190. Defaults to 1350.
        """
        self.restart_engine()

        self.engine.set_elo_rating(elo)

    def get_fen(self) -> str:
        """
        Get current FEN position.

        Returns:
            str: the FEN.
        """
        self.restart_engine()

        return self.engine.get_fen_position()

    def check_valid(self, fen: str) -> bool:
        """
        Check if the FEN is valid or not.

        Args:
            fen (str): the FEN.

        Returns:
            bool: True if the FEN is valid.
        """
        self.restart_engine()

        return self.engine.is_fen_valid(fen=fen)

    def check_move(self, move: str) -> bool:
        """
        Check if move is possible.

        Args:
            move (str): the move, format by `{current}{moved}` (eg: e2e4).

        Returns:
            bool: True if possible.
        """
        self.restart_engine()

        # for Stockfish 16 and below:
        if not self.engine.is_move_correct(move):
            return False

        # for Stockfish 17+ (it skips errors)
        fen = self.get_fen()
        self.engine.make_moves_from_current_position(move)
        if fen == self.get_fen():
            return False
        self.engine.set_fen_position(fen)
        return True

    def move(self, move: str) -> None:
        """
        Move the piece.

        Args:
            move (str): the move, format by `{current}{moved}` (eg: e2e4).

        Raises:
            FileNotFoundError: Cannot find history.json file.
        """
        self.restart_engine()

        self.engine.make_moves_from_current_position(move)
        self.current_move += 1
        try:
            with open(PROJECT_PATH / 'history.json', mode="r", encoding="utf-8") as read_file:
                existed_data: dict = json.load(read_file)
                read_file.close()
        except FileNotFoundError as err:
            raise FileNotFoundError('Cannot access history.json file') from err

        data: dict = {
            str(self.current_move): {
                "fen": self.get_fen()
            }
        }

        # remove the other multi-universe your created
        for _id in range(self.current_move, len(existed_data)):
            existed_data.pop(str(_id))

        existed_data.update(data)

        with open(PROJECT_PATH / 'history.json', mode="w", encoding="utf-8") as write_file:
            json.dump(existed_data, write_file, indent=4)
            write_file.close()

if __name__ == '__main__':
    pass
