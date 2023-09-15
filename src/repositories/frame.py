import shelve
from src.models.frame import Frame
from src.configs import DB_CONFIG

class FrameRepository():
    
    db = shelve.open(f'data/{DB_CONFIG.get("FRAME_DB")}', writeback = True)
    db.update(db.items() or Frame.asDict())
    Frame.fromDict(**dict(db.items())) # busca do shelve e joga no model
    
    @classmethod
    def update(cls):
        cls.db.update(Frame.asDict()) # atualiza o shelve com base no que está no model
        return dict(cls.db.items())