# -*- coding: utf-8 -*-
"""
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
import json
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QVariant, Qt, QCoreApplication
from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt.QtGui import QStandardItemModel, QStandardItem, QIcon

from qgis.core import Qgis, QgsProject



FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'settings_dialog.ui'))

settings_file_path = os.path.join(os.path.dirname(__file__), 'settings.json')

from ..core.settings import Settings

class SettingsDialog(QDialog, FORM_CLASS):
    
    def __init__(self, iface):
        """Initialize the data settings dialog window."""
        super(SettingsDialog, self).__init__(iface.mainWindow())
        self.setupUi(self)
        self.iface = iface
        
        self.SettingsProvider = Settings()
        self.settings = self.SettingsProvider.getSettings()

    def showEvent(self, event):

        self.model_file_dialog.setFilePath(self.settings['models_dir']) 
        
        models = self.SettingsProvider.getModelNamesList()
        if len(models) > 0:
            self.found_models_label.setText(f"Found {len(models)} models:")
            self.found_models_titles_label.setText(', '.join(models))
        else:
            self.found_models_label.setText("No models found in the selected directory.")
            self.found_models_titles_label.setText("") 
                
        super(SettingsDialog, self).showEvent(event)
        
    def accept(self):
        """Called when the OK button has been pressed."""

        self.settings['models_dir'] = self.model_file_dialog.filePath()

        self.SettingsProvider.saveSettings(self.settings)
  
        self.close()
