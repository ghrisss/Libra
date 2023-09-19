import depthai as dai

from src.models.frame import Frame
from src.repositories.frame import FrameRepository
from src.controllers.device import DeviceController



class FrameController():
    def __init__(cls) -> None:
        pass
 
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
    
      
    @classmethod
    def getImageSetting(cls):
        
        # focus
        if Frame.getFocus():
            ctrl = dai.CameraControl()
            ctrl.setAutoFocusTrigger()
            if Frame.continuous_focus:
                ctrl.setAutoFocusMode(dai.CameraControl.AutoFocusMode.CONTINUOUS_VIDEO)
            else:
                ctrl.setAutoFocusMode(dai.CameraControl.AutoFocusMode.AUTO)
            DeviceController.controlIn.send(ctrl)
        else:
            ctrl = dai.CameraControl()
            ctrl.setManualFocus(Frame.lens_posision)
            DeviceController.controlIn.send(ctrl)
            
        # exposure
        if Frame.getExposure():
            ctrl = dai.CameraControl()
            ctrl.setAutoExposureEnable()
            if Frame.auto_exposure_lock:
                ctrl.setAutoExposureLock(Frame.auto_exposure_lock)
            DeviceController.controlIn.send(ctrl)
        else:
            ctrl = dai.CameraControl()
            ctrl.setManualExposure(Frame.exposition_time, Frame.sensor_iso)
            DeviceController.controlIn.send(ctrl)
                
        # crop
        if Frame.getCropCase():
            crop_image = dai.ImageManipConfig()
            crop_image.setCropRect(Frame.getCropX(), Frame.getCropY(), 0, 0)
            DeviceController.configIn.send(crop_image)
        
        # white_balance
        if Frame.getWhiteBalance():
            ctrl = dai.CameraControl()
            ctrl.setAutoWhiteBalanceMode(dai.CameraControl.AutoWhiteBalanceMode.AUTO)
            if Frame.auto_wb_lock:
                ctrl.setAutoWhiteBalanceLock(Frame.auto_wb_lock)
            DeviceController.controlIn.send(ctrl)
        else:
            ctrl = dai.CameraControl()
            ctrl.setManualWhiteBalance(Frame.white_balance_manual)
            DeviceController.controlIn.send(ctrl)
            
        # saturation
        ctrl.setSaturation(Frame.getSaturation())
        # contrast
        ctrl.setContrast(Frame.getContrast())
        # brightness
        ctrl.setBrightness(Frame.getBrightness())
        # sharpness
        ctrl.setSharpness(Frame.getSharpness())
        # luma_denoise
        ctrl.setLumaDenoise(Frame.getLumaDenoise())
        # chroma_denoise
        ctrl.setChromaDenoise(Frame.getChromaDenoise())
        DeviceController.controlIn.send(ctrl)