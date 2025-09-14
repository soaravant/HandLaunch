"""
Gesture trainer dialog for training custom gestures.
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QDialogButtonBox
from loguru import logger


class GestureTrainerDialog(QDialog):
    """Dialog for training custom gestures."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gesture Trainer")
        self.setModal(True)
        self.resize(400, 300)
        
        self.setup_ui()
        logger.info("Gesture trainer dialog initialized")
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # TODO: Implement gesture training interface
        label = QLabel("Gesture Training Interface\n(Coming Soon)")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        
        layout.addWidget(button_box)
