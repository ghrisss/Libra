
class Device():
    
    useCamera = False
    colorCameraEnable = False
    rightCameraEnable = False
    leftCameraEnable = False
    videoEnable = False
    frameEnable = False
    draftEnable = False
    device = None
    
    @classmethod
    def setUseCamera(cls, case):
        cls.useCamera = case
        return cls.useCamera
    
    @classmethod
    def getUseCamera(cls):
        return cls.useCamera
    
    @classmethod
    def setColorCameraEnable(cls, case):
        cls.colorCameraEnable = case
        return cls.colorCameraEnable
    
    @classmethod
    def getColorCameraEnable(cls):
        return cls.colorCameraEnable
    
    @classmethod
    def setVideoEnable(cls, case):
        cls.videoEnable = case
        cls.frameEnable = False
        cls.draftEnable = False
        return cls.videoEnable
    
    @classmethod
    def getVideoEnable(cls):
        return cls.videoEnable
    
    @classmethod
    def setFrameEnable(cls, case):
        cls.frameEnable = case
        cls.videoEnable = False
        cls.draftEnable = False
        return cls.frameEnable
    
    @classmethod
    def getFrameEnable(cls):
        return cls.frameEnable
    
    @classmethod
    def setDraftEnable(cls, case):
        cls.draftEnable = case
        cls.videoEnable = False
        cls.frameEnable = False
        return cls.draftEnable
    
    @classmethod
    def getDraftEnable(cls):
        return cls.draftEnable
    
    @classmethod
    def setDevice(cls, selectedDevice):
        cls.device = selectedDevice
        return cls.device
    
    @classmethod
    def getDevice(cls):
        return cls.device