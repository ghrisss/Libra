import depthai as dai
from src.configs import COLOR_CAM, DEBUG
from src.models.device import Device

class PipelineController():
    
    @classmethod
    def getPipeline(cls):
        pipeline = dai.Pipeline()
        if Device.getColorCameraEnable():
            if Device.getVideoEnable() or Device.getFrameEnable():
                cls.setColorPipeline(pipeline=pipeline)
            if Device.getDraftEnable():
                cls.setDraftPipeline(pipeline=pipeline)
        return pipeline
    
    @classmethod
    def setColorPipeline(cls, pipeline):
        # define os nós, de source e output
        rgbCam = pipeline.create(dai.node.ColorCamera)
        frameEncoder = pipeline.create(dai.node.VideoEncoder)
        rgbCamOut = pipeline.create(dai.node.XLinkOut)
        rgbCamOut.setStreamName('rgb')
        controlIn = pipeline.create(dai.node.XLinkIn)
        controlIn.setStreamName("control")
        frameOut = pipeline.create(dai.node.XLinkOut)
        frameOut.setStreamName('frame')
        
        # define as propriedades dos nós
        rgbCam.setVideoSize(COLOR_CAM.get('VIDEO_SIZE'))
        # rgbCam.setPreviewSize(COLOR_CAM.get('PREVIEW_SIZE'))
        rgbCam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_4_K)
        rgbCam.setBoardSocket(dai.CameraBoardSocket.CAM_A)
        rgbCam.setFps(COLOR_CAM.get('FPS'))
        
        frameEncoder.setDefaultProfilePreset(1, dai.VideoEncoderProperties.Profile.MJPEG)
        if DEBUG:
            print('[PipelineController] Pipelines criadas e prorpiedades atribuídas \n'+
                '[PipelineController] Parâmetros da câmera colorida \n' +
                    f'[PipelineController] FPS: {rgbCam.getFps()}, resolução: {rgbCam.getResolution()}, video: {rgbCam.getVideoSize()}, ' +
                        f'crop: {tuple([round(i,3) for i in rgbCam.getSensorCrop()])}')
        
        # cria a ligação entre eles
        rgbCam.video.link(rgbCamOut.input)
        controlIn.out.link(rgbCam.inputControl)
        rgbCam.still.link(frameEncoder.input)
        frameEncoder.bitstream.link(frameOut.input)
        if DEBUG:
            print('[PipelineController] Ligações entre pipelines atribuídas')


    @classmethod
    def setDraftPipeline(cls, pipeline):
        # define os nós, de source e output
        rgbCam = pipeline.create(dai.node.ColorCamera)
        controlIn = pipeline.create(dai.node.XLinkIn)
        controlIn.setStreamName('control')
        configIn = pipeline.create(dai.node.XLinkIn)
        configIn.setStreamName('config')
        ispOut = pipeline.create(dai.node.XLinkOut)
        ispOut.setStreamName('isp')
        rgbCamOut = pipeline.create(dai.node.XLinkOut)
        rgbCamOut.setStreamName('rgb')
        frameOut = pipeline.create(dai.node.XLinkOut)
        frameOut.setStreamName('frame')
        frameEncoder = pipeline.create(dai.node.VideoEncoder)
        
        # define as propriedades dos nós
        rgbCam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
        rgbCam.setIspScale(2, 3)
        rgbCam.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)
        rgbCam.setVideoSize(COLOR_CAM.get('PREVIEW_SIZE'))
        # rgbCam.setPreviewSize(COLOR_CAM.get('PREVIEW_SIZE'))
        # rgbCam.setPreviewKeepAspectRatio(True)
        frameEncoder.setDefaultProfilePreset(1, dai.VideoEncoderProperties.Profile.MJPEG)
        if DEBUG:
            print('[PipelineController] Pipelines criadas e prorpiedades atribuídas')
        
        # cria a ligação entre eles
        rgbCam.isp.link(ispOut.input)
        rgbCam.still.link(frameEncoder.input)
        rgbCam.video.link(rgbCamOut.input)
        # rgbCam.preview.link(rgbCamOut.input)
        controlIn.out.link(rgbCam.inputControl)
        configIn.out.link(rgbCam.inputConfig)
        frameEncoder.bitstream.link(frameOut.input)
        if DEBUG:
            print('[PipelineController] Ligações entre pipelines atribuídas \n' +
                '[PipelineController] Parâmetros da câmera colorida \n' +
                    f'[PipelineController] FPS: {rgbCam.getFps()}, resolução: {rgbCam.getResolution()}, ' +
                        f'video: {rgbCam.getVideoSize()}, crop: {rgbCam.getSensorCrop()}')
            