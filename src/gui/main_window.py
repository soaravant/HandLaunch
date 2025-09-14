"""
Main window for the HandLaunch application.

This module contains the main application window with camera preview,
gesture controls, and application management.
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QTabWidget, QStatusBar,
    QMenuBar, QMenu, QMessageBox, QSystemTrayIcon, QAction, QToolButton
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor
from loguru import logger

from gui.components.camera_widget import CameraWidget
from gui.components.gesture_list import GestureListWidget
from gui.components.app_mapper import AppMapperWidget
from gui.settings_dialog import SettingsDialog
from core.camera_manager import CameraManager
from core.gesture_detector import GestureDetector
from core.app_launcher import AppLauncher
from core.config_manager import ConfigManager


class MainWindow(QMainWindow):
    """Main application window."""
    
    # Signals
    gesture_detected = pyqtSignal(str, float)  # gesture_name, confidence
    
    def __init__(self):
        super().__init__()
        self.camera_manager = CameraManager()
        self.gesture_detector = GestureDetector()
        self.app_launcher = AppLauncher()
        self.config_manager = ConfigManager()
        self.capture_pending = False
        self.capture_timer = QTimer(self)
        self.capture_timer.setSingleShot(True)
        self.capture_timer.timeout.connect(self._on_capture_timeout)
        self.cooldown_active = False
        self.cooldown_timer = QTimer(self)
        self.cooldown_timer.setSingleShot(True)
        self.cooldown_timer.timeout.connect(self._on_cooldown_complete)
        
        self.setup_ui()
        self.setup_connections()
        self.setup_timer()
        
        logger.info("Main window initialized")
    
    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("HandLaunch v0.1.0")
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create left panel with camera and bottom record control
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 12, 0)
        left_layout.setSpacing(8)
        
        # Camera
        self.camera_widget = CameraWidget()
        left_layout.addWidget(self.camera_widget)
        
        # Record control below camera
        record_row = QHBoxLayout()
        record_row.addStretch()
        self.record_button = QToolButton()
        self.record_button.setCheckable(True)
        self.record_button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.record_button.clicked.connect(self.toggle_detection)
        self._set_record_button_ui(is_recording=False)
        record_row.addWidget(self.record_button)
        record_row.addStretch()
        left_layout.addLayout(record_row)
        
        main_layout.addWidget(left_panel, 2)
        
        # Create control panel (right side)
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel, 1)
        
        # Setup menu bar
        self.setup_menu_bar()
        
        # Setup status bar
        self.setup_status_bar()
        
        # Setup system tray
        self.setup_system_tray()
    
    def create_control_panel(self):
        """Create the control panel widget."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Create tab widget
        tab_widget = QTabWidget()
        # App mapping tab only (Gestures tab removed per design)
        self.app_mapper = AppMapperWidget()
        tab_widget.addTab(self.app_mapper, "App Mappings")
        
        layout.addWidget(tab_widget)
        
        # No control buttons in the right panel
        
        return panel
    
    def setup_menu_bar(self):
        """Setup the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_status_bar(self):
        """Setup the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def _set_record_button_ui(self, is_recording: bool):
        """Update the record button to show a dot + 'Record' label under icon.
        Red when idle, green when recording.
        """
        # Create a pixmap with a colored dot
        size = 14  # smaller dot
        pm = QPixmap(size, size)
        pm.fill(Qt.transparent)
        painter = QPainter(pm)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(40, 200, 90) if is_recording else QColor(227, 51, 51))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, size, size)
        painter.end()
        self.record_button.setIcon(QIcon(pm))
        self.record_button.setIconSize(QSize(size, size))
        self.record_button.setText("Record")
        self.record_button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.record_button.setStyleSheet(
            "QToolButton { "
            "    color: white; "
            "    font-size: 12px; "
            "    padding: 12px 16px; "
            "    text-align: center; "
            "    border: 1px solid #444; "
            "    border-radius: 8px; "
            "    background-color: #2a2a2a; "
+            "} "
+            "QToolButton:hover { "
+            "    background-color: #3a3a3a; "
+            "} "
+            "QToolButton:pressed { "
+            "    background-color: #1a1a1a; "
+            "} "
+            "QToolButton:checked { "
+            "    border-color: #e33; "
+            "    background-color: #3a2a2a; "
+            "}"
        )
    
    def setup_system_tray(self):
        """Setup the system tray icon."""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            # TODO: Add tray icon and menu
            self.tray_icon.show()
    
    def setup_connections(self):
        """Setup signal connections."""
        self.gesture_detected.connect(self.on_gesture_detected)
        
        # Connect camera manager to camera widget
        self.camera_manager.set_frame_callback(self.camera_widget.update_frame)
        
        # Connect camera widget signals
        if hasattr(self.camera_widget, 'frame_processed'):
            self.camera_widget.frame_processed.connect(self.process_frame)
    
    def setup_timer(self):
        """Setup the main processing timer."""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(1000)  # Update every second
    
    def toggle_detection(self):
        """Toggle gesture detection on/off."""
        if self.record_button.isChecked():
            self.start_detection()
        else:
            self.stop_detection()
    
    def start_detection(self):
        """Start gesture detection."""
        try:
            if self.camera_manager.start_camera():
                self._set_record_button_ui(is_recording=True)
                self.status_bar.showMessage("Gesture detection active")
                logger.info("Gesture detection started")
            else:
                self.record_button.setChecked(False)
                QMessageBox.warning(self, "Camera Error", "Failed to start camera")
        except Exception as e:
            logger.error(f"Failed to start detection: {e}")
            self.start_button.setChecked(False)
            QMessageBox.critical(self, "Error", f"Failed to start detection: {e}")
    
    def stop_detection(self):
        """Stop gesture detection."""
        self.camera_manager.stop_camera()
        self._set_record_button_ui(is_recording=False)
        self.status_bar.showMessage("Gesture detection stopped")
        logger.info("Gesture detection stopped")
    
    def process_frame(self, frame):
        """Process camera frame for gesture detection."""
        if not self.record_button.isChecked():
            return
        # Skip only during cooldown; during countdown we still update the hint
        if self.cooldown_active:
            return
        if self.capture_pending:
            try:
                gestures = self.gesture_detector.detect_gestures(frame)
                if gestures:
                    top = max(gestures, key=lambda g: g[1])
                    self.camera_widget.hint_gesture_name = top[0]
                    self.camera_widget.hint_confidence = top[1]
            except Exception as e:
                logger.error(f"Error updating countdown hint: {e}")
            return

        try:
            # Detect gestures in the frame
            gestures = self.gesture_detector.detect_gestures(frame)
            
            # Process detected gestures
            for gesture_name, confidence in gestures:
                if confidence > 0.8:  # High confidence threshold
                    # Start capture countdown; store hint text/icon
                    self.capture_pending = True
                    self.camera_widget.countdown_active = True
                    self.camera_widget.countdown_start.start()
                    self.camera_widget.hint_gesture_name = gesture_name
                    self.camera_widget.hint_confidence = confidence
                    # Save snapshot frame to analyze after timeout
                    # Defer snapshot until countdown completes per requirements
                    self._pending_gesture_hint = gesture_name
                    self.capture_timer.start(2000)
                    
        except Exception as e:
            logger.error(f"Error processing frame: {e}")

    def _on_capture_timeout(self):
        """Handle end of capture countdown: analyze snapshot and launch app."""
        try:
            self.camera_widget.countdown_active = False
            self.capture_pending = False
            # Take snapshot now (after 2s)
            snapshot = getattr(self.camera_widget, 'current_frame', None)
            if snapshot is None:
                return
            # Re-run detection on snapshot for final decision
            gestures = self.gesture_detector.detect_gestures(snapshot)
            chosen = None
            if gestures:
                chosen = max(gestures, key=lambda g: g[1])
            elif hasattr(self, '_pending_gesture_hint'):
                chosen = (self._pending_gesture_hint, 0.8)
            if chosen:
                gesture_name, confidence = chosen
                self.gesture_detected.emit(gesture_name, confidence)
        except Exception as e:
            logger.error(f"Error on capture timeout: {e}")
    
    def on_gesture_detected(self, gesture_name, confidence):
        """Handle detected gesture."""
        logger.info(f"Gesture detected: {gesture_name} (confidence: {confidence:.2f})")
        
        # Get mapped application
        app_path = self.app_mapper.get_app_for_gesture(gesture_name)
        
        if app_path:
            try:
                self.app_launcher.launch_app(app_path)
                self.status_bar.showMessage(f"Launched app for gesture: {gesture_name}")
                # Start 4s cooldown
                self.cooldown_active = True
                self.camera_widget.cooldown_active = True
                self.camera_widget.cooldown_start.start()
                self.cooldown_timer.start(4000)
                # Stop recording automatically
                if self.record_button.isChecked():
                    self.record_button.setChecked(False)
                    self.stop_detection()
            except Exception as e:
                logger.error(f"Failed to launch app: {e}")
                QMessageBox.warning(self, "Launch Error", f"Failed to launch application: {e}")
        else:
            self.status_bar.showMessage(f"No app mapped for gesture: {gesture_name}")

    def _on_cooldown_complete(self):
        self.cooldown_active = False
        self.camera_widget.cooldown_active = False
    
    def open_gesture_trainer(self):
        """Open the gesture training dialog."""
        from gui.gesture_trainer import GestureTrainerDialog
        
        dialog = GestureTrainerDialog(self)
        if dialog.exec():
            # Refresh gesture list
            self.gesture_list.refresh_gestures()
            logger.info("Gesture training completed")
    
    def open_settings(self):
        """Open the settings dialog."""
        dialog = SettingsDialog(self)
        if dialog.exec():
            # Apply settings
            logger.info("Settings updated")
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About HandLaunch",
            "HandLaunch v0.1.0\n\n"
            "A desktop application that uses hand gesture recognition\n"
            "to launch applications via camera input.\n\n"
            "Built with Python, OpenCV, MediaPipe, and PyQt5."
        )
    
    def update_status(self):
        """Update status bar with current information."""
        if self.record_button.isChecked():
            fps = self.camera_manager.get_fps()
            self.status_bar.showMessage(f"Detection active - FPS: {fps}")
    
    def closeEvent(self, event):
        """Handle application close event."""
        self.stop_detection()
        self.camera_manager.cleanup()
        logger.info("Application closing")
        event.accept()
