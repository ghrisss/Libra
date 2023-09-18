from shutil import move
from pathlib import Path
from src.configs import DEBUG, FILES
from src.models.frame import Frame
from src.repositories.frame import FrameRepository

class FrameController():
    def __init__(cls) -> None:
        pass
    
    @classmethod
    def tranferFile(cls, dir_name, file_name):
        root_dir = FILES.get('ROOT_DIR')
        dst_path = f"{root_dir}\\created_files\\{dir_name}"
        Path(dst_path).mkdir(parents=True, exist_ok=True)
        try:
            move(f"{root_dir}\\{file_name}", f"{dst_path}\\{file_name}")
            if DEBUG:
                print(f'[FrameController] arquivo enviado para diretório {dir_name} localizado em {dst_path}')
        except Exception as e:
            print("[FrameController] ERRO: arquivo ou diretório não encontrado \n" +
                  f"[FrameController] Tentativa de envio de {root_dir} \n[FrameController]Tentou enviar para {dst_path}")

 
    def setFocusState(auto_case, lock_case):
        Frame.setFocus(auto_case, lock_case)
        FrameRepository.update()
        return Frame.getFocus()
    
    def getFocusState():
        pass
    
    def setExposureState(auto_case, lock_case):
        Frame.setExposure(auto_case, lock_case)
        FrameRepository.update()
        return Frame.getExposure()
    
    def getExposureState():
        pass
    
    def setWhiteBalanceState(auto_case, lock_case):
        Frame.setWhiteBalance(auto_case, lock_case)
        FrameRepository.update()
        return Frame.getExposure()
    
    def getWhiteBalanceState():
        pass
    
    def setCropState(case):
        Frame.setCropCase(case)
        FrameRepository.update()
        return Frame.getCropCase()
            
    def getCropState():
        pass