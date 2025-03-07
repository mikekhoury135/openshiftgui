#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from pathlib import Path
from PySide6.QtCore import QSettings

class Settings:
    def __init__(self):
        self.settings = QSettings("OpenShiftGUI", "OpenShiftGUI")
        self.default_settings = {
            "oc_path": "",
            "theme": "light"
        }
        
        # Create settings folder if it doesn't exist
        self.settings_dir = Path.home() / ".openshift_gui"
        self.settings_dir.mkdir(exist_ok=True)
    
    def get_oc_path(self):
        """Get the configured OpenShift CLI path"""
        path = self.settings.value("oc_path", "")
        
        # If no custom path, return empty string
        if not path:
            return ""
        
        # Check if the path exists and is executable
        if os.path.exists(path) and os.access(path, os.X_OK):
            return path
        
        # Path doesn't exist or isn't executable
        return ""
    
    def set_oc_path(self, path):
        """Set the OpenShift CLI path"""
        self.settings.setValue("oc_path", path)
    
    def get_theme(self):
        """Get the current UI theme (light/dark)"""
        return self.settings.value("theme", "light")
    
    def set_theme(self, theme):
        """Set the UI theme (light/dark)"""
        self.settings.setValue("theme", theme)
    
    def get_all_settings(self):
        """Get all settings as a dictionary"""
        settings_dict = {}
        for key in self.default_settings.keys():
            settings_dict[key] = self.settings.value(key, self.default_settings[key])
        return settings_dict