from json import dump
from os.path import exists

import depthai as dai

from src.configs import DEBUG, QUEUE_PARAMETERS
from src.controllers.frame import FrameController
from src.models.device import Device


class DeviceController():
    @classmethod
    def __init__(cls):
        cls.rgbOut = None
        cls.frameOut = None
        cls.controlIn = None
        cls.videoOut = None
        cls.configIn = None
        cls.ispOut = None


    @classmethod
    def setDevice(cls, pipeline):
        default_device = cls.getDefaultDevice()
        Device.setDevice(dai.Device(pipeline, default_device))
        '''-----------------------------------------'''
        '''             Crash verif.                '''
        if Device.device.hasCrashDump():
            crashDump = cls.device.getCrashDump()
            commitHash = crashDump.depthaiCommitHash
            deviceId = crashDump.deviceId

            json = crashDump.serializeToJson()
            
            i = -1
            while True:
                i += 1
                destPath = 'crashDump_' + str(i) + '_' + deviceId + '_' + commitHash + '.json'
                if exists(destPath):
                    continue

                with open(destPath, 'w', encoding='utf-8') as f:
                    dump(json, f, ensure_ascii=False, indent=4)
                    
                FrameController.tranferFile(dir_name='crash_dumps', file_name=destPath)

                print(f'[Crash] Crash dump found on your device! \n[Crash] Saved to {destPath} \n' +
                    '[Crash] Please report to developers!')
                break
        else:
            if DEBUG:
                print('-'*50)
                print('[Crash] There was no crash dump found on your device!')
        '''-----------------------------------------------------'''
            
        if DEBUG:
            print('-'*50)
            print(f'[DeviceController] Informações do dispositivo: {Device.device.getDeviceInfo()} \n' +
                f'[DeviceController] Dispositivo com pipeline rodando? {Device.device.isPipelineRunning()}')
            
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
                print('[DeviceSetup] Dispositivo OAK Encontrado, realizando escolha de dispositivo padrão \n' +
                      '[DeviceSetup] Dispositivo Padrão escolhido: ', defaultDeviceID)
            if defaultDeviceID is None:
                defaultDeviceID = devices[0].getMxId()
                if DEBUG:
                    print('[DeviceSetup] Dispositivo não utiliza protocolo XLink USB VSC, adquirindo apenas o primeiro dispositivo \n'
                          '[DeviceSetup] Dispositivo Padrão escolhido: ', defaultDeviceID)
        defaultDevice = dai.DeviceInfo(defaultDeviceID)
        return defaultDevice


    @classmethod
    def setDataQueue(cls):
        runningDevice = Device.device
        for input_name in runningDevice.getInputQueueNames():
            match input_name:
                case 'control':
                    cls.controlIn = runningDevice.getInputQueue(
                        name=input_name, 
                        maxSize=QUEUE_PARAMETERS.get('QUEUE_SIZE'),
                        blocking = QUEUE_PARAMETERS.get('QUEUE_BLOCKING')
                        )
                case 'config':
                    cls.configIn = runningDevice.getInputQueue(
                        name=input_name, 
                        maxSize=QUEUE_PARAMETERS.get('QUEUE_SIZE'),
                        blocking = QUEUE_PARAMETERS.get('QUEUE_BLOCKING')
                        )
            
        for output_name in runningDevice.getOutputQueueNames():
            match output_name:
                case 'rgb':
                    cls.rgbOut = runningDevice.getOutputQueue(
                        name=output_name, 
                        maxSize=QUEUE_PARAMETERS.get('QUEUE_SIZE'),
                        blocking = QUEUE_PARAMETERS.get('QUEUE_BLOCKING')
                        )
                case 'frame':
                    cls.frameOut = runningDevice.getOutputQueue(
                        name=output_name, 
                        maxSize=QUEUE_PARAMETERS.get('QUEUE_SIZE'),
                        blocking = QUEUE_PARAMETERS.get('QUEUE_BLOCKING')
                        )
                case 'isp':
                    cls.ispOut = runningDevice.getOutputQueue(
                        name=output_name, 
                        maxSize=QUEUE_PARAMETERS.get('QUEUE_SIZE'),
                        blocking = QUEUE_PARAMETERS.get('QUEUE_BLOCKING')
                        )