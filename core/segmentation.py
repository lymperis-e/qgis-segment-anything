from typing import Dict

from ..installation.check_dependencies import check


try:
    import torch
    import numpy as np
    from samgeo import SamGeo
    from ..samgeo_overwrites.samgeo import SamGeoMod
except:
    try:
        check(['segment_anything', 'torch', 'torchvision', 'numpy', 'opencv-python', 'segment-anything-py', 'segment-geospatial'])
    finally:
        import torch
        import numpy as np
        from samgeo import SamGeo
        from ..samgeo_overwrites.samgeo import SamGeoMod
        
        
from .settings import Settings
from .arrayImage import ArrayImage


class AutoMaskGenerator:
    
    def __init__(self, device='cpu', settings_provider=None):
        
        self.SettingsProvider = settings_provider if settings_provider else Settings()
        
        self.device = device
        self.checkpointFile = self._getCheckpointFile()
        self.modelType = self._getModelType(self.checkpointFile)
        
        self.Sam = SamGeoMod(
            checkpoint=self.checkpointFile,
            model_type=self.modelType,
            device=self.device,
            erosion_kernel=(3, 3),
            mask_multiplier=255,
            sam_kwargs=None,
        )
    
    def _getCheckpointFile(self):
        selectedModel = self.SettingsProvider.selectedModel
        return self.SettingsProvider.getModelByName(selectedModel)["path"]

    def _getModelType(self, checkpoint: str):
        
        if "sam_vit_h" in checkpoint:
            modelType = "vit_h"

        if "sam_vit_l" in checkpoint:
            modelType = "vit_l"
        
        if "sam_vit_b" in checkpoint:
            modelType = "vit_b"
        
        if not modelType:
            raise Exception("Model type not found")
    
        return modelType
    
    
    
    
    def segmentImage(self, image: str, output: str = None):
        
        #normalized_img = ArrayImage(image).getArray(single_band=False)
        print(f"Segmenting image: {image}")
        print(f"Output: {output}")
        
        try:
            masks = self.Sam.generate(image, output)
            return masks
        
        except RuntimeError as e:
            print(e)
            return str(e)    
