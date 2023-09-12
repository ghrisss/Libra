import depthai as dai
from json import dump
from os.path import exists
from src.configs import QUEUE_PARAMETERS, DEBUG
from src.controllers.frame import FrameController


class DeviceController():
    @classmethod
    def __init__(cls):
        cls.device = None
        cls.rgbOut = None
        cls.frameOut = None
        cls.controlIn = None
        cls.videoOut = None
        cls.configIn = None
        cls.ispOut = None


    @classmethod
    def setDevice(cls, pipeline):
        default_device = cls.getDefaultDevice()
        cls.device = dai.Device(pipeline, default_device)
        '''-----------------------------------------'''
        '''             Crash verif.                '''
        if cls.device.hasCrashDump():
            crashDump = cls.device.getCrashDump()
            commitHash = crashDump.depthaiCommitHash
            deviceId = crashDump.deviceId

            json = crashDump.serializeToJson()
            
            i = -1
            while True:
                i += 1
                destPath = "crashDump_" + str(i) + "_" + deviceId + "_" + commitHash + ".json"
                if exists(destPath):
                    continue

                with open(destPath, 'w', encoding='utf-8') as f:
                    dump(json, f, ensure_ascii=False, indent=4)
                    
                FrameController.tranferFile(dir_name='crash_dumps', file_name=destPath)

                print("[Crash] Crash dump found on your device!")
                print(f"[Crash] Saved to {destPath}")
                print("[Crash] Please report to developers!")
                break
        else:
            if DEBUG:
                print('-'*50)
                print("[Crash] There was no crash dump found on your device!")
        '''-----------------------------------------------------'''
            
        if DEBUG:
            print('-'*50)
            print('[DeviceController] Informações do dispositivo: ', cls.device.getDeviceInfo())
            print('[DeviceController] Dispositivo com pipeline rodando? ', cls.device.isPipelineRunning())
            
        cls.setDataQueue()


    @classmethod
    def getDefaultDevice(cls):
        devices = dai.Device.getAllAvailableDevices()
        if DEBUG:
            print('-'*50)
            print('[DeviceSetup] Quantidade devices: ', len(devices))
        if len(devices) > 0:
            defaultDeviceID = next(map(
                lambda info: info.getMxId(),
                filter(lambda info: info.protocol == dai.XLinkProtocol.X_LINK_USB_VSC, devices)
            ), None)
            if DEBUG and defaultDeviceID is not None:
                print('[DeviceSetup] Dispositivo OAK Encontrado, realizando escolha de dispositivo padrão')
                print('[DeviceSetup] Dispositivo Padrão escolhido: ', defaultDeviceID)
            if defaultDeviceID is None:
                defaultDeviceID = devices[0].getMxId()
                if DEBUG:
                    print('[DeviceSetup] Dispositivo não utiliza protocolo XLink USB VSC, adquirindo apenas o primeiro dispositivo')
                    print('[DeviceSetup] Dispositivo Padrão escolhido: ', defaultDeviceID)
        defaultDevice = dai.DeviceInfo(defaultDeviceID)
        return defaultDevice


    @classmethod
    def setDataQueue(cls):
                
        for input_name in cls.device.getInputQueueNames():
            match input_name:
                case 'control':
                    cls.controlIn = cls.device.getInputQueue(
                        name=input_name, 
                        maxSize=QUEUE_PARAMETERS.get('QUEUE_SIZE'),
                        blocking = QUEUE_PARAMETERS.get('QUEUE_BLOCKING')
                        )
                case 'config':
                    cls.configIn = cls.device.getInputQueue(
                        name=input_name, 
                        maxSize=QUEUE_PARAMETERS.get('QUEUE_SIZE'),
                        blocking = QUEUE_PARAMETERS.get('QUEUE_BLOCKING')
                        )
            
        for output_name in cls.device.getOutputQueueNames():
            match output_name:
                case 'rgb':
                    cls.rgbOut = cls.device.getOutputQueue(
                        name=output_name, 
                        maxSize=QUEUE_PARAMETERS.get('QUEUE_SIZE'),
                        blocking = QUEUE_PARAMETERS.get('QUEUE_BLOCKING')
                        )
                case 'frame':
                    cls.frameOut = cls.device.getOutputQueue(
                        name=output_name, 
                        maxSize=QUEUE_PARAMETERS.get('QUEUE_SIZE'),
                        blocking = QUEUE_PARAMETERS.get('QUEUE_BLOCKING')
                        )
                case 'isp':
                    cls.ispOut = cls.device.getOutputQueue(
                        name=output_name, 
                        maxSize=QUEUE_PARAMETERS.get('QUEUE_SIZE'),
                        blocking = QUEUE_PARAMETERS.get('QUEUE_BLOCKING')
                        )

        
        # TODO: eventualmente, fazer com que o que está como cls. neste arquivo, seja os objetos dentro do deviceModel, 
        # as funções do controller sendo atribuídas pela decisão feita no job e nos models ter as funções de set e get