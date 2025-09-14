"""
Gesture list widget for managing available gestures.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
    QListWidgetItem, QPushButton, QLabel, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from loguru import logger


class GestureListWidget(QWidget):
    """Widget for displaying and managing gestures."""
    
    # Signals
    gesture_selected = pyqtSignal(str)
    gesture_deleted = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.gestures = {}
        self.setup_ui()
        self.load_gestures()
        
        logger.info("Gesture list widget initialized")
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Available Gestures")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
        
        # Gesture list
        self.gesture_list = QListWidget()
        self.gesture_list.itemClicked.connect(self.on_gesture_selected)
        layout.addWidget(self.gesture_list)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_gestures)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_selected_gesture)
        self.delete_button.setEnabled(False)
        
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Connect list selection to button state
        self.gesture_list.itemSelectionChanged.connect(self.on_selection_changed)
    
    def load_gestures(self):
        """Load available gestures."""
        # Default gestures
        default_gestures = {
            "open_palm": {
                "name": "Open Palm",
                "description": "All fingers extended",
                "confidence": 0.9,
                "enabled": True
            },
            "fist": {
                "name": "Fist",
                "description": "All fingers closed",
                "confidence": 0.9,
                "enabled": True
            },
            "peace_sign": {
                "name": "Peace Sign",
                "description": "Index and middle finger extended",
                "confidence": 0.8,
                "enabled": True
            },
            "thumbs_up": {
                "name": "Thumbs Up",
                "description": "Thumb extended, others closed",
                "confidence": 0.8,
                "enabled": True
            },
            "pointing": {
                "name": "Pointing",
                "description": "Index finger extended",
                "confidence": 0.7,
                "enabled": True
            }
        }
        
        self.gestures = default_gestures
        self.refresh_gestures()
    
    def refresh_gestures(self):
        """Refresh the gesture list display."""
        self.gesture_list.clear()
        
        for gesture_id, gesture_data in self.gestures.items():
            item = QListWidgetItem()
            item.setText(f"{gesture_data['name']} ({gesture_data['confidence']:.1f})")
            item.setData(Qt.UserRole, gesture_id)
            
            # Set item properties based on enabled state
            if gesture_data['enabled']:
                item.setForeground(Qt.black)
            else:
                item.setForeground(Qt.gray)
            
            self.gesture_list.addItem(item)
        
        logger.info(f"Refreshed gesture list with {len(self.gestures)} gestures")
    
    def on_gesture_selected(self, item: QListWidgetItem):
        """Handle gesture selection."""
        gesture_id = item.data(Qt.UserRole)
        if gesture_id:
            self.gesture_selected.emit(gesture_id)
            logger.info(f"Selected gesture: {gesture_id}")
    
    def on_selection_changed(self):
        """Handle selection change."""
        has_selection = len(self.gesture_list.selectedItems()) > 0
        self.delete_button.setEnabled(has_selection)
    
    def delete_selected_gesture(self):
        """Delete the selected gesture."""
        selected_items = self.gesture_list.selectedItems()
        if not selected_items:
            return
        
        item = selected_items[0]
        gesture_id = item.data(Qt.UserRole)
        
        if gesture_id in self.gestures:
            # Confirm deletion
            reply = QMessageBox.question(
                self,
                "Delete Gesture",
                f"Are you sure you want to delete the gesture '{self.gestures[gesture_id]['name']}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                del self.gestures[gesture_id]
                self.refresh_gestures()
                self.gesture_deleted.emit(gesture_id)
                logger.info(f"Deleted gesture: {gesture_id}")
    
    def add_gesture(self, gesture_id: str, gesture_data: dict):
        """Add a new gesture."""
        self.gestures[gesture_id] = gesture_data
        self.refresh_gestures()
        logger.info(f"Added gesture: {gesture_id}")
    
    def update_gesture(self, gesture_id: str, gesture_data: dict):
        """Update an existing gesture."""
        if gesture_id in self.gestures:
            self.gestures[gesture_id].update(gesture_data)
            self.refresh_gestures()
            logger.info(f"Updated gesture: {gesture_id}")
    
    def get_gesture(self, gesture_id: str) -> dict:
        """Get gesture data by ID."""
        return self.gestures.get(gesture_id, {})
    
    def get_all_gestures(self) -> dict:
        """Get all gestures."""
        return self.gestures.copy()
    
    def set_gesture_enabled(self, gesture_id: str, enabled: bool):
        """Enable or disable a gesture."""
        if gesture_id in self.gestures:
            self.gestures[gesture_id]['enabled'] = enabled
            self.refresh_gestures()
            logger.info(f"Set gesture {gesture_id} enabled: {enabled}")
    
    def get_enabled_gestures(self) -> dict:
        """Get only enabled gestures."""
        return {k: v for k, v in self.gestures.items() if v.get('enabled', True)}
