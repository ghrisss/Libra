from shutil import move
from pathlib import Path
from src.configs import DEBUG

class FrameController():
    def __init__(cls) -> None:
        pass
    
    @classmethod
    def tranferFile(cls, dir_name, file_name):
        dir_path = f"C:\\Users\\henriquebf\\Luxonis\\Balanceador\\{dir_name}"
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        root_dir = Path(__file__).parent.parent.parent
        try:
            move(f"{root_dir}\\{file_name}", f"{dir_path}\\{file_name}")
            if DEBUG:
                print(f'[FrameController] arquivo enviado para diretório {dir_name}')
        except Exception as e:
            print("[FrameController] ERRO: arquivo ou diretório não encontrado")
            print(f"[FrameController] Tentativa de envio de {root_dir}")
            print(f"[FrameController]Tentou enviar para {dir_path}")