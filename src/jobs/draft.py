from itertools import cycle

import cv2
import depthai as dai

from src.configs import DEBUG, DRAFT
from src.controllers.device import DeviceController
from src.controllers.frame import FrameController
from src.models.frame import Frame
from src.repositories.frame import FrameRepository


class DraftJob():
    
    def run(self, rgb_node = None):
        Frame.auto_wb_mode = cycle([item for name, item in vars(dai.CameraControl.AutoWhiteBalanceMode).items() if name.isupper()])
        Frame.anti_banding_mode = cycle([item for name, item in vars(dai.CameraControl.AntiBandingMode).items() if name.isupper()])
        Frame.effect_mode = cycle([item for name, item in vars(dai.CameraControl.EffectMode).items() if name.isupper()])
        
        max_crop_x = (rgb_node.getIspWidth() - rgb_node.getVideoWidth()) / rgb_node.getIspWidth()
        max_crop_y = (rgb_node.getIspHeight() - rgb_node.getVideoHeight()) / rgb_node.getIspHeight()
        self.max_crop_x = max_crop_x
        self.max_crop_y = max_crop_y
        # print(max_crop_x, max_crop_y, rgb_node.getIspWidth(), rgb_node.getVideoHeight())
        
        FrameController.getImageSetting()
        
        self.help()
        
        while True:
            colorFrames = DeviceController.rgbOut.tryGetAll() # metodo tryGetAll(): tenta recuperar TODAS as mensagens na queue
            for frame in colorFrames:
                frame = frame.getCvFrame()
                # frame = cv2.pyrDown(frame)
                cv2.imshow('configuração de parâmetros', frame)
                
            ispFrames = DeviceController.ispOut.tryGetAll()
            for frame in ispFrames:
                # frame_number = frame.getSequenceNum()
                if Frame.getShow():
                    txt = f"Exposure: {frame.getExposureTime().total_seconds()*1000:.3f} ms, "
                    txt += f"ISO: {frame.getSensitivity()}, "
                    txt += f"Lens position: {frame.getLensPosition()}, "
                    txt += f"Color temp: {frame.getColorTemperature()} K"
                    print(txt)
                    Frame.setShow(False)
                # frame = frame.getCvFrame()
                # # frame = cv2.pyrDown(frame)
                # cv2.imshow('isp', frame)
            
            if Frame.getCamConfig():
                print('dentro do config', Frame.crop_x, Frame.crop_y)
                crop_image = dai.ImageManipConfig()
                crop_image.setCropRect(Frame.crop_x, Frame.crop_y, 0, 0)
                DeviceController.configIn.send(crop_image)
                if DEBUG:
                    print(f"Configuring new image crop: -x {Frame.crop_x} -y {Frame.crop_y}")
                Frame.setCamConfig(False)
                
            key = cv2.waitKey(1)
            
            if key in (ord('q'), ord('Q')):
                break
            
            elif key == ord('/'):
                Frame.setShow(True)
                print('-'*160)
                print("Printing camera settings")
                
            elif key == ord('\t'):
                self.resetParams()
                print('Reseting all Parameters')
                    
            elif key in (ord('t'), ord('T')):
                print('Autofocus trigger, single focus')
                ctrl = dai.CameraControl()
                ctrl.setAutoFocusMode(dai.CameraControl.AutoFocusMode.AUTO)
                ctrl.setAutoFocusTrigger()
                FrameController.setFocusState(auto_case=True, lock_case=False)
                DeviceController.controlIn.send(ctrl)
                
            elif key in (ord('f'), ord('F')):
                print('Autofocus trigger, continuous focus')
                ctrl = dai.CameraControl()
                ctrl.setAutoFocusMode(dai.CameraControl.AutoFocusMode.CONTINUOUS_VIDEO)
                ctrl.setAutoFocusTrigger()
                FrameController.setFocusState(auto_case=True, lock_case=True)
                DeviceController.controlIn.send(ctrl)
                
            elif key in (ord('e'), ord('E')):
                print('Autoexposure enable')
                ctrl = dai.CameraControl()
                ctrl.setAutoExposureEnable()
                FrameController.setExposureState(auto_case=True, lock_case=False)
                DeviceController.controlIn.send(ctrl)
                
            elif key in (ord('b'), ord ('B')):
                print('Auto white-balance enable')
                ctrl = dai.CameraControl()
                ctrl.setAutoWhiteBalanceMode(dai.CameraControl.AutoWhiteBalanceMode.AUTO)
                FrameController.setWhiteBalanceState(auto_case=True, lock_case=False)
                DeviceController.controlIn.send(ctrl)
                '''
            # TODO: 
            a ideia para otimizar os acessos a outros arquivos .py é a de ter uma variável nesse arquivo, que é modificada a cada loop, no caso abaixo a variável 'lens_position'
            e outra variável separada no FrameModel, e a cada tempo sem mudança na variável deste arquivo, ou a cada tempo é feita uma verificação no arquivo model é feito tanto
            a atualização da variável no FrameModel como também é atribuido oo case para as variáveis de estado (lock, exposition...) e consequentemente o repositório''' 
            elif key in [ord(','), ord('.')]:
                if key == ord(','): Frame.lens_posision -= DRAFT.get('LENS_STEP')
                elif key == ord('.'): Frame.lens_posision += DRAFT.get('LENS_STEP')
                Frame.lens_posision = Frame.limit(Frame.lens_posision, 0, 255)
                print("Setting manual focus, lens position: ", Frame.lens_posision)
                ctrl = dai.CameraControl()
                ctrl.setManualFocus(Frame.lens_posision)
                FrameController.setFocusState(auto_case=False, lock_case=False)
                DeviceController.controlIn.send(ctrl)
                
            elif key in [ord('i'), ord('o'), ord('k'), ord('l'), ord('I'), ord('O'), ord('K'), ord('L')]:
                if key in (ord('i'), ord('I')): Frame.exposition_time -= DRAFT.get('EXP_STEP')
                if key in (ord('o'), ord('O')): Frame.exposition_time += DRAFT.get('EXP_STEP')
                if key in (ord('k'), ord('K')): Frame.sensor_iso -= DRAFT.get('ISO_STEP')
                if key in (ord('l'), ord('L')): Frame.sensor_iso += DRAFT.get('ISO_STEP')
                Frame.exposition_time = Frame.limit(Frame.exposition_time, 1, 33000)
                Frame.sensor_iso = Frame.limit(Frame.sensor_iso, 100, 1600)
                print("Setting manual exposure, time: ", Frame.exposition_time, "iso: ", Frame.sensor_iso)
                ctrl = dai.CameraControl()
                ctrl.setManualExposure(Frame.exposition_time, Frame.sensor_iso)
                FrameController.setExposureState(auto_case=False, lock_case=False)
                DeviceController.controlIn.send(ctrl)
                
            elif key in [ord('n'), ord('m'), ord('N'), ord('M')]:
                if key in (ord('n'), ord('N')): Frame.white_balance_manual -= DRAFT.get('WB_STEP')
                if key in (ord('m'), ord('M')): Frame.white_balance_manual += DRAFT.get('WB_STEP')
                Frame.white_balance_manual = Frame.limit(Frame.white_balance_manual, 1000, 12000)
                print("Setting manual white balance, temperature: ", Frame.white_balance_manual, "K")
                ctrl = dai.CameraControl()
                ctrl.setManualWhiteBalance(Frame.white_balance_manual)
                FrameController.setWhiteBalanceState(auto_case=False, lock_case=False)
                DeviceController.controlIn.send(ctrl)
                '''
                # TODO:
                talvez com a ideia de atualizar o model e o repositório com base em tempo, para não exigir tanto processamento, possa ser necessário refatorar funções como a de baixo
                que se comunicam diretamente com o FrameModel para atualizar os valores
                '''
            elif key in [ord('w'), ord('a'), ord('s'), ord('d'), ord('W'), ord('A'), ord('S'), ord('D')]:
                if key in (ord('a'), ord('A')):
                    crop_x = Frame.getCropX() - (max_crop_x / rgb_node.getResolutionWidth()) * DRAFT.get('STEP_SIZE')
                    crop_x = crop_x if crop_x >= 0 else 0
                    Frame.setCropX(crop_x)
                elif key in (ord('d'), ord('D')):
                    crop_x = Frame.getCropX() + (max_crop_x / rgb_node.getResolutionWidth()) * DRAFT.get('STEP_SIZE')
                    crop_x = crop_x if crop_x <= max_crop_x else max_crop_x
                    Frame.setCropX(crop_x)
                elif key in (ord('w'), ord('W')):
                    crop_y = Frame.getCropY() - (max_crop_y / rgb_node.getResolutionHeight()) * DRAFT.get('STEP_SIZE')
                    crop_y = crop_y if crop_y >= 0 else 0
                    Frame.setCropY(crop_y)
                elif key in (ord('s'), ord('S')):
                    crop_y = Frame.getCropY() + (max_crop_y / rgb_node.getResolutionHeight()) * DRAFT.get('STEP_SIZE')
                    crop_y = crop_y if crop_y <= max_crop_y else max_crop_y
                    Frame.setCropY(crop_y)
                FrameRepository.update()
                Frame.setCamConfig(True)
                
            elif key in (ord('z'), ord('Z')):
                Frame.auto_wb_lock = not Frame.auto_wb_lock
                print("Auto white balance lock:", Frame.auto_wb_lock)
                ctrl = dai.CameraControl()
                ctrl.setAutoWhiteBalanceLock(Frame.auto_wb_lock)
                FrameController.setWhiteBalanceState(auto_case=True, lock_case=True)
                DeviceController.controlIn.send(ctrl)
                
            elif key in (ord('x'), ord('X')):
                Frame.auto_exposure_lock = not Frame.auto_exposure_lock
                print("Auto exposure lock:", Frame.auto_exposure_lock)
                ctrl = dai.CameraControl()
                ctrl.setAutoExposureLock(Frame.auto_exposure_lock)
                FrameController.setExposureState(auto_case=True, lock_case=True)
                DeviceController.controlIn.send(ctrl)
            
            elif key in (ord('h'), ord('H')):
                self.help()
                
            elif key >= 0 and chr(key) in '0123456789':
                if   key == ord('1'): Frame.control = 'auto_wb_mode'
                elif key == ord('2'): Frame.control = 'auto_exposure_comp'
                elif key == ord('3'): Frame.control = 'anti_banding_mode'
                elif key == ord('4'): Frame.control = 'effect_mode'
                elif key == ord('5'): Frame.control = 'brightness'
                elif key == ord('6'): Frame.control = 'contrast'
                elif key == ord('7'): Frame.control = 'saturation'
                elif key == ord('8'): Frame.control = 'sharpness'
                elif key == ord('9'): Frame.control = 'luma_denoise'
                elif key == ord('0'): Frame.control = 'chroma_denoise'
                pass
            
            elif key in [ord('-'), ord('_'), ord('='), ord('+')]:
                change = 0
                if key in [ord('-'), ord('_')]: change = -1
                if key in [ord('='), ord('+')]: change = 1
                ctrl = dai.CameraControl()
                
                if Frame.control == 'none':
                    print('Please select a control mode to change through numerical keys "0" to "9"')
                    
                elif Frame.control == 'auto_exposure_comp':
                    Frame.auto_exposure_comp = Frame.limit((Frame.auto_exposure_comp+change), -9, 9)
                    print("Auto exposure compensation: ", Frame.auto_exposure_comp)
                    ctrl.setAutoExposureCompensation(Frame.auto_exposure_comp)
                    
                elif Frame.control == 'anti_banding_mode':
                    abm = next(Frame.anti_banding_mode)
                    print('Anti banding mode: ', abm)
                    ctrl.setAntiBandingMode(abm)
                    
                elif Frame.control == 'auto_wb_mode':
                    awb = next(Frame.auto_wb_mode)
                    print('Auto white balance mode: ', awb)
                    ctrl.setAutoWhiteBalanceMode(awb)
                    
                elif Frame.control == 'effect_mode':
                    eff = next(Frame.effect_mode)
                    print("Effect mode", eff)
                    ctrl.setEffectMode(eff)
                    
                elif Frame.control == 'brightness':
                    brightness = Frame.limit((Frame.getBrightness() + change), -10, 10)
                    Frame.setBrightness(brightness)
                    ctrl.setBrightness(brightness)
                    FrameRepository.update()
                     
                elif Frame.control == 'contrast':
                    contrast = Frame.limit((Frame.getContrast() + change), -10, 10)
                    Frame.setContrast(contrast)
                    ctrl.setContrast(contrast)
                    FrameRepository.update()
                    
                elif Frame.control == 'saturation':
                    saturation = Frame.limit((Frame.getSaturation() + change), -10, 10)
                    Frame.setSaturation(saturation)
                    ctrl.setSaturation(saturation)
                    FrameRepository.update()
                    
                elif Frame.control == 'sharpness':
                    sharpness = Frame.limit((Frame.getSharpness() + change), 0, 4)
                    Frame.setSharpness(sharpness)
                    ctrl.setSharpness(sharpness)
                    FrameRepository.update()
                    
                elif Frame.control == 'luma_denoise':
                    luma_denoise = Frame.limit((Frame.getLumaDenoise() + change), 0, 4)
                    Frame.setLumaDenoise(luma_denoise)
                    ctrl.setLumaDenoise(luma_denoise)
                    FrameRepository.update()
                    
                elif Frame.control == 'chroma_denoise':
                    chroma_denoise = Frame.limit((Frame.getChromaDenoise() + change), 0, 4)
                    Frame.setChromaDenoise(chroma_denoise)
                    ctrl.setChromaDenoise(chroma_denoise)
                    FrameRepository.update()
                    
                DeviceController.controlIn.send(ctrl)
    
    def help(self):
        print('-'*160)
        txt = "     ---     Configuração da câmera      ---     \n"
        txt += "Região de interesse: 'W','A','S','D' para determinar a posição do processamento \n"
        txt +="Foco: 'T' para disparar o autofoco, 'F' para manter o autofoco ativado continuamente \n"
        txt +="Foco: ',' e '.' para calibrar a posição da lente manualmente \n"
        txt += "Tempo de exposição: 'E' para ativar a calibração automática, 'X' pode ser travado no modo automático \n"
        txt += "Tempo de exposição: 'I' e 'O' para alterar manualmente, 'K' e 'L' para alterar a sensibilidade da ISO \n"
        txt += "Balanço de branco: 'B' para ajuste automático, 'N' e 'M' para alteração manual \n"
        txt += "Balanço de branco: 'Z' para travar modo automático"
        print(txt)
        print('-'*160)
        txt = "Utilize os outros comandos através do teclado numerico: \n"
        txt += "'1' -> Auto White-Balance mode (Incandescnet, fluorescent, daylight, twilight, shade, etc...) \n"
        txt += "'2' -> Auto Exposure compensation \n"
        txt +="'3' -> anti-banding/flicker mode \n"
        txt += "'4' -> effect mode (Monochromatic, negative, solarize, sepia, aqua, etc...) \n"
        txt += "'5' -> brightness \n"
        txt += "'6' -> contrast \n"
        txt += "'7' -> saturation \n"
        txt += "'8' -> sharpness \n"
        txt += "'9' -> luma denoise \n"
        txt += "'0' -> chroma denoise \n"
        txt += "Ao utilizar os comandos do teclado numérico, utilize as teclas '+' e '-' para alterar os valores"
        print(txt)
        print('-'*160)
        print("Pressione '/' para mostrar as configurações atuais de: tempo de exposição, ISO, posição da lente, e temperatura de cor")
        print("Pressione 'Tab' para retornar as configurações iniciais/padrões")
    
    def resetParams(self):
        # focus
        ctrl = dai.CameraControl()
        ctrl.setAutoFocusTrigger()
        ctrl.setAutoFocusMode(dai.CameraControl.AutoFocusMode.CONTINUOUS_VIDEO)
        DeviceController.controlIn.send(ctrl)
            
        # exposure
        ctrl = dai.CameraControl()
        ctrl.setAutoExposureEnable()
        DeviceController.controlIn.send(ctrl)
        
        # white_balance
        ctrl = dai.CameraControl()
        ctrl.setAutoWhiteBalanceMode(dai.CameraControl.AutoWhiteBalanceMode.AUTO)
        DeviceController.controlIn.send(ctrl)
                
        # crop
        crop_image = dai.ImageManipConfig()
        crop_image.setCropRect(self.max_crop_x, self.max_crop_y, 0, 0)
        DeviceController.configIn.send(crop_image)

        # saturation
        ctrl.setSaturation(0)
        # contrast
        ctrl.setContrast(0)
        # brightness
        ctrl.setBrightness(0)
        # sharpness
        ctrl.setSharpness(0)
        # luma_denoise
        ctrl.setLumaDenoise(0)
        # chroma_denoise
        ctrl.setChromaDenoise(0)
        DeviceController.controlIn.send(ctrl)
        
        # reseta os valores do model
        Frame.resetValues()
        FrameRepository.update()
        
    def cropPreview(self):
        while True:
            
            colorFrames = DeviceController.rgbOut.get()
            cv2.imshow("[Configurando Crop] aperte Q para sair e confirmar o tamanho do recorte", colorFrames.getCvFrame())
            
            key = cv2.waitKey(1)
            if key in (ord('q'), ord('Q')):
                cv2.destroyAllWindows()
                break