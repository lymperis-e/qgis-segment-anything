from typing import Dict
import os
import json


class Settings:
    
    def __init__(self) -> None:
        self._loadSettings()

    def _loadSettings(self):
        self.settings_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'settings')
        self.settings_file = os.path.join(self.settings_dir, 'settings.json')

        self.settings = self._readSettings()
        self.models = self._readModels()

        # Set the first model as default
        self.selectedModel = self.getModelNamesList()[0]

    def _readSettings(self) -> dict:
        with open(self.settings_file, 'r') as file:
            return json.load(file)

    def _readModels(self):
        available_models = list()
        for filename in os.listdir(self.settings['models_dir']):
            if filename.endswith(".pth"):
                available_models.append({
                    "name": filename,
                    "path": os.path.join(self.settings['models_dir'], filename)
                })
        return available_models

    def saveSettings(self, settings: Dict[str, str]):
        self.settings = settings
        with open(self.settings_file, 'w') as file:
            json.dump(self.settings, file)
        self._loadSettings()

    def getSettings(self) -> Dict[str, str]:
        return self.settings

    def setSelectedModel(self, name: str):
        for model in self.models:
            if model['name'] == name:
                self.selectedModel = model
    
    def getModelNamesList(self):
        return [model['name'] for model in self.models]

    def getModelByName(self, name: str):
        for model in self.models:
            if model['name'] == name:
                return model
        return None
