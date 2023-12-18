import shelve

from src.configs import DB_CONFIG
from src.models.frame import Frame
from src.controllers.files import FilesController


class FrameRepository():

    try:
        db = shelve.open(
            f'created_files/data/{DB_CONFIG.get("FRAME_DB")}', writeback = True)
    except FileNotFoundError:
        FilesController.transferFile(dir_name='data', file_name=f'{DB_CONFIG.get("FRAME_DB")}.dat')
        db = shelve.open(
            f'created_files/data/{DB_CONFIG.get("FRAME_DB")}', writeback = True)
    db.update(db.items() or Frame.asDict())
    Frame.fromDict(**dict(db.items())) # busca do shelve e joga no model
    
    @classmethod
    def update(cls):
        cls.db.update(Frame.asDict()) # atualiza o shelve com base no que está no model
        return dict(cls.db.items())
