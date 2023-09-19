
from pathlib import Path
from shutil import move

from src.configs import DEBUG

class FilesController():
    
    @classmethod
    def transferFile(cls, dir_name, file_name):
        root_dir = Path(__file__).parent.parent.parent
        dst_path = f"{root_dir}\\created_files\\{dir_name}"
        Path(dst_path).mkdir(parents=True, exist_ok=True)
        try:
            move(f"{root_dir}\\{file_name}", f"{dst_path}\\{file_name}")
            if DEBUG:
                print(f'[FrameController] arquivo enviado para diretório {dir_name} localizado em {dst_path}')
        except Exception as e:
            print("[FrameController] ERRO: arquivo ou diretório não encontrado \n" +
                  f"[FrameController] Tentativa de envio de {root_dir} \n[FrameController]Tentou enviar para {dst_path}")