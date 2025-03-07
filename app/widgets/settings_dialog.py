#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QLineEdit, QPushButton, QFileDialog,
    QGroupBox, QComboBox, QDialogButtonBox, QMessageBox
)
from PySide6.QtCore import Qt

from ..settings import Settings

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.settings = Settings()
        self.setWindowTitle("Settings")
        self.resize(500, 300)
        
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Create OpenShift CLI Path settings
        oc_group = QGroupBox("OpenShift CLI Path")
        oc_layout = QFormLayout()
        
        self.oc_path_edit = QLineEdit()
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_for_oc)
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.oc_path_edit)
        path_layout.addWidget(self.browse_button)
        
        oc_layout.addRow("Path to oc.exe:", path_layout)
        oc_group.setLayout(oc_layout)
        
        # Create appearance settings
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QFormLayout()
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Light", "light")
        self.theme_combo.addItem("Dark", "dark")
        
        appearance_layout.addRow("Theme:", self.theme_combo)
        appearance_group.setLayout(appearance_layout)
        
        # Add description
        description = QLabel("Note: Changes to settings will take effect after restarting the application.")
        description.setWordWrap(True)
        
        # Add the standard buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save_settings)
        buttons.rejected.connect(self.reject)
        
        # Add everything to the main layout
        main_layout.addWidget(oc_group)
        main_layout.addWidget(appearance_group)
        main_layout.addWidget(description)
        main_layout.addStretch(1)
        main_layout.addWidget(buttons)
        
        self.setLayout(main_layout)
    
    def load_settings(self):
        """Load the current settings into the UI"""
        # Load OpenShift CLI path
        oc_path = self.settings.get_oc_path()
        self.oc_path_edit.setText(oc_path)
        
        # Load theme
        theme = self.settings.get_theme()
        index = self.theme_combo.findData(theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
    
    def save_settings(self):
        """Save the settings and close the dialog"""
        # Save OpenShift CLI path
        oc_path = self.oc_path_edit.text().strip()
        self.settings.set_oc_path(oc_path)
        
        # Save theme
        theme = self.theme_combo.currentData()
        self.settings.set_theme(theme)
        
        # Show a message about restarting
        QMessageBox.information(
            self,
            "Settings Saved",
            "Settings have been saved. Some changes may require restarting the application."
        )
        
        self.accept()
    
    def browse_for_oc(self):
        """Open file browser to select oc.exe"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select OpenShift CLI (oc.exe)", 
            "", 
            "Executable Files (*.exe);;All Files (*)"
        )
        
        if file_path:
            self.oc_path_edit.setText(file_path)