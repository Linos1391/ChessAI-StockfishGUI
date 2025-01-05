"""Main code of ChessAI."""

import json
import sys
import pathlib

from stockfish.models import StockfishException

from .gui import ChessAIApp

PROJECT_PATH: str = pathlib.Path(__file__).parent

def main():
    """
    Run the main code.

    Raises:
        StockfishException: user did not add stockfish path yet.
    """
    if getattr(sys, "frozen", False):
        # If the 'frozen' flag is set, we are in bundled-app mode.
        path = 'setting.json'
    else:
        # Normal development mode. Use os.getcwd() or __file__ as appropriate in your case...
        path = PROJECT_PATH / 'setting.json'

    try:
        with open(path, mode="r", encoding="utf-8") as read_file:
            data = json.load(read_file)
            read_file.close()
    except FileNotFoundError:
        print('Cannot find setting.json file. Start create new one.')

        data: dict = {
            "ChessAI": {
                "Engine": "",
                "Analyse Every Move": False,
                "Elo": 1350,
                "Current Template": "",
            },
            "Stockfish": {
                "Debug Log File": "",
                "UCI_Chess960": False,
                "Min Split Depth": 0,
                "Threads": 1,
                "Hash": 16,
            },
        }

    if data['ChessAI']['Engine'] == '':
        stockfish_path = input('Please paste in path to stockfish:\n>>')
        if stockfish_path == '':
            raise StockfishException('You did not add the Stockfish path yet.')

        data['ChessAI']['Engine'] = stockfish_path

        with open(path, mode="w", encoding="utf-8") as write_file:
            json.dump(data, write_file, indent=4)
            write_file.close()

    app = ChessAIApp(data)
    app.run()

if __name__ == '__main__':
    main()
