from stockfish.models import Stockfish

class Engine:
    def __init__(self, data):
        self.data = data
        
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
        # for Stockfish 16 and below:
        if not self.engine.is_move_correct(move):
            return False

        # for Stockfish 17+
        fen = self.get_FEN()
        self.move(move)
        if fen == self.get_FEN():
            return False
        self.engine.set_fen_position(fen)
        return True
    
    def move(self, move: str) -> None:
        self.engine.make_moves_from_current_position(move)
