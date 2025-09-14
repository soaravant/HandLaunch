"""
App mapping dialog for creating and editing gesture to application mappings.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QComboBox, QPushButton, QLabel, QLineEdit, QFileDialog,
    QMessageBox, QGroupBox
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from loguru import logger
import os
import platform
from pathlib import Path


class AppMappingDialog(QDialog):
    """Dialog for creating and editing gesture to application mappings."""
    
    def __init__(self, parent=None, available_apps=None, existing_gestures=None, 
                 selected_gesture=None, current_app_path=""):
        super().__init__(parent)
        self.available_apps = available_apps or []
        self.existing_gestures = existing_gestures or []
        self.selected_gesture = selected_gesture
        self.current_app_path = current_app_path
        # Fix path resolution - go up from src/gui/components to project root
        self.icon_path = Path(__file__).parent.parent.parent.parent / "resources" / "icons"
        
        self.setup_ui()
        self.setup_connections()
        
        # Set initial values if editing
        if selected_gesture:
            self.set_initial_values()
    
    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("Map Gesture to Application")
        self.setModal(True)
        self.resize(500, 300)
        
        layout = QVBoxLayout(self)
        
        # Gesture selection group
        gesture_group = QGroupBox("Gesture Selection")
        gesture_layout = QFormLayout(gesture_group)
        
        self.gesture_combo = QComboBox()
        self.gesture_combo.setEditable(False)
        
        # Add available gestures
        gesture_display_names = {
            "open_palm": "Open Palm",
            "fist": "Fist", 
            "peace_sign": "Peace Sign",
            "thumbs_up": "Thumbs Up",
            "pointing": "Pointing"
        }
        
        for gesture_id in self.existing_gestures:
            display_name = gesture_display_names.get(gesture_id, gesture_id)
            self.gesture_combo.addItem(display_name, gesture_id)
        
        gesture_layout.addRow("Gesture:", self.gesture_combo)
        layout.addWidget(gesture_group)
        
        # Application selection group
        app_group = QGroupBox("Application Selection")
        app_layout = QFormLayout(app_group)
        
        # Application selection method
        self.app_method_combo = QComboBox()
        self.app_method_combo.addItems(["Select from list", "Browse for application"])
        app_layout.addRow("Method:", self.app_method_combo)
        
        # Application list
        self.app_combo = QComboBox()
        self.app_combo.setIconSize(QSize(20, 20))
        self.app_combo.setEditable(False)
        self.populate_app_combo()
        app_layout.addRow("Application:", self.app_combo)
        
        # Custom path input
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Enter application path...")
        self.browse_button = QPushButton("Browse...")
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.browse_button)
        app_layout.addRow("Custom Path:", path_layout)
        
        layout.addWidget(app_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.setDefault(True)
        
        self.cancel_button = QPushButton("Cancel")
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def setup_connections(self):
        """Setup signal connections."""
        self.app_method_combo.currentTextChanged.connect(self.on_method_changed)
        self.browse_button.clicked.connect(self.browse_for_app)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        # Initially hide custom path
        self.path_edit.setVisible(False)
        self.browse_button.setVisible(False)
    
    def populate_app_combo(self):
        """Populate the application combo box."""
        self.app_combo.clear()
        
        for app in self.available_apps:
            # Get app icon
            app_icon = self._get_app_icon(app["path"])
            self.app_combo.addItem(app_icon, app["name"], app["path"])
    
    def _get_app_icon(self, app_path: str) -> QIcon:
        """Get application icon."""
        if not app_path:
            return QIcon()
        
        try:
            if platform.system() == "Darwin" and app_path.endswith('.app'):
                # For macOS .app bundles, try to get the icon from the bundle
                resources_path = os.path.join(app_path, "Contents", "Resources")
                
                if os.path.exists(resources_path):
                    # Try common icon names
                    icon_names = [
                        "AppIcon.icns", "icon.icns", "App.icns", "application.icns",
                        "AppIcon.png", "icon.png", "App.png", "application.png"
                    ]
                    
                    for icon_name in icon_names:
                        icon_path = os.path.join(resources_path, icon_name)
                        if os.path.exists(icon_path):
                            return QIcon(icon_path)
                    
                    # Try to find any .icns or .png file in Resources
                    for file in os.listdir(resources_path):
                        if file.endswith(('.icns', '.png')):
                            icon_path = os.path.join(resources_path, file)
                            return QIcon(icon_path)
                
                # Try using the app bundle itself as an icon (macOS can extract icons from bundles)
                return QIcon(app_path)
            
            # Fallback to default app icon
            return QIcon()
        except Exception as e:
            logger.warning(f"Could not load icon for {app_path}: {e}")
            return QIcon()
    
    def on_method_changed(self, method):
        """Handle application selection method change."""
        if method == "Select from list":
            self.app_combo.setVisible(True)
            self.path_edit.setVisible(False)
            self.browse_button.setVisible(False)
        else:  # Browse for application
            self.app_combo.setVisible(False)
            self.path_edit.setVisible(True)
            self.browse_button.setVisible(True)
    
    def browse_for_app(self):
        """Browse for application file."""
        import platform
        
        if platform.system() == "Darwin":  # macOS
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Application",
                "/Applications",
                "Application bundles (*.app);;All files (*.*)"
            )
        else:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Application",
                "",
                "Executable files (*.exe);;All files (*.*)"
            )
        
        if file_path:
            self.path_edit.setText(file_path)
    
    def set_initial_values(self):
        """Set initial values when editing existing mapping."""
        if self.selected_gesture:
            # Set gesture
            gesture_display_names = {
                "open_palm": "Open Palm",
                "fist": "Fist",
                "peace_sign": "Peace Sign", 
                "thumbs_up": "Thumbs Up",
                "pointing": "Pointing"
            }
            
            display_name = gesture_display_names.get(self.selected_gesture, self.selected_gesture)
            index = self.gesture_combo.findText(display_name)
            if index >= 0:
                self.gesture_combo.setCurrentIndex(index)
            
            # Set application
            if self.current_app_path:
                # Check if it's in our available apps
                found_in_list = False
                for i, app in enumerate(self.available_apps):
                    if app["path"] == self.current_app_path:
                        self.app_method_combo.setCurrentText("Select from list")
                        self.app_combo.setCurrentIndex(i)
                        found_in_list = True
                        break
                
                if not found_in_list:
                    # Use custom path
                    self.app_method_combo.setCurrentText("Browse for application")
                    self.path_edit.setText(self.current_app_path)
    
    def get_mapping(self):
        """Get the selected mapping."""
        # Get gesture
        gesture_data = self.gesture_combo.currentData()
        if not gesture_data:
            return None, None
        
        # Get application path
        if self.app_method_combo.currentText() == "Select from list":
            app_path = self.app_combo.currentData()
        else:
            app_path = self.path_edit.text().strip()
        
        if not app_path:
            return None, None
        
        return gesture_data, app_path
    
    def accept(self):
        """Handle OK button click."""
        gesture, app_path = self.get_mapping()
        
        if not gesture:
            QMessageBox.warning(self, "Invalid Selection", "Please select a gesture.")
            return
        
        if not app_path:
            QMessageBox.warning(self, "Invalid Selection", "Please select an application.")
            return
        
        # Validate application path
        if not os.path.exists(app_path):
            reply = QMessageBox.question(
                self,
                "Path Not Found",
                f"The application path '{app_path}' does not exist.\n\nDo you want to continue anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                return
        
        super().accept()
