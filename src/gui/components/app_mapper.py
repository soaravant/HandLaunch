"""
App mapper widget for managing gesture to application mappings.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QLabel, QComboBox,
    QFileDialog, QMessageBox, QHeaderView
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from loguru import logger


class AppMapperWidget(QWidget):
    """Widget for managing gesture to application mappings."""
    
    # Signals
    mapping_changed = pyqtSignal(str, str)  # gesture, app_path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mappings = {}
        self.available_apps = []
        
        self.setup_ui()
        self.load_mappings()
        self.discover_apps()
        
        logger.info("App mapper widget initialized")
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Gesture to Application Mappings")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
        
        # Mappings table
        self.mappings_table = QTableWidget()
        self.mappings_table.setColumnCount(3)
        self.mappings_table.setHorizontalHeaderLabels(["Gesture", "Application", "Path"])
        
        # Set table properties
        header = self.mappings_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        
        self.mappings_table.setAlternatingRowColors(True)
        self.mappings_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        layout.addWidget(self.mappings_table)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add Mapping")
        self.add_button.clicked.connect(self.add_mapping)
        
        self.edit_button = QPushButton("Edit Mapping")
        self.edit_button.clicked.connect(self.edit_mapping)
        self.edit_button.setEnabled(False)
        
        self.remove_button = QPushButton("Remove Mapping")
        self.remove_button.clicked.connect(self.remove_mapping)
        self.remove_button.setEnabled(False)
        
        self.refresh_button = QPushButton("Refresh Apps")
        self.refresh_button.clicked.connect(self.discover_apps)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addWidget(self.refresh_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Connect table selection to button state
        self.mappings_table.itemSelectionChanged.connect(self.on_selection_changed)
    
    def load_mappings(self):
        """Load gesture mappings."""
        # Default mappings (empty for now)
        default_mappings = {
            "open_palm": "",
            "fist": "",
            "peace_sign": "",
            "thumbs_up": "",
            "pointing": ""
        }
        
        self.mappings = default_mappings
        self.refresh_table()
    
    def discover_apps(self):
        """Discover available applications."""
        # This would integrate with the AppLauncher class
        # For now, use some common applications
        self.available_apps = [
            {"name": "Chrome", "path": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"},
            {"name": "Firefox", "path": "C:\\Program Files\\Mozilla Firefox\\firefox.exe"},
            {"name": "Notepad", "path": "notepad.exe"},
            {"name": "Calculator", "path": "calc.exe"},
            {"name": "File Explorer", "path": "explorer.exe"},
            {"name": "VLC Media Player", "path": "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe"},
        ]
        
        logger.info(f"Discovered {len(self.available_apps)} applications")
    
    def refresh_table(self):
        """Refresh the mappings table."""
        self.mappings_table.setRowCount(len(self.mappings))
        
        for row, (gesture, app_path) in enumerate(self.mappings.items()):
            # Gesture name
            gesture_item = QTableWidgetItem(self._get_gesture_display_name(gesture))
            gesture_item.setFlags(gesture_item.flags() & ~Qt.ItemIsEditable)
            self.mappings_table.setItem(row, 0, gesture_item)
            
            # Application name
            app_name = self._get_app_name_from_path(app_path)
            app_item = QTableWidgetItem(app_name)
            app_item.setFlags(app_item.flags() & ~Qt.ItemIsEditable)
            self.mappings_table.setItem(row, 1, app_item)
            
            # Application path
            path_item = QTableWidgetItem(app_path)
            path_item.setFlags(path_item.flags() & ~Qt.ItemIsEditable)
            self.mappings_table.setItem(row, 2, path_item)
        
        logger.info("Refreshed mappings table")
    
    def _get_gesture_display_name(self, gesture_id: str) -> str:
        """Get display name for gesture ID."""
        display_names = {
            "open_palm": "Open Palm",
            "fist": "Fist",
            "peace_sign": "Peace Sign",
            "thumbs_up": "Thumbs Up",
            "pointing": "Pointing"
        }
        return display_names.get(gesture_id, gesture_id)
    
    def _get_app_name_from_path(self, app_path: str) -> str:
        """Extract application name from path."""
        if not app_path:
            return "Not Set"
        
        # Find app in discovered apps
        for app in self.available_apps:
            if app["path"] == app_path:
                return app["name"]
        
        # Extract from path
        import os
        return os.path.basename(app_path)
    
    def on_selection_changed(self):
        """Handle table selection change."""
        has_selection = len(self.mappings_table.selectedItems()) > 0
        self.edit_button.setEnabled(has_selection)
        self.remove_button.setEnabled(has_selection)
    
    def add_mapping(self):
        """Add a new gesture mapping."""
        from gui.components.app_mapping_dialog import AppMappingDialog
        
        dialog = AppMappingDialog(self, self.available_apps, list(self.mappings.keys()))
        if dialog.exec():
            gesture, app_path = dialog.get_mapping()
            if gesture and app_path:
                self.mappings[gesture] = app_path
                self.refresh_table()
                self.mapping_changed.emit(gesture, app_path)
                logger.info(f"Added mapping: {gesture} -> {app_path}")
    
    def edit_mapping(self):
        """Edit selected mapping."""
        selected_items = self.mappings_table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        gesture_item = self.mappings_table.item(row, 0)
        gesture_id = self._get_gesture_id_from_display_name(gesture_item.text())
        
        if gesture_id:
            from gui.components.app_mapping_dialog import AppMappingDialog
            
            dialog = AppMappingDialog(
                self, 
                self.available_apps, 
                list(self.mappings.keys()),
                gesture_id,
                self.mappings[gesture_id]
            )
            if dialog.exec():
                gesture, app_path = dialog.get_mapping()
                if gesture and app_path:
                    self.mappings[gesture] = app_path
                    self.refresh_table()
                    self.mapping_changed.emit(gesture, app_path)
                    logger.info(f"Updated mapping: {gesture} -> {app_path}")
    
    def remove_mapping(self):
        """Remove selected mapping."""
        selected_items = self.mappings_table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        gesture_item = self.mappings_table.item(row, 0)
        gesture_id = self._get_gesture_id_from_display_name(gesture_item.text())
        
        if gesture_id:
            reply = QMessageBox.question(
                self,
                "Remove Mapping",
                f"Are you sure you want to remove the mapping for '{gesture_item.text()}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.mappings[gesture_id] = ""
                self.refresh_table()
                self.mapping_changed.emit(gesture_id, "")
                logger.info(f"Removed mapping for: {gesture_id}")
    
    def _get_gesture_id_from_display_name(self, display_name: str) -> str:
        """Get gesture ID from display name."""
        gesture_map = {
            "Open Palm": "open_palm",
            "Fist": "fist",
            "Peace Sign": "peace_sign",
            "Thumbs Up": "thumbs_up",
            "Pointing": "pointing"
        }
        return gesture_map.get(display_name, display_name)
    
    def get_app_for_gesture(self, gesture: str) -> str:
        """Get application path for gesture."""
        return self.mappings.get(gesture, "")
    
    def set_mapping(self, gesture: str, app_path: str):
        """Set mapping for gesture."""
        self.mappings[gesture] = app_path
        self.refresh_table()
        self.mapping_changed.emit(gesture, app_path)
    
    def get_all_mappings(self) -> dict:
        """Get all mappings."""
        return self.mappings.copy()
