#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QListWidget, QListWidgetItem, QPushButton,
    QLabel, QMessageBox, QGroupBox
)
from PySide6.QtCore import Signal, Qt, QThread

from ..openshift_client import OpenShiftClient

class NamespacesWorker(QThread):
    """Thread for retrieving namespaces to prevent UI freeze"""
    finished = Signal(bool, object)

    def __init__(self, client):
        super().__init__()
        self.client = client

    def run(self):
        success, data = self.client.get_namespaces()
        self.finished.emit(success, data)

class NamespaceViewerWidget(QWidget):
    # Signal emitted when a namespace is selected
    namespace_selected = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.client = OpenShiftClient()
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Create namespaces group
        namespace_group = QGroupBox("Namespaces")
        namespace_layout = QVBoxLayout()
        
        # Add refresh button and counter
        header_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_namespaces)
        
        self.counter_label = QLabel("0 namespaces found")
        
        header_layout.addWidget(self.refresh_button)
        header_layout.addWidget(self.counter_label)
        header_layout.addStretch(1)
        
        namespace_layout.addLayout(header_layout)
        
        # Add namespace list
        self.namespace_list = QListWidget()
        self.namespace_list.itemClicked.connect(self.on_namespace_selected)
        namespace_layout.addWidget(self.namespace_list)
        
        namespace_group.setLayout(namespace_layout)
        
        # Add everything to the main layout
        main_layout.addWidget(namespace_group)
        
        self.setLayout(main_layout)
    
    def load_namespaces(self):
        """Load namespaces from the current context"""
        self.refresh_button.setEnabled(False)
        self.namespace_list.clear()
        self.counter_label.setText("Loading namespaces...")
        
        # Use a separate thread to avoid UI freeze
        self.namespaces_worker = NamespacesWorker(self.client)
        self.namespaces_worker.finished.connect(self.on_namespaces_loaded)
        self.namespaces_worker.start()
    
    def on_namespaces_loaded(self, success, data):
        """Handle namespaces loading result"""
        self.refresh_button.setEnabled(True)
        
        if success:
            namespaces = data
            for namespace in sorted(namespaces):
                item = QListWidgetItem(namespace)
                self.namespace_list.addItem(item)
            
            self.counter_label.setText(f"{len(namespaces)} namespaces found")
        else:
            error_message = data
            self.counter_label.setText("Failed to load namespaces")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load namespaces:\n{error_message}"
            )
    
    def on_namespace_selected(self, item):
        """Handle namespace selection"""
        namespace = item.text()
        success, _ = self.client.set_namespace(namespace)
        
        if success:
            self.namespace_selected.emit(namespace)
        else:
            QMessageBox.warning(
                self,
                "Warning",
                f"Failed to switch to namespace {namespace}"
            )