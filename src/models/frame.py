
class Frame():
    
    # crop padrão
    crop_x: float = 0.0
    crop_y: float = 0.0
    
    # padrões e limites para controle de foco e exposição manual
    lens_posision: int = 150
    exposition_time: int = 5000
    sensor_iso: int = 800
    white_balance_manual: int = 4000

    control: str = 'none'
    auto_exposure_comp: int = 0
    saturation: int = 0
    contrast: int = 0
    brightness: int = 0
    sharpness: int = 0
    luma_denoise: int = 0
    chroma_denoise: int = 0
    
    send_cam_config: bool = False
    show: bool = False
    auto_focus: bool = True
    auto_exposure: bool = True
    auto_white_balance: bool = True
    crop: bool = False
    aspect_ratio: list = None
    continuous_focus: bool = True
    auto_exposure_lock: bool = False
    auto_wb_lock: bool = False
    
    auto_wb_mode: list = []
    anti_banding_mode: list = []
    effect_mode: list = []
    
    @classmethod
    def __init__(cls,
        crop_x = 0, crop_y = 0, lens_posision: int = 150, exposition_time: int = 5000,
        sensor_iso: int = 800, white_balance_manual: int = 4000, control: str = 'none',
        auto_exposure_comp: int = 0, saturation: int = 0, contrast: int = 0, brightness: int = 0, 
        sharpness: int = 0, luma_denoise: int = 0, chroma_denoise: int = 0, send_cam_config: bool = False, 
        show: bool = False, auto_focus: bool = True, auto_exposure: bool = True, auto_white_balance: bool = True, 
        crop: bool = False, aspect_ratio: list = None, continuous_focus: bool = True, auto_exposure_lock: bool = False, 
        auto_wb_lock: bool = False, auto_wb_mode: list = [], anti_banding_mode: list = [], effect_mode: list = []
    ):
        cls.crop_x = crop_x
        cls.crop_y = crop_y
        cls.lens_posision = lens_posision
        cls.exposition_time = exposition_time
        cls.sensor_iso = sensor_iso
        cls.white_balance_manual = white_balance_manual
        cls.control = control
        cls.auto_exposure_comp = auto_exposure_comp
        cls.saturation = saturation
        cls.contrast = contrast
        cls.brightness = brightness
        cls.sharpness = sharpness
        cls.luma_denoise = luma_denoise
        cls.chroma_denoise = chroma_denoise
        cls.send_cam_config = send_cam_config
        cls.show = show
        cls.auto_focus = auto_focus
        cls.auto_exposure = auto_exposure
        cls.auto_white_balance = auto_white_balance
        cls.crop = crop
        cls.aspect_ratio = aspect_ratio
        cls.continuous_focus = continuous_focus
        cls.auto_exposure_lock = auto_exposure_lock
        cls.auto_wb_lock = auto_wb_lock
        cls.auto_wb_mode = auto_wb_mode
        cls.anti_banding_mode = anti_banding_mode
        cls.effect_mode = effect_mode
        
    @classmethod
    def asDict(cls):
        return {
            '_crop_x': cls.crop_x,
            '_crop_y': cls.crop_y,
            '_lens_position': cls.lens_posision,
            '_exposition_time': cls.exposition_time,
            '_sensor_iso': cls.sensor_iso,
            '_white_balance_manual': cls.white_balance_manual,
            # '_control' : cls.control,
            '_auto_exposure_comp' : cls.auto_exposure_comp,
            '_saturation' : cls.saturation,
            '_contrast' : cls.contrast,
            '_brightness' : cls.brightness,
            '_sharpness' : cls.sharpness,
            '_luma_denoise' : cls.luma_denoise,
            '_chroma_denoise' : cls.chroma_denoise,
            # '_send_cam_config' : cls.send_cam_config,
            # '_show' : cls.show,
            '_auto_focus' : cls.auto_focus,
            '_auto_exposure' : cls.auto_exposure,
            '_auto_white_balance' : cls.auto_white_balance,
            '_crop' : cls.crop,
            '_continuous_focus' : cls.continuous_focus,
            '_auto_exposure_lock' : cls.auto_exposure_lock,
            '_auto_wb_lock' : cls.auto_wb_lock,
            # '_auto_wb_mode' : cls.auto_wb_mode,
            # '_anti_banding_mode' : cls.anti_banding_mode,
            # '_effect_mode' : cls.effect_mode,
        }
    
    @classmethod
    def fromDict(
        cls,
        _crop_x = 0,
        _crop_y = 0,
        _lens_position = 150,
        _exposition_time = 5000,
        _sensor_iso = 800,
        _white_balance_manual = 4000,
        # _control = 'none',
        _auto_exposure_comp = 0,
        _saturation = 0,
        _contrast = 0,
        _brightness = 0,
        _sharpness = 0,
        _luma_denoise = 0,
        _chroma_denoise = 0,
        # _send_cam_config = False,
        # _show = False,
        _auto_focus = True,
        _auto_exposure = True,
        _auto_white_balance = True,
        _crop = False,
        _continuous_focus = True,
        _auto_exposure_lock = False,
        _auto_wb_lock = False,
        # _auto_wb_mode = [],
        # _anti_banding_mode = [],
        # _effect_mode = [],
    ):
        cls.crop_x = _crop_x
        cls.crop_y = _crop_y
        cls.lens_posision = _lens_position
        cls.exposition_time = _exposition_time
        cls.sensor_iso = _sensor_iso
        cls.white_balance_manual = _white_balance_manual
        # cls.control = _control
        cls.auto_exposure_comp = _auto_exposure_comp
        cls.saturation = _saturation
        cls.contrast = _contrast
        cls.brightness = _brightness
        cls.sharpness = _sharpness
        cls.luma_denoise = _luma_denoise
        cls.chroma_denoise = _chroma_denoise
        # cls.send_cam_config = _send_cam_config
        # cls.show = _show
        cls.auto_focus = _auto_focus
        cls.auto_exposure = _auto_exposure
        cls.auto_white_balance = _auto_white_balance
        cls.crop = _crop
        cls.continuous_focus = _continuous_focus
        cls.auto_exposure_lock = _auto_exposure_lock
        cls.auto_wb_lock = _auto_wb_lock
        # cls.auto_wb_mode = _auto_wb_mode
        # cls.anti_banding_mode = _anti_banding_mode
        # cls.effect_mode = _effect_mode
    
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
    def setFocus(cls, case, lock_case):
        cls.auto_focus = case
        cls.continuous_focus = lock_case
        return cls.auto_focus
    
    @classmethod
    def getFocus(cls):
        return cls.auto_focus
    
    @classmethod
    def setExposure(cls, case, lock_case):
        cls.auto_exposure = case
        cls.auto_exposure_lock = lock_case
        return cls.auto_exposure
    
    @classmethod
    def getExposure(cls):
        return cls.auto_exposure
    
    @classmethod
    def setWhiteBalance(cls, case, lock_case):
        cls.auto_white_balance = case
        cls.auto_wb_lock = lock_case
        return cls.auto_white_balance
    
    @classmethod
    def getWhiteBalance(cls):
        return cls.auto_white_balance
    
    @classmethod
    def setCropCase(cls, case):
        cls.crop = case
        return cls.crop
    
    @classmethod
    def getCropCase(cls):
        return cls.crop
    
    
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
    def setAspectRatio(cls, value):
        cls.aspect_ratio = value
        return cls.aspect_ratio
        
    @classmethod
    def getAspectRatio(cls):
        return cls.aspect_ratio
    
    
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
