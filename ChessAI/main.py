from ChessGUI import ChessGUIApp
from stockfish.models import StockfishException
import json
import sys
import pathlib

PROJECT_PATH: str = pathlib.Path(__file__).parent

def main():
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
    except:
        print('Cannot find setting.json file. Start create new one. If the file existed but this is called. Try to make an issue on Github.')
        
        data: dict = {
            "ChessAI": {
                "Engine": "",
                "Analyse Every Move": False,
                "Elo": 1350,
            },             
            "Stockfish": {
                "Debug Log File": "",
                "UCI_Chess960": False,
                "Min Split Depth": 0,
                "Threads": 1,
                "Hash": 16,
            },
        }
        
        with open(path, mode="w", encoding="utf-8") as write_file:
            json.dump(data, write_file, indent=4)
            write_file.close()
            
    if data['ChessAI']['Engine'] == '':
        raise StockfishException('You did not add the Stockfish path yet.')
    
    app = ChessGUIApp(data)
    app.run()
    
if __name__ == '__main__':
    main()
