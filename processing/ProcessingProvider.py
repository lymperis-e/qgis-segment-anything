import os
import sys

pluginPath = os.path.dirname(__file__)
sys.path.append(os.path.join(pluginPath, "processing"))

from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsProcessingProvider

from .AutoMaskGenerator import AutoMaskGeneratorAlgorithm

class QSegmentAnythingProcessingProvider(QgsProcessingProvider):

    def __init__(self):
        QgsProcessingProvider.__init__(self)

    def unload(self):
        pass

    def loadAlgorithms(self):
        self.addAlgorithm(AutoMaskGeneratorAlgorithm())

    def id(self):
        return 'segment_anything'

    def name(self):
        return self.tr('Segment Anything')

    def icon(self):
        return QIcon(os.path.join(pluginPath, "icons", "icon.png"))

    def longName(self):
        return 'Segment Anything'
