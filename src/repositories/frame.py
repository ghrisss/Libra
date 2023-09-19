import shelve

from src.configs import DB_CONFIG
from src.models.frame import Frame


class FrameRepository():
    
    # ?: atualmente, o pacote shelve não está conseguindo criar arquivos, a solução que 
    # ? implementei foi a de EU mesmo criar o arquivo que deveria ser criado, nesse caso 
    # ? 'frame.shelve'
    # ?: naquele endereço aqui em baixo. Teria de ser verificado o porquê o usuário 
    # ? consegue e o python não, se for algo de permissões diferentes entre ambos ou coisa
    # ? do tipo
    db = shelve.open(
        f'created_files/data/{DB_CONFIG.get("FRAME_DB")}', writeback = True)
    db.update(db.items() or Frame.asDict())
    Frame.fromDict(**dict(db.items())) # busca do shelve e joga no model
    
    @classmethod
    def update(cls):
        cls.db.update(Frame.asDict()) # atualiza o shelve com base no que está no model
        return dict(cls.db.items())
