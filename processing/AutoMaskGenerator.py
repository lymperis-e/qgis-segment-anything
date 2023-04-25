from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterRasterDestination,
    QgsMessageLog,
    Qgis
)
from qgis.PyQt.QtCore import QCoreApplication

from typing import Dict

from ..installation.check_dependencies import check
from ..samgeo_overwrites.samgeo import SamGeoMod
from ..core.settings import Settings


class AutoMaskGeneratorAlgorithm(QgsProcessingAlgorithm):

    def __init__(self):
        super().__init__()
        
    def tr(self, string):
        return QCoreApplication.translate('Processing', string)
    
    def name(self):
        return 'segment_anything_automatic_mask_generator'

    def displayName(self):
        return self.tr('IDF 1: Locate Nearest Meteo Stations')
    
    def group(self):
        return self.tr('segment_anything')
    
    def groupId(self):
        return 'segment_anything'

    def shortHelpString(self):
        return self.tr('Locate the 4 meteo stations nearest to the centroid of the basin')

    def createInstance(self):
        return AutoMaskGeneratorAlgorithm()
    
    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                'input_image',
                'Input Image',
                defaultValue=None,
                optional=False,
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                'output_mask',
                'Output Mask',
                createByDefault=True,
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        input_image = self.parameterAsRasterLayer(parameters, 'input_image', context)
        output_mask = self.parameterAsOutputLayer(parameters, 'output_mask', context)

        device = 'cpu'
        settings_provider = Settings()

        checkpoint_file = self._get_checkpoint_file(settings_provider)
        model_type = self._get_model_type(checkpoint_file)

        Sam = SamGeoMod(
            checkpoint=checkpoint_file,
            model_type=model_type,
            device=device,
            erosion_kernel=(3, 3),
            mask_multiplier=255,
            sam_kwargs=None,
        )

        QgsMessageLog.logMessage(f'Segmenting image: {input_image.source()}',
                                 tag='segment_anything', level=Qgis.Info)
        QgsMessageLog.logMessage(f'Output: {output_mask}',
                                 tag='segment_anything', level=Qgis.Info)

        try:
            masks = Sam.generate(input_image.source(), output_mask)
            return {'output_mask': masks}

        except RuntimeError as e:
            QgsMessageLog.logMessage(str(e), tag='segment_anything', level=Qgis.Critical)
            return {}

    def _get_checkpoint_file(self, settings_provider):
        selected_model = settings_provider.selectedModel
        return settings_provider.getModelByName(selected_model)['path']

    def _get_model_type(self, checkpoint: str):
        model_type = None

        if 'sam_vit_h' in checkpoint:
            model_type = 'vit_h'

        if 'sam_vit_l' in checkpoint:
            model_type = 'vit_l'

        if 'sam_vit_b' in checkpoint:
            model_type = 'vit_b'

        if not model_type:
            raise Exception('Model type not found')

        return model_type
