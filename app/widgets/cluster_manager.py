#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, 
    QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QApplication
)
from PySide6.QtCore import Signal, Qt, QThread
import keyring

from ..openshift_client import OpenShiftClient

class LoginWorker(QThread):
    """Thread for login operations to prevent UI freeze"""
    finished = Signal(bool, str)

    def __init__(self, client, url, username, password):
        super().__init__()
        self.client = client
        self.url = url
        self.username = username
        self.password = password

    def run(self):
        success, message = self.client.login(self.url, self.username, self.password)
        self.finished.emit(success, message)

class ClusterManagerWidget(QWidget):
    # Signal emitted when cluster connection status changes
    cluster_connected = Signal(bool, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.client = OpenShiftClient()
        self.init_ui()
        self.load_saved_clusters()
        
        # Check if OpenShift CLI is installed
        self.check_oc_installed()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Create login form
        login_group = QGroupBox("Cluster Login")
        login_layout = QFormLayout()
        
        self.cluster_name_edit = QLineEdit()
        login_layout.addRow("Cluster Name:", self.cluster_name_edit)
        
        self.server_edit = QLineEdit()
        login_layout.addRow("Server URL:", self.server_edit)
        
        self.username_edit = QLineEdit()
        login_layout.addRow("Username:", self.username_edit)
        
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        login_layout.addRow("Password:", self.password_edit)
        
        # Add buttons for login and save
        button_layout = QHBoxLayout()
        
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        
        self.save_button = QPushButton("Save Cluster")
        self.save_button.clicked.connect(self.save_cluster)
        
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.save_button)
        
        login_layout.addRow("", button_layout)
        login_group.setLayout(login_layout)
        
        # Create saved clusters section
        saved_group = QGroupBox("Saved Clusters")
        saved_layout = QVBoxLayout()
        
        self.clusters_combo = QComboBox()
        self.clusters_combo.currentIndexChanged.connect(self.load_cluster_details)
        saved_layout.addWidget(self.clusters_combo)
        
        saved_group.setLayout(saved_layout)
        
        # Add status section
        status_group = QGroupBox("Connection Status")
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel("Not connected")
        status_layout.addWidget(self.status_label)
        
        status_group.setLayout(status_layout)
        
        # Add everything to the main layout
        main_layout.addWidget(login_group)
        main_layout.addWidget(saved_group)
        main_layout.addWidget(status_group)
        main_layout.addStretch(1)
        
        self.setLayout(main_layout)
    
    def check_oc_installed(self):
        """Check if OpenShift CLI is installed and show warning if not"""
        if not self.client.is_oc_installed():
            QMessageBox.warning(
                self,
                "OpenShift CLI Not Found",
                "The OpenShift CLI (oc) was not found on your system. "
                "Please install it and make sure it's available in your PATH."
            )
            self.login_button.setEnabled(False)
            self.status_label.setText("ERROR: OpenShift CLI not installed")
    
    def load_saved_clusters(self):
        """Load saved cluster configurations"""
        clusters = self.client.get_saved_clusters()
        self.clusters_combo.clear()
        
        if clusters:
            self.clusters_combo.addItem("Select a saved cluster...")
            for cluster in clusters:
                self.clusters_combo.addItem(cluster["name"], cluster)
        else:
            self.clusters_combo.addItem("No saved clusters")
    
    def load_cluster_details(self, index):
        """Load selected cluster details into the form"""
        if index <= 0:  # Skip the "Select a saved cluster..." or "No saved clusters" item
            return
        
        cluster = self.clusters_combo.itemData(index)
        if not cluster:
            return
        
        self.cluster_name_edit.setText(cluster["name"])
        self.server_edit.setText(cluster["url"])
        self.username_edit.setText(cluster["username"])
        
        # Try to retrieve password from the system keyring
        service_name = f"openshift_gui_{cluster['url']}"
        password = keyring.get_password(service_name, cluster["username"])
        if password:
            self.password_edit.setText(password)
        else:
            self.password_edit.clear()
    
    def save_cluster(self):
        """Save current cluster configuration"""
        name = self.cluster_name_edit.text().strip()
        url = self.server_edit.text().strip()
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        
        if not name or not url or not username:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please provide a name, server URL, and username."
            )
            return
        
        # Save cluster info (without password)
        self.client.save_cluster(name, url, username)
        
        # If password is provided, save it in system keyring
        if password:
            service_name = f"openshift_gui_{url}"
            keyring.set_password(service_name, username, password)
        
        # Refresh the clusters list
        self.load_saved_clusters()
        
        QMessageBox.information(
            self,
            "Cluster Saved",
            f"Cluster '{name}' has been saved."
        )
    
    def login(self):
        """Login to the OpenShift cluster"""
        url = self.server_edit.text().strip()
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        
        if not url or not username or not password:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please provide server URL, username, and password."
            )
            return
        
        # Update UI to show we're connecting
        self.login_button.setEnabled(False)
        self.status_label.setText("Connecting...")
        QApplication.processEvents()
        
        # Use a separate thread for login to prevent UI freeze
        self.login_worker = LoginWorker(self.client, url, username, password)
        self.login_worker.finished.connect(self.on_login_finished)
        self.login_worker.start()
    
    def on_login_finished(self, success, message):
        """Handle login result"""
        self.login_button.setEnabled(True)
        
        if success:
            cluster_name = self.cluster_name_edit.text().strip() or self.server_edit.text()
            self.status_label.setText(f"Connected to {cluster_name}")
            self.cluster_connected.emit(True, cluster_name)
        else:
            self.status_label.setText("Login failed")
            QMessageBox.critical(
                self,
                "Login Failed",
                f"Could not log in to the OpenShift cluster.\n\nError: {message}"
            )
            self.cluster_connected.emit(False, None)