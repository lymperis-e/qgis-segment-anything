from typing import Dict

from segment_anything import SamAutomaticMaskGenerator, sam_model_registry, SamPredictor
import numpy as np
import torch
import matplotlib.pyplot as plt
import cv2

from .settings import Settings
from .arrayImage import ArrayImage

class AutoMaskGenerator:
    
    def __init__(self, device='cpu', settings_provider=None):
        
        self.SettingsProvider = settings_provider if settings_provider else Settings()
        
        self.device = device
        self.Sam = self.loadModel(self.getCheckpointsFile())
        self.Sam.to(device=device)
        
        self.mask_generator = SamAutomaticMaskGenerator(self.Sam)
    
    
    def getCheckpointsFile(self):
        m = self.SettingsProvider.selectedModel
        return self.SettingsProvider.getModelByName(m)["path"]

    def loadModel(self, checkpoint: str):
        
        if "sam_vit_h" in checkpoint:
            modelType = "vit_h"

        if "sam_vit_l" in checkpoint:
            modelType = "vit_l"
        
        if "sam_vit_b" in checkpoint:
            modelType = "vit_b"
        
        if not modelType:
            raise Exception("Model type not found")
    
        return sam_model_registry[modelType](checkpoint=checkpoint)
    
    
    
    
    def segmentImage(self, image):
        
        normalized_img = ArrayImage(image).getArray(single_band=False)
        try:
            masks = self.mask_generator.generate(normalized_img)
        
            plt.figure(figsize=(20, 20))
            plt.imshow(normalized_img)
            #show_anns(masks)
            plt.axis('off')
            plt.show() 
            
            return masks
        
        except RuntimeError as e:
            print(e)
            return str(e)    





        
def show_anns(anns):
    if len(anns) == 0:
        return
    sorted_anns = sorted(anns, key=(lambda x: x['area']), reverse=True)
    ax = plt.gca()
    ax.set_autoscale_on(False)
    polygons = []
    color = []
    for ann in sorted_anns:
        m = ann['segmentation']
        img = np.ones((m.shape[0], m.shape[1], 3))
        color_mask = np.random.random((1, 3)).tolist()[0]
        for i in range(3):
            img[:,:,i] = color_mask[i]
        ax.imshow(np.dstack((img, m*0.35)))