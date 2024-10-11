from stockfish.models import Stockfish, StockfishException
import json
import pathlib

PROJECT_PATH: str = pathlib.Path(__file__).parent

# R.I.P the legend himself o7
class ModifiedStockfish(Stockfish):
    crashed: bool = False
    
    def _put(self, command: str) -> None:
        if not self._stockfish.stdin:
            raise BrokenPipeError()
        if self._stockfish.poll() is None and not self._has_quit_command_been_sent:
            # My code:
            print(command)
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
    current_move: int = 0
    
    def __init__(self, data):
        self.data = data
        
        self.engine: object = ModifiedStockfish(self.data['ChessAI']['Engine'], parameters={'UCI_LimitStrength': True})

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
        if not self.engine.crashed:
            return
        
        self.engine = ModifiedStockfish(self.data['ChessAI']['Engine'], parameters={'UCI_LimitStrength': True})
        
        self.engine.update_engine_parameters(self.data['Stockfish'])
        
        with open(PROJECT_PATH / 'history.json', mode="r", encoding="utf-8") as read_file:
            data: dict = json.load(read_file)
            read_file.close()
            
        self.engine.set_fen_position(data[str(len(data) - 1)]['fen'])
        
        print('Complete restart Stockfish.')
        

    def get_stats(self) -> dict:
        self.restart_engine()
        
        return self.engine.get_evaluation()
    
    def get_top_moves(self) -> tuple[str]:
        """
        Get 2 best moves.
        """
        self.restart_engine()
        
        moves: list[str]= []
        for move in self.engine.get_top_moves(2):
            moves.append(move['Move'])
        return moves
    
    def settings(self, parameters: dict | None) -> None:
        self.restart_engine()
        
        self.engine.update_engine_parameters(parameters)
        
    def set_elo(self, elo: int=1350) -> None:
        self.restart_engine()
        
        self.engine.set_elo_rating(elo)
        
    def get_FEN(self) -> str:
        self.restart_engine()
        
        return self.engine.get_fen_position()
        
    def check_valid(self, FEN: str) -> bool:
        self.restart_engine()
        
        return self.engine.is_fen_valid(fen=FEN)
    
    def check_move(self, move: str) -> bool:
        self.restart_engine()
        
        # for Stockfish 16 and below:
        if not self.engine.is_move_correct(move):
            return False

        # for Stockfish 17+
        fen = self.get_FEN()
        self.engine.make_moves_from_current_position(move)
        if fen == self.get_FEN():
            return False
        self.engine.set_fen_position(fen)
        return True
    
    def move(self, move: str) -> None:
        self.restart_engine()
        
        self.engine.make_moves_from_current_position(move)
        self.current_move += 1
        try:
            with open(PROJECT_PATH / 'history.json', mode="r", encoding="utf-8") as read_file:
                existed_data: dict = json.load(read_file)
                read_file.close()
        except:
            raise Exception('Cannot access history.json file')
        
        data: dict = {
            str(self.current_move): {
                "fen": self.get_FEN()
            }
        }
        
        # remove the other multi-universe your created
        for id in range(self.current_move, len(existed_data)):
            existed_data.pop(str(id))
        
        existed_data.update(data)
        
        with open(PROJECT_PATH / 'history.json', mode="w", encoding="utf-8") as write_file:
            json.dump(existed_data, write_file, indent=4)
            write_file.close()

if __name__ == '__main__':
    print('Use "main.py" dude')
