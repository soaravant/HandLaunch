"""
Camera widget for displaying video feed and gesture detection overlay.
"""

import cv2
import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, QElapsedTimer
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
        self.countdown_active = False
        self.countdown_ms = 2000
        self.countdown_start = QElapsedTimer()
        self.cooldown_active = False
        self.cooldown_ms = 4000
        self.cooldown_start = QElapsedTimer()
        self.hint_gesture_name = None
        self.hint_confidence = 0.0
        
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
        
        # Removed extra controls per design (overlay toggle, snapshot)
    
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
            
            # Draw countdown overlay if active
            if self.countdown_active:
                remaining_ms = max(0, self.countdown_ms - self.countdown_start.elapsed())
                if remaining_ms == 0:
                    self.countdown_active = False
                else:
                    from PyQt5.QtGui import QPainter, QColor, QFont, QPen
                    pm = QPixmap(scaled_pixmap)
                    painter = QPainter(pm)
                    painter.setRenderHint(QPainter.Antialiasing)
                    radius = 24
                    margin = 12
                    # Unified dark background capsule
                    bg_width = radius*2 + 10 + 120
                    bg_height = radius*2
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(QColor(0, 0, 0, 150))
                    painter.drawRoundedRect(margin, margin, bg_width, bg_height, 12, 12)
                    # Timer circle
                    painter.setPen(QColor(255, 255, 255))
                    painter.setBrush(QColor(0, 0, 0, 0))
                    painter.drawEllipse(margin, margin, radius*2, radius*2)
                    # Progress arc
                    pen = QPen(QColor(255,255,255))
                    pen.setWidth(3)
                    painter.setPen(pen)
                    # Draw arc proportional to remaining time
                    frac = max(0.0, min(1.0, remaining_ms / float(self.countdown_ms)))
                    start_angle = 90 * 16
                    span_angle = int(-360 * 16 * (1.0 - frac))
                    painter.drawArc(margin, margin, radius*2, radius*2, start_angle, span_angle)
                    painter.setPen(QColor(255, 255, 255))
                    font = QFont()
                    font.setPointSize(16)
                    font.setBold(True)
                    painter.setFont(font)
                    seconds = int((remaining_ms + 999) / 1000)
                    painter.drawText(margin, margin, radius*2, radius*2, Qt.AlignCenter, str(seconds))
                    # Draw hint icon + label to the right of timer
                    # Use gesture hint if available
                    if getattr(self, 'hint_gesture_name', None):
                        text_x = margin + radius*2 + 10
                        # Draw emoji icon
                        emoji_icon = self._get_gesture_emoji_icon(self.hint_gesture_name)
                        hint_pix = emoji_icon.pixmap(24, 24)
                        painter.drawPixmap(text_x, margin + radius - 12, hint_pix)
                        text_x += 28
                        painter.setPen(QColor(255,255,255))
                        painter.drawText(text_x, margin + radius + 6, self.hint_gesture_name.replace('_',' ').title())
                    painter.end()
                    scaled_pixmap = pm

            # Cooldown bar removed per new design

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
        # Draw hint (icon + label) near top-left when countdown is active
        try:
            if self.countdown_active and gestures:
                from PyQt5.QtGui import QPainter, QColor, QFont, QIcon
                from pathlib import Path
                painter = QPainter()
                h, w, _ = overlay_frame.shape
                painter.begin(QImage(overlay_frame.data, w, h, w*3, QImage.Format_RGB888))
                painter.setRenderHint(QPainter.Antialiasing)
                margin = 12
                # Draw emoji icon for gesture
                gesture_name, confidence = gestures[0]
                emoji_icon = self._get_gesture_emoji_icon(gesture_name)
                pix = emoji_icon.pixmap(24, 24)
                painter.drawPixmap(margin, margin, pix)
                text_x = margin + 28
                painter.setPen(QColor(255, 255, 255))
                font = QFont()
                font.setPointSize(12)
                painter.setFont(font)
                painter.drawText(text_x, margin + 18, f"{gesture_name.replace('_',' ').title()}")
                painter.end()
        except Exception:
            pass
        
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
    
    def _get_gesture_emoji_icon(self, gesture_id: str):
        """Get emoji icon for gesture."""
        from PyQt5.QtGui import QFont, QPixmap, QPainter, QIcon
        from PyQt5.QtCore import Qt
        
        emoji_map = {
            "open_palm": "✋",
            "fist": "✊", 
            "peace_sign": "✌️",
            "thumbs_up": "👍",
            "pointing": "👆"
        }
        
        emoji = emoji_map.get(gesture_id, "❓")
        
        # Create a pixmap with the emoji
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Set font for emoji (force color emoji font per OS)
        import platform as _plt
        font = QFont()
        os_name = _plt.system()
        if os_name == "Darwin":
            font.setFamily("Apple Color Emoji")
        elif os_name == "Windows":
            font.setFamily("Segoe UI Emoji")
        else:
            font.setFamily("Noto Color Emoji")
        font.setPointSize(16)
        painter.setFont(font)
        
        # Draw emoji centered
        painter.drawText(pixmap.rect(), Qt.AlignCenter, emoji)
        painter.end()
        
        return QIcon(pixmap)
