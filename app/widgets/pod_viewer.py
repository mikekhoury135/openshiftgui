#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTableWidget, QTableWidgetItem, QPushButton, 
    QLabel, QMessageBox, QGroupBox, QTextEdit,
    QTabWidget, QComboBox, QHeaderView
)
from PySide6.QtCore import Signal, Qt, QThread, Slot
from PySide6.QtGui import QColor, QFont

from ..openshift_client import OpenShiftClient

class PodsWorker(QThread):
    """Thread for retrieving pods to prevent UI freeze"""
    finished = Signal(bool, object)

    def __init__(self, client, namespace):
        super().__init__()
        self.client = client
        self.namespace = namespace

    def run(self):
        success, data = self.client.get_pods(self.namespace)
        self.finished.emit(success, data)

class PodDetailsWorker(QThread):
    """Thread for retrieving pod details"""
    finished = Signal(bool, str)

    def __init__(self, client, pod_name, namespace):
        super().__init__()
        self.client = client
        self.pod_name = pod_name
        self.namespace = namespace

    def run(self):
        success, data = self.client.get_pod_details(self.pod_name, self.namespace)
        self.finished.emit(success, data)

class PodLogsWorker(QThread):
    """Thread for retrieving pod logs"""
    finished = Signal(bool, str)

    def __init__(self, client, pod_name, container_name, namespace):
        super().__init__()
        self.client = client
        self.pod_name = pod_name
        self.container_name = container_name
        self.namespace = namespace

    def run(self):
        success, data = self.client.get_pod_logs(
            self.pod_name, self.container_name, self.namespace
        )
        self.finished.emit(success, data)

class PodViewerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.client = OpenShiftClient()
        self.current_namespace = None
        self.current_pod = None
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Create a splitter to divide the pod list and pod details
        splitter = QSplitter(Qt.Vertical)
        
        # Pod list section
        pods_group = QGroupBox("Pods")
        pods_layout = QVBoxLayout()
        
        # Header with refresh button and namespace info
        header_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_pods)
        
        self.namespace_label = QLabel("Namespace: None")
        self.pod_count_label = QLabel("0 pods")
        
        header_layout.addWidget(self.refresh_button)
        header_layout.addWidget(self.namespace_label)
        header_layout.addWidget(self.pod_count_label)
        header_layout.addStretch(1)
        
        pods_layout.addLayout(header_layout)
        
        # Pod table
        self.pods_table = QTableWidget()
        self.pods_table.setColumnCount(5)
        self.pods_table.setHorizontalHeaderLabels(["Name", "Ready", "Status", "Restarts", "Age"])
        self.pods_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.pods_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.pods_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.pods_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.pods_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.pods_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.pods_table.setSelectionMode(QTableWidget.SingleSelection)
        self.pods_table.itemSelectionChanged.connect(self.on_pod_selected)
        
        pods_layout.addWidget(self.pods_table)
        pods_group.setLayout(pods_layout)
        
        # Pod details section
        details_group = QGroupBox("Pod Details")
        details_layout = QVBoxLayout()
        
        # Create tab widget for different views of pod info
        self.details_tabs = QTabWidget()
        
        # Details tab
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setFont(QFont("Courier New", 10))
        self.details_tabs.addTab(self.details_text, "Details")
        
        # Logs tab with container selector
        logs_widget = QWidget()
        logs_layout = QVBoxLayout()
        
        container_layout = QHBoxLayout()
        container_layout.addWidget(QLabel("Container:"))
        self.container_combo = QComboBox()
        self.container_combo.currentIndexChanged.connect(self.load_container_logs)
        container_layout.addWidget(self.container_combo)
        
        logs_layout.addLayout(container_layout)
        
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setFont(QFont("Courier New", 10))
        logs_layout.addWidget(self.logs_text)
        
        logs_widget.setLayout(logs_layout)
        self.details_tabs.addTab(logs_widget, "Logs")
        
        # Health tab
        self.health_text = QTextEdit()
        self.health_text.setReadOnly(True)
        self.health_text.setFont(QFont("Courier New", 10))
        self.details_tabs.addTab(self.health_text, "Health")
        
        details_layout.addWidget(self.details_tabs)
        details_group.setLayout(details_layout)
        
        # Add widgets to splitter
        splitter.addWidget(pods_group)
        splitter.addWidget(details_group)
        
        # Add splitter to main layout
        main_layout.addWidget(splitter)
        
        self.setLayout(main_layout)
    
    @Slot(str)
    def load_pods(self, namespace):
        """Load pods from the specified namespace"""
        self.current_namespace = namespace
        self.namespace_label.setText(f"Namespace: {namespace}")
        self.refresh_pods()
    
    def refresh_pods(self):
        """Refresh the pods list for the current namespace"""
        if not self.current_namespace:
            QMessageBox.information(
                self,
                "Information",
                "Please select a namespace first"
            )
            return
        
        self.refresh_button.setEnabled(False)
        self.pods_table.setRowCount(0)
        self.pod_count_label.setText("Loading pods...")
        
        # Use a separate thread to avoid UI freeze
        self.pods_worker = PodsWorker(self.client, self.current_namespace)
        self.pods_worker.finished.connect(self.on_pods_loaded)
        self.pods_worker.start()
    
    def on_pods_loaded(self, success, data):
        """Handle pods loading result"""
        self.refresh_button.setEnabled(True)
        
        if success:
            pods_data = data
            self.populate_pods_table(pods_data)
        else:
            error_message = data
            self.pod_count_label.setText("Failed to load pods")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load pods:\n{error_message}"
            )
    
    def populate_pods_table(self, pods_data):
        """Populate the pods table with data"""
        pods = pods_data.get("items", [])
        self.pods_table.setRowCount(len(pods))
        self.pod_count_label.setText(f"{len(pods)} pods")
        
        for row, pod in enumerate(pods):
            metadata = pod.get("metadata", {})
            status = pod.get("status", {})
            
            # Get pod name
            name = metadata.get("name", "")
            
            # Get container statuses
            container_statuses = status.get("containerStatuses", [])
            ready_count = sum(1 for cs in container_statuses if cs.get("ready", False))
            total_count = len(container_statuses)
            ready = f"{ready_count}/{total_count}"
            
            # Get pod status
            pod_status = status.get("phase", "Unknown")
            
            # Get restart count
            restarts = sum(cs.get("restartCount", 0) for cs in container_statuses)
            
            # Get age
            creation_timestamp = metadata.get("creationTimestamp", "")
            # This would need proper age calculation based on current time vs creation time
            age = creation_timestamp  # Simplified for now
            
            # Create table items
            name_item = QTableWidgetItem(name)
            ready_item = QTableWidgetItem(ready)
            status_item = QTableWidgetItem(pod_status)
            restarts_item = QTableWidgetItem(str(restarts))
            age_item = QTableWidgetItem(age)
            
            # Set colors based on status
            if pod_status == "Running":
                status_item.setBackground(QColor(200, 255, 200))  # Light green
            elif pod_status == "Failed":
                status_item.setBackground(QColor(255, 200, 200))  # Light red
            elif pod_status == "Pending":
                status_item.setBackground(QColor(255, 255, 200))  # Light yellow
            
            # Add items to the table
            self.pods_table.setItem(row, 0, name_item)
            self.pods_table.setItem(row, 1, ready_item)
            self.pods_table.setItem(row, 2, status_item)
            self.pods_table.setItem(row, 3, restarts_item)
            self.pods_table.setItem(row, 4, age_item)
    
    def on_pod_selected(self):
        """Handle pod selection"""
        selected_items = self.pods_table.selectedItems()
        if not selected_items:
            return
        
        selected_row = selected_items[0].row()
        pod_name = self.pods_table.item(selected_row, 0).text()
        self.current_pod = pod_name
        
        # Load pod details
        self.load_pod_details()
        
        # Update container dropdown
        self.load_container_list()
    
    def load_pod_details(self):
        """Load details for the selected pod"""
        if not self.current_pod or not self.current_namespace:
            return
        
        self.details_text.clear()
        self.details_text.setPlainText("Loading pod details...")
        
        # Use a separate thread
        self.details_worker = PodDetailsWorker(
            self.client, self.current_pod, self.current_namespace
        )
        self.details_worker.finished.connect(self.on_details_loaded)
        self.details_worker.start()
        
        # Also update health information
        self.update_health_info()
    
    def on_details_loaded(self, success, data):
        """Handle pod details loading result"""
        if success:
            self.details_text.setPlainText(data)
        else:
            self.details_text.setPlainText(f"Error loading pod details: {data}")
    
    def load_container_list(self):
        """Load the list of containers for the selected pod"""
        if not self.current_pod or not self.current_namespace:
            return
        
        # Clear the combo box
        self.container_combo.clear()
        self.logs_text.clear()
        
        # Get pod data to extract containers
        success, pod_data = self.client.get_pods(self.current_namespace)
        if not success:
            return
        
        # Find the selected pod
        pod = None
        for item in pod_data.get("items", []):
            if item.get("metadata", {}).get("name") == self.current_pod:
                pod = item
                break
        
        if not pod:
            return
        
        # Extract container names
        containers = pod.get("spec", {}).get("containers", [])
        container_names = [container.get("name") for container in containers]
        
        # Add containers to the combo box
        self.container_combo.addItems(container_names)
    
    def load_container_logs(self):
        """Load logs for the selected container"""
        if not self.current_pod or not self.current_namespace:
            return
        
        container_name = self.container_combo.currentText()
        if not container_name:
            return
        
        self.logs_text.clear()
        self.logs_text.setPlainText("Loading logs...")
        
        # Use a separate thread
        self.logs_worker = PodLogsWorker(
            self.client, self.current_pod, container_name, self.current_namespace
        )
        self.logs_worker.finished.connect(self.on_logs_loaded)
        self.logs_worker.start()
    
    def on_logs_loaded(self, success, data):
        """Handle container logs loading result"""
        if success:
            self.logs_text.setPlainText(data)
        else:
            self.logs_text.setPlainText(f"Error loading logs: {data}")
    
    def update_health_info(self):
        """Update the health information for the selected pod"""
        if not self.current_pod or not self.current_namespace:
            return
        
        self.health_text.clear()
        self.health_text.setPlainText("Loading health information...")
        
        # Get pod data to extract health information
        success, pod_data = self.client.get_pods(self.current_namespace)
        if not success:
            self.health_text.setPlainText(f"Error loading health information: {pod_data}")
            return
        
        # Find the selected pod
        pod = None
        for item in pod_data.get("items", []):
            if item.get("metadata", {}).get("name") == self.current_pod:
                pod = item
                break
        
        if not pod:
            self.health_text.setPlainText(f"Pod '{self.current_pod}' not found")
            return
        
        # Extract health information
        health_info = []
        
        # Pod conditions
        conditions = pod.get("status", {}).get("conditions", [])
        if conditions:
            health_info.append("=== Pod Conditions ===")
            for condition in conditions:
                status = condition.get("status", "")
                type_ = condition.get("type", "")
                reason = condition.get("reason", "")
                message = condition.get("message", "")
                health_info.append(f"Type: {type_}")
                health_info.append(f"Status: {status}")
                if reason:
                    health_info.append(f"Reason: {reason}")
                if message:
                    health_info.append(f"Message: {message}")
                health_info.append("")
        
        # Container statuses
        container_statuses = pod.get("status", {}).get("containerStatuses", [])
        if container_statuses:
            health_info.append("=== Container Statuses ===")
            for cs in container_statuses:
                name = cs.get("name", "")
                ready = cs.get("ready", False)
                restarts = cs.get("restartCount", 0)
                health_info.append(f"Container: {name}")
                health_info.append(f"Ready: {ready}")
                health_info.append(f"Restart Count: {restarts}")
                
                # Container state
                state = cs.get("state", {})
                for state_type, state_info in state.items():
                    health_info.append(f"State: {state_type}")
                    if state_info:
                        reason = state_info.get("reason", "")
                        if reason:
                            health_info.append(f"Reason: {reason}")
                        
                        message = state_info.get("message", "")
                        if message:
                            health_info.append(f"Message: {message}")
                
                # Last state if it exists
                last_state = cs.get("lastState", {})
                if any(last_state.values()):
                    health_info.append("Last State:")
                    for state_type, state_info in last_state.items():
                        if state_info:
                            health_info.append(f"  {state_type}:")
                            reason = state_info.get("reason", "")
                            if reason:
                                health_info.append(f"  Reason: {reason}")
                            
                            message = state_info.get("message", "")
                            if message:
                                health_info.append(f"  Message: {message}")
                
                health_info.append("")
        
        # Pod status
        status = pod.get("status", {})
        phase = status.get("phase", "")
        message = status.get("message", "")
        reason = status.get("reason", "")
        
        health_info.append("=== Pod Status ===")
        health_info.append(f"Phase: {phase}")
        if reason:
            health_info.append(f"Reason: {reason}")
        if message:
            health_info.append(f"Message: {message}")
        
        # Display the health information
        self.health_text.setPlainText("\n".join(health_info))