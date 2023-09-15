import depthai as dai

class Frame():
    
    # crop padrão
    crop_x= 0
    crop_y = 0
    send_cam_config = False
    
    # padrões e limites para controle de foco e exposição manual
    lens_posision = 150
    exposition_time = 20000
    sensor_iso = 800
    white_balance_manual = 4000
    auto_exposure_comp = 0
    auto_exposure_lock = False
    auto_wb_lock = False
    saturation = 0
    contrast = 0
    brightness = 0
    sharpness = 0
    luma_denoise = 0
    chroma_denoise = 0
    control = 'none'
    show = False
    
    auto_white_balance = []
    anti_banding_mode = []
    effect_mode = []
    
    
    def limit(num, v0, v1):
        return max(v0, min(num, v1))
    
    @classmethod
    def setShow(cls, case):
        cls.show = case
        return cls.show
    
    @classmethod
    def getShow(cls):
        return cls.show
    
    @classmethod
    def setCamConfig(cls, case):
        cls.send_cam_config = case
        return cls.send_cam_config
    
    @classmethod
    def getCamConfig(cls):
        return cls.send_cam_config
    
    @classmethod
    def setCropX(cls, crop):
        cls.crop_x = crop
        return cls.crop_x
    
    @classmethod
    def getCropX(cls):
        return cls.crop_x
    
    @classmethod
    def setCropY(cls, crop):
        cls.crop_y = crop
        return cls.crop_y
    
    @classmethod
    def getCropY(cls):
        return cls.crop_y
    
    
    
    @classmethod
    def setSaturation(cls, value):
        cls.saturation = value
        return cls.saturation
    
    @classmethod
    def getSaturation(cls):
        return cls.saturation
    
    @classmethod
    def setContrast(cls, value):
        cls.contrast = value
        return cls.contrast
    
    @classmethod
    def getContrast(cls):
        return cls.contrast
    
    @classmethod
    def setBrightness(cls, value):
        cls.brightness = value
        return cls.brightness
    
    @classmethod
    def getBrightness(cls):
        return cls.brightness
    
    @classmethod
    def setSharpness(cls, value):
        cls.sharpness = value
        return cls.sharpness
    
    @classmethod
    def getSharpness(cls):
        return cls.sharpness
    
    @classmethod
    def setLumaDenoise(cls, value):
        cls.luma_denoise = value
        return cls.luma_denoise
    
    @classmethod
    def getLumaDenoise(cls):
        return cls.luma_denoise
    
    @classmethod
    def setChromaDenoise(cls, value):
        cls.chroma_denoise = value
        return cls.chroma_denoise

    @classmethod
    def getChromaDenoise(cls):
        return cls.chroma_denoise

# TODO: ficaram salvas em uma pasta repositories com um shelve, que guarda os dados de cada objeto em um JSON