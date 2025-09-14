"""
Camera widget for displaying video feed and gesture detection overlay.
"""

import cv2
import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QImage, QPixmap
from loguru import logger


class CameraWidget(QWidget):
    """Widget for displaying camera feed with gesture detection overlay."""
    
    # Signals
    frame_processed = pyqtSignal(np.ndarray)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_frame = None
        self.detection_overlay = True
        
        self.setup_ui()
        self.setup_timer()
        
        logger.info("Camera widget initialized")
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Camera display label
        self.camera_label = QLabel()
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setMinimumSize(640, 480)
        self.camera_label.setStyleSheet("""
            QLabel {
                border: 2px solid #333;
                border-radius: 10px;
                background-color: #000;
            }
        """)
        layout.addWidget(self.camera_label)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.overlay_button = QPushButton("Toggle Overlay")
        self.overlay_button.setCheckable(True)
        self.overlay_button.setChecked(True)
        self.overlay_button.clicked.connect(self.toggle_overlay)
        
        self.snapshot_button = QPushButton("Take Snapshot")
        self.snapshot_button.clicked.connect(self.take_snapshot)
        
        button_layout.addWidget(self.overlay_button)
        button_layout.addWidget(self.snapshot_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
    
    def setup_timer(self):
        """Setup update timer."""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(33)  # ~30 FPS
    
    def update_frame(self, frame: np.ndarray):
        """Update the camera frame."""
        self.current_frame = frame.copy()
        self.frame_processed.emit(frame)
    
    def update_display(self):
        """Update the display with current frame."""
        if self.current_frame is not None:
            # Convert frame to QImage
            rgb_image = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
            # Scale image to fit label while maintaining aspect ratio
            pixmap = QPixmap.fromImage(qt_image)
            scaled_pixmap = pixmap.scaled(
                self.camera_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            self.camera_label.setPixmap(scaled_pixmap)
    
    def toggle_overlay(self):
        """Toggle detection overlay display."""
        self.detection_overlay = self.overlay_button.isChecked()
        logger.info(f"Detection overlay: {'enabled' if self.detection_overlay else 'disabled'}")
    
    def take_snapshot(self):
        """Take a snapshot of the current frame."""
        if self.current_frame is not None:
            try:
                # Save snapshot with timestamp
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"snapshot_{timestamp}.jpg"
                
                cv2.imwrite(filename, self.current_frame)
                logger.info(f"Snapshot saved: {filename}")
                
            except Exception as e:
                logger.error(f"Failed to save snapshot: {e}")
    
    def draw_gesture_overlay(self, frame: np.ndarray, gestures: list) -> np.ndarray:
        """Draw gesture detection overlay on frame."""
        if not self.detection_overlay:
            return frame
        
        overlay_frame = frame.copy()
        
        # Draw detected gestures
        for gesture_name, confidence in gestures:
            # Draw gesture name and confidence
            text = f"{gesture_name}: {confidence:.2f}"
            cv2.putText(
                overlay_frame,
                text,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )
        
        return overlay_frame
    
    def set_camera_status(self, status: str):
        """Set camera status display."""
        if status == "connected":
            self.camera_label.setStyleSheet("""
                QLabel {
                    border: 2px solid #00ff00;
                    border-radius: 10px;
                    background-color: #000;
                }
            """)
        elif status == "disconnected":
            self.camera_label.setStyleSheet("""
                QLabel {
                    border: 2px solid #ff0000;
                    border-radius: 10px;
                    background-color: #000;
                }
            """)
        else:
            self.camera_label.setStyleSheet("""
                QLabel {
                    border: 2px solid #333;
                    border-radius: 10px;
                    background-color: #000;
                }
            """)
    
    def clear_display(self):
        """Clear the camera display."""
        self.camera_label.clear()
        self.camera_label.setText("No Camera Feed")
        self.camera_label.setStyleSheet("""
            QLabel {
                border: 2px solid #333;
                border-radius: 10px;
                background-color: #000;
                color: #666;
                font-size: 16px;
            }
        """)
