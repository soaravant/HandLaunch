"""
Settings dialog for GestureLauncher configuration.
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTabWidget, QDialogButtonBox
from loguru import logger


class SettingsDialog(QDialog):
    """Settings dialog for application configuration."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(500, 400)
        
        self.setup_ui()
        logger.info("Settings dialog initialized")
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # TODO: Add settings tabs
        # - Camera settings
        # - Gesture detection settings
        # - Application settings
        # - Logging settings
        
        layout.addWidget(tab_widget)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
