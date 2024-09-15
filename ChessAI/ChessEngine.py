import pathlib
import json
from stockfish.models import Stockfish, StockfishException

PROJECT_PATH: str = pathlib.Path(__file__).parent
PROJECT_SETTING: str = PROJECT_PATH / 'setting.json'

class Engine:
    def __init__(self):
        try:
            with open(PROJECT_SETTING, mode="r", encoding="utf-8") as read_file:
                self.data = json.load(read_file)
                read_file.close()
        except:
            print('Cannot find setting.json file. Start create new one. If the file existed but this is called. Try to make an issue on Github.')
            
            self.data: dict = {
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
            
            with open(PROJECT_SETTING, mode="w", encoding="utf-8") as write_file:
                json.dump(self.data, write_file, indent=4)
                write_file.close()
                
        if self.data['ChessAI']['Engine'] == '':
            raise StockfishException('You did not add the Stockfish path yet.')
        
        self.engine: Stockfish = Stockfish(self.data['ChessAI']['Engine'], parameters={'UCI_LimitStrength': True})

        self.engine.update_engine_parameters(self.data['Stockfish'])

    def get_stats(self) -> dict:
        return self.engine.get_evaluation()
    
    def get_top_moves(self) -> tuple[str]:
        """
        Get 2 best moves.
        """
        
        moves: list[str]= []
        for move in self.engine.get_top_moves(2):
            moves.append(move['Move'])
        return moves
    
    def settings(self, parameters: dict | None) -> None:
        self.engine.update_engine_parameters(parameters)
        
    def set_elo(self, elo: int=1350) -> None:
        self.engine.set_elo_rating(elo)
        
    def get_FEN(self) -> str:
        return self.engine.get_fen_position()
        
    def check_valid(self, FEN: str) -> bool:
        return self.engine.is_fen_valid(fen=FEN)
    
    def check_move(self, move: str) -> bool:
        return self.engine.is_move_correct(move)
    
    def move(self, move: str) -> None:
        self.engine.make_moves_from_current_position(move)
        
if __name__ == '__main__':
    engine = Engine()
    engine.engine.set_fen_position(input('FEN: '))
    
    while True:
        print(engine.engine.get_board_visual())
        move = input('input: ')
        print(engine.check_move(move))
        engine.move([move])