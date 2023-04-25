# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QSegmentAnything
                                 A QGIS plugin
 META AI's Segment Anything (SAM) QGIS integration
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-04-21
        git sha              : $Format:%H$
        copyright            : (C) 2023 by Efstathios Lymperis
        email                : geo.elymperis@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsApplication

# Initialize Qt resources from file resources.py
from .resources import *

# Import the code for the DockWidget
from .qgs_segment_anything_dockwidget import QSegmentAnythingDockWidget
import os.path

from .installation.check_dependencies import check
from .settings.settings_dialog import SettingsDialog
from .core.settings import Settings
from .core.segmentation import AutoMaskGenerator


from .processing.ProcessingProvider import QSegmentAnythingProcessingProvider

DEPENDENCIES_OK = False
try:
    from segment_anything import SamPredictor, sam_model_registry, SamAutomaticMaskGenerator
    import numpy as np
    import torch
    import matplotlib.pyplot as plt
    import cv2
    from samgeo import SamGeo
    DEPENDENCIES_OK = False
except:
    try:
        check(['segment_anything', 'torch', 'torchvision', 'numpy',
              'matplotlib', 'opencv-python', ' matplotlib', 'segment-anything-py', 'segment-geospatial'])
    finally:
        from segment_anything import SamPredictor, sam_model_registry
        import numpy as np
        import torch
        import matplotlib.pyplot as plt
        import cv2
        from samgeo import SamGeo
        DEPENDENCIES_OK = True


class QSegmentAnything(object):
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        self.provider = QSegmentAnythingProcessingProvider()
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'QSegmentAnything_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&Segment Anything QGIS')
        self.toolbar = self.iface.addToolBar(u'QSegmentAnything')
        self.toolbar.setObjectName(u'QSegmentAnything')
        self.pluginIsActive = False
        self.dockwidget = None
        self.settingsDialog = None
        self.SettingsProvider = Settings()

    def tr(self, message):
        return QCoreApplication.translate('QSegmentAnything', message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):

        icon_path = ':/plugins/qgs_segment_anything/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Segment Anything'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # Settings Dialog
        icon = QIcon(os.path.dirname(__file__) + "/icons/icon_gear.png")
        self.openSettings = QAction(
            icon, "Select data folder (Geomeletitiki W.A.)", self.iface.mainWindow())
        self.openSettings.triggered.connect(self.showSettingsDialog)
        self.openSettings.setCheckable(False)
        self.iface.addToolBarIcon(self.openSettings)

        # Settings Dialog
        self.add_action(
            QIcon(os.path.dirname(__file__) + "/icons/icon_gear.png"),
            text=self.tr(u'Segment Anything - Settings'),
            callback=self.showSettingsDialog,
            parent=self.iface.mainWindow())

        # Register Processing Provider
        QgsApplication.processingRegistry().addProvider(self.provider)

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)
        self.pluginIsActive = False

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Segment Anything QGIS'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def showSettingsDialog(self):
        if not self.settingsDialog:
            self.settingsDialog = SettingsDialog(self.iface)
        self.settingsDialog.show()

    # --------------------------------------------------------------------------

    def showSystemSpecs(self):
        from .core.system_specs import get_specs
        system_specs = get_specs()
        specs_text = f" PyTorch: {system_specs['pytorch']}    Torch Vision: {system_specs['torchvision']} CUDA: {system_specs['CUDA']}"
        self.dockwidget.system_specs_label.setText(specs_text)

    def selectModel(self):
        available_models = self.SettingsProvider.getModelNamesList()
        self.dockwidget.select_model_combo.clear()
        self.dockwidget.select_model_combo.addItems(available_models)
        self.dockwidget.select_model_combo.currentIndexChanged.connect(lambda x: self.SettingsProvider.setSelectedModel(self.dockwidget.select_model_combo.currentText()))

    def test(self):
        # load the raster layer in QGIS
        layer = self.iface.activeLayer()     

        # get the file path of the raster layer
        file_path = layer.dataProvider().dataSourceUri()        

        maskGenerator = AutoMaskGenerator(device='cuda' if torch.cuda.is_available() else 'cpu', settings_provider=self.SettingsProvider)
        maskGenerator.segmentImage(image=file_path, output=os.path.join(os.path.expanduser('~'), 'Downloads', 'test.tiff'))

    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True

            if self.dockwidget is None:
                self.dockwidget = QSegmentAnythingDockWidget()

            self.dockwidget.closingPlugin.connect(self.onClosePlugin)
            self.showSystemSpecs()
            self.selectModel()

            #self.test()
            self.dockwidget.test_btn.clicked.connect(self.test)

            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
            self.dockwidget.show()