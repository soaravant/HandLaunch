"""
Main window for the GestureLauncher application.

This module contains the main application window with camera preview,
gesture controls, and application management.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QTabWidget, QStatusBar,
    QMenuBar, QMenu, QMessageBox, QSystemTrayIcon
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QIcon
from loguru import logger

from .components.camera_widget import CameraWidget
from .components.gesture_list import GestureListWidget
from .components.app_mapper import AppMapperWidget
from .settings_dialog import SettingsDialog
from ..core.camera_manager import CameraManager
from ..core.gesture_detector import GestureDetector
from ..core.app_launcher import AppLauncher
from ..core.config_manager import ConfigManager


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
        
        self.setup_ui()
        self.setup_connections()
        self.setup_timer()
        
        logger.info("Main window initialized")
    
    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("GestureLauncher v0.1.0")
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create camera widget (left side)
        self.camera_widget = CameraWidget()
        main_layout.addWidget(self.camera_widget, 2)
        
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
        
        # Gesture management tab
        self.gesture_list = GestureListWidget()
        tab_widget.addTab(self.gesture_list, "Gestures")
        
        # App mapping tab
        self.app_mapper = AppMapperWidget()
        tab_widget.addTab(self.app_mapper, "App Mappings")
        
        layout.addWidget(tab_widget)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Detection")
        self.start_button.setCheckable(True)
        self.start_button.clicked.connect(self.toggle_detection)
        
        self.train_button = QPushButton("Train Gesture")
        self.train_button.clicked.connect(self.open_gesture_trainer)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.train_button)
        
        layout.addLayout(button_layout)
        
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
    
    def setup_system_tray(self):
        """Setup the system tray icon."""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            # TODO: Add tray icon and menu
            self.tray_icon.show()
    
    def setup_connections(self):
        """Setup signal connections."""
        self.gesture_detected.connect(self.on_gesture_detected)
        
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
        if self.start_button.isChecked():
            self.start_detection()
        else:
            self.stop_detection()
    
    def start_detection(self):
        """Start gesture detection."""
        try:
            if self.camera_manager.start_camera():
                self.start_button.setText("Stop Detection")
                self.status_bar.showMessage("Gesture detection active")
                logger.info("Gesture detection started")
            else:
                self.start_button.setChecked(False)
                QMessageBox.warning(self, "Camera Error", "Failed to start camera")
        except Exception as e:
            logger.error(f"Failed to start detection: {e}")
            self.start_button.setChecked(False)
            QMessageBox.critical(self, "Error", f"Failed to start detection: {e}")
    
    def stop_detection(self):
        """Stop gesture detection."""
        self.camera_manager.stop_camera()
        self.start_button.setText("Start Detection")
        self.status_bar.showMessage("Gesture detection stopped")
        logger.info("Gesture detection stopped")
    
    def process_frame(self, frame):
        """Process camera frame for gesture detection."""
        if not self.start_button.isChecked():
            return
        
        try:
            # Detect gestures in the frame
            gestures = self.gesture_detector.detect_gestures(frame)
            
            # Process detected gestures
            for gesture_name, confidence in gestures:
                if confidence > 0.8:  # High confidence threshold
                    self.gesture_detected.emit(gesture_name, confidence)
                    
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
    
    def on_gesture_detected(self, gesture_name, confidence):
        """Handle detected gesture."""
        logger.info(f"Gesture detected: {gesture_name} (confidence: {confidence:.2f})")
        
        # Get mapped application
        app_path = self.app_mapper.get_app_for_gesture(gesture_name)
        
        if app_path:
            try:
                self.app_launcher.launch_app(app_path)
                self.status_bar.showMessage(f"Launched app for gesture: {gesture_name}")
            except Exception as e:
                logger.error(f"Failed to launch app: {e}")
                QMessageBox.warning(self, "Launch Error", f"Failed to launch application: {e}")
        else:
            self.status_bar.showMessage(f"No app mapped for gesture: {gesture_name}")
    
    def open_gesture_trainer(self):
        """Open the gesture training dialog."""
        from .gesture_trainer import GestureTrainerDialog
        
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
            "About GestureLauncher",
            "GestureLauncher v0.1.0\n\n"
            "A desktop application that uses hand gesture recognition\n"
            "to launch applications via camera input.\n\n"
            "Built with Python, OpenCV, MediaPipe, and PyQt6."
        )
    
    def update_status(self):
        """Update status bar with current information."""
        if self.start_button.isChecked():
            fps = self.camera_manager.get_fps()
            self.status_bar.showMessage(f"Detection active - FPS: {fps}")
    
    def closeEvent(self, event):
        """Handle application close event."""
        self.stop_detection()
        self.camera_manager.cleanup()
        logger.info("Application closing")
        event.accept()
