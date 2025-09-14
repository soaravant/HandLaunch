"""
Camera management module for GestureLauncher.

This module handles camera access, video capture, and frame processing.
"""

import cv2
import threading
import time
from typing import Optional, Callable, Tuple
from loguru import logger


class CameraManager:
    """Manages camera access and video capture."""
    
    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_running = False
        self.frame_callback: Optional[Callable] = None
        self.capture_thread: Optional[threading.Thread] = None
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        
    def start_camera(self, width: int = 640, height: int = 480, fps: int = 30) -> bool:
        """Start camera capture."""
        try:
            if self.is_running:
                logger.warning("Camera is already running")
                return True
            
            # Initialize camera
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                logger.error(f"Failed to open camera {self.camera_index}")
                return False
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.cap.set(cv2.CAP_PROP_FPS, fps)
            
            # Get actual properties
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = int(self.cap.get(cv2.CAP_PROP_FPS))
            
            logger.info(f"Camera started: {actual_width}x{actual_height} @ {actual_fps}fps")
            
            # Start capture thread
            self.is_running = True
            self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.capture_thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start camera: {e}")
            return False
    
    def stop_camera(self):
        """Stop camera capture."""
        self.is_running = False
        
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=2.0)
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        logger.info("Camera stopped")
    
    def set_frame_callback(self, callback: Callable):
        """Set callback function for frame processing."""
        self.frame_callback = callback
    
    def _capture_loop(self):
        """Main capture loop running in separate thread."""
        while self.is_running and self.cap:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    logger.warning("Failed to read frame from camera")
                    continue
                
                # Update FPS counter
                self._update_fps()
                
                # Call frame callback if set
                if self.frame_callback:
                    self.frame_callback(frame)
                    
            except Exception as e:
                logger.error(f"Error in capture loop: {e}")
                break
        
        logger.info("Capture loop ended")
    
    def _update_fps(self):
        """Update FPS counter."""
        self.fps_counter += 1
        current_time = time.time()
        
        if current_time - self.fps_start_time >= 1.0:
            self.current_fps = self.fps_counter
            self.fps_counter = 0
            self.fps_start_time = current_time
    
    def get_fps(self) -> int:
        """Get current FPS."""
        return self.current_fps
    
    def get_frame(self) -> Optional[Tuple[bool, any]]:
        """Get a single frame from camera."""
        if not self.cap:
            return None
        
        return self.cap.read()
    
    def get_camera_info(self) -> dict:
        """Get camera information."""
        if not self.cap:
            return {}
        
        return {
            'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': int(self.cap.get(cv2.CAP_PROP_FPS)),
            'brightness': self.cap.get(cv2.CAP_PROP_BRIGHTNESS),
            'contrast': self.cap.get(cv2.CAP_PROP_CONTRAST),
            'saturation': self.cap.get(cv2.CAP_PROP_SATURATION),
        }
    
    def set_camera_property(self, property_id: int, value: float) -> bool:
        """Set camera property."""
        if not self.cap:
            return False
        
        return self.cap.set(property_id, value)
    
    def list_available_cameras(self) -> list:
        """List all available cameras."""
        available_cameras = []
        
        for i in range(10):  # Check first 10 camera indices
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available_cameras.append(i)
                cap.release()
        
        return available_cameras
    
    def cleanup(self):
        """Cleanup camera resources."""
        self.stop_camera()
        logger.info("Camera manager cleaned up")
