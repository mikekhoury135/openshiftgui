#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QMessageBox, QStatusBar, QMenu, QMenuBar
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPalette, QColor, QAction

from .widgets.cluster_manager import ClusterManagerWidget
from .widgets.namespace_viewer import NamespaceViewerWidget
from .widgets.pod_viewer import PodViewerWidget
from .widgets.settings_dialog import SettingsDialog
from .settings import Settings

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.settings = Settings()
        
        self.setWindowTitle("OpenShift GUI")
        self.resize(1200, 800)
        
        # Set up the status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
        
        # Create menu bar
        self.setup_menu()
        
        # Set up the main tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Create tabs
        self.cluster_manager = ClusterManagerWidget(self)
        self.namespace_viewer = NamespaceViewerWidget(self)
        self.pod_viewer = PodViewerWidget(self)
        
        self.tabs.addTab(self.cluster_manager, "Cluster Configuration")
        self.tabs.addTab(self.namespace_viewer, "Namespaces")
        self.tabs.addTab(self.pod_viewer, "Pods")
        
        # Connect signals
        self.cluster_manager.cluster_connected.connect(self.on_cluster_connected)
        self.namespace_viewer.namespace_selected.connect(self.pod_viewer.load_pods)
        
        # Apply theme (must be done after creating widgets)
        self.apply_theme()

    def setup_menu(self):
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)
        
        # File menu
        file_menu = QMenu("&File", self)
        menu_bar.addMenu(file_menu)
        
        exit_action = QAction("E&xit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Settings menu
        settings_menu = QMenu("&Settings", self)
        menu_bar.addMenu(settings_menu)
        
        settings_action = QAction("&Preferences", self)
        settings_action.triggered.connect(self.open_settings)
        settings_menu.addAction(settings_action)
        
        # Theme submenu
        theme_menu = settings_menu.addMenu("&Theme")
        
        self.light_theme_action = QAction("&Light", self)
        self.light_theme_action.triggered.connect(lambda: self.change_theme("light"))
        self.light_theme_action.setCheckable(True)
        
        self.dark_theme_action = QAction("&Dark", self)
        self.dark_theme_action.triggered.connect(lambda: self.change_theme("dark"))
        self.dark_theme_action.setCheckable(True)
        
        theme_menu.addAction(self.light_theme_action)
        theme_menu.addAction(self.dark_theme_action)
        
        # Help menu
        help_menu = QMenu("&Help", self)
        menu_bar.addMenu(help_menu)
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def show_about(self):
        QMessageBox.about(
            self,
            "About OpenShift GUI",
            "OpenShift GUI\n\n"
            "A desktop application for managing OpenShift clusters offline.\n\n"
            "© 2023"
        )
    
    def on_cluster_connected(self, connected, cluster_name=None):
        if connected:
            self.statusBar.showMessage(f"Connected to cluster: {cluster_name}")
            self.tabs.setTabEnabled(1, True)
            self.tabs.setTabEnabled(2, True)
            # Trigger namespace refresh
            self.namespace_viewer.load_namespaces()
        else:
            self.statusBar.showMessage("Not connected to any cluster")
            self.tabs.setTabEnabled(1, False)
            self.tabs.setTabEnabled(2, False)
    
    def open_settings(self):
        """Open the settings dialog"""
        dialog = SettingsDialog(self)
        if dialog.exec():
            # If settings were saved, apply theme changes immediately
            self.apply_theme()
    
    def change_theme(self, theme):
        """Change the application theme"""
        self.settings.set_theme(theme)
        self.apply_theme()
        
        # Show message about the theme change
        QMessageBox.information(
            self,
            "Theme Changed",
            f"Theme changed to {theme.capitalize()}."
        )
    
    def apply_theme(self):
        """Apply the current theme to the application"""
        theme = self.settings.get_theme()
        
        # Update menu checkmarks
        if hasattr(self, 'light_theme_action'):
            self.light_theme_action.setChecked(theme == "light")
            self.dark_theme_action.setChecked(theme == "dark")
        
        app = self.parent()
        if app is None:
            # If no parent, get the application instance directly
            from PySide6.QtWidgets import QApplication
            app = QApplication.instance()
            
        if theme == "dark":
            self.apply_dark_theme(app)
        else:
            self.apply_light_theme(app)
    
    def apply_dark_theme(self, app):
        """Apply dark theme to the application"""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
        palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        palette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
        palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127))
        
        app.setPalette(palette)
        app.setStyle("Fusion") # Use Fusion style for better dark mode appearance
        
        # Apply stylesheet for additional components
        app.setStyleSheet("""
        QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }
        QTableView { gridline-color: #353535; }
        QTabBar::tab:selected { background: #3c7fb1; color: white; }
        QTabBar::tab:!selected { background: #353535; }
        QHeaderView::section { background-color: #353535; color: white; }
        QComboBox QAbstractItemView { background-color: #353535; color: white; }
        QComboBox { background-color: #353535; color: white; }
        QTextEdit { background-color: #202020; color: white; }
        QListWidget { background-color: #202020; color: white; }
        QLineEdit { background-color: #202020; color: white; }
        """)
    
    def apply_light_theme(self, app):
        """Apply light theme to the application (default)"""
        app.setPalette(app.style().standardPalette())
        app.setStyleSheet("")  # Clear any custom styles