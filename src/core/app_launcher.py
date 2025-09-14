"""
Application launcher module for HandLaunch.

This module handles launching external applications based on detected gestures.
"""

import subprocess
import os
import platform
import psutil
from typing import Dict, List, Optional
from pathlib import Path
from loguru import logger


class AppLauncher:
    """Handles launching external applications."""
    
    def __init__(self):
        self.system = platform.system()
        self.gesture_app_mappings: Dict[str, str] = {}
        self.load_mappings()
        
        logger.info(f"App launcher initialized for {self.system}")
    
    def load_mappings(self):
        """Load gesture to application mappings."""
        # Default mappings
        default_mappings = {
            "open_palm": self._get_default_app("browser"),
            "fist": self._get_default_app("file_manager"),
            "peace_sign": self._get_default_app("browser"),
            "thumbs_up": self._get_default_app("media_player"),
            "pointing": self._get_default_app("file_manager")
        }
        
        self.gesture_app_mappings.update(default_mappings)
        logger.info("Loaded default app mappings")
    
    def _get_default_app(self, app_type: str) -> str:
        """Get default application path for the given type."""
        if self.system == "Windows":
            return self._get_windows_default_app(app_type)
        elif self.system == "Darwin":  # macOS
            return self._get_macos_default_app(app_type)
        else:  # Linux
            return self._get_linux_default_app(app_type)
    
    def _get_windows_default_app(self, app_type: str) -> str:
        """Get Windows default application."""
        mappings = {
            "browser": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "file_manager": "explorer.exe",
            "media_player": "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe",
            "text_editor": "notepad.exe",
            "terminal": "cmd.exe"
        }
        return mappings.get(app_type, "notepad.exe")
    
    def _get_macos_default_app(self, app_type: str) -> str:
        """Get macOS default application."""
        mappings = {
            "browser": "open -a Safari",
            "file_manager": "open -a Finder",
            "media_player": "open -a VLC",
            "text_editor": "open -a TextEdit",
            "terminal": "open -a Terminal"
        }
        return mappings.get(app_type, "open -a TextEdit")
    
    def _get_linux_default_app(self, app_type: str) -> str:
        """Get Linux default application."""
        mappings = {
            "browser": "firefox",
            "file_manager": "nautilus",
            "media_player": "vlc",
            "text_editor": "gedit",
            "terminal": "gnome-terminal"
        }
        return mappings.get(app_type, "gedit")
    
    def launch_app(self, app_path: str) -> bool:
        """Launch an application."""
        try:
            if not app_path:
                logger.warning("No application path provided")
                return False
            
            logger.info(f"Launching application: {app_path}")
            
            if self.system == "Windows":
                return self._launch_windows_app(app_path)
            elif self.system == "Darwin":
                return self._launch_macos_app(app_path)
            else:
                return self._launch_linux_app(app_path)
                
        except Exception as e:
            logger.error(f"Failed to launch app {app_path}: {e}")
            return False
    
    def _launch_windows_app(self, app_path: str) -> bool:
        """Launch application on Windows."""
        try:
            if app_path.endswith('.exe'):
                # Direct executable
                subprocess.Popen([app_path], shell=True)
            else:
                # Use shell to open file/URL
                subprocess.Popen(f'start "" "{app_path}"', shell=True)
            return True
        except Exception as e:
            logger.error(f"Windows app launch failed: {e}")
            return False
    
    def _launch_macos_app(self, app_path: str) -> bool:
        """Launch application on macOS."""
        try:
            if app_path.startswith('open -a'):
                # Use open command
                subprocess.Popen(app_path.split(), shell=False)
            else:
                # Direct executable
                subprocess.Popen([app_path], shell=False)
            return True
        except Exception as e:
            logger.error(f"macOS app launch failed: {e}")
            return False
    
    def _launch_linux_app(self, app_path: str) -> bool:
        """Launch application on Linux."""
        try:
            # Try to launch in background
            subprocess.Popen([app_path], shell=False, 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            return True
        except Exception as e:
            logger.error(f"Linux app launch failed: {e}")
            return False
    
    def set_gesture_mapping(self, gesture: str, app_path: str):
        """Set mapping between gesture and application."""
        self.gesture_app_mappings[gesture] = app_path
        logger.info(f"Set mapping: {gesture} -> {app_path}")
    
    def get_gesture_mapping(self, gesture: str) -> Optional[str]:
        """Get application path for gesture."""
        return self.gesture_app_mappings.get(gesture)
    
    def get_all_mappings(self) -> Dict[str, str]:
        """Get all gesture mappings."""
        return self.gesture_app_mappings.copy()
    
    def remove_gesture_mapping(self, gesture: str):
        """Remove gesture mapping."""
        if gesture in self.gesture_app_mappings:
            del self.gesture_app_mappings[gesture]
            logger.info(f"Removed mapping for gesture: {gesture}")
    
    def discover_applications(self) -> List[Dict[str, str]]:
        """Discover available applications on the system."""
        apps = []
        
        if self.system == "Windows":
            apps = self._discover_windows_apps()
        elif self.system == "Darwin":
            apps = self._discover_macos_apps()
        else:
            apps = self._discover_linux_apps()
        
        logger.info(f"Discovered {len(apps)} applications")
        return apps
    
    def _discover_windows_apps(self) -> List[Dict[str, str]]:
        """Discover Windows applications."""
        apps = []
        
        # Common Windows app locations
        common_paths = [
            "C:\\Program Files",
            "C:\\Program Files (x86)",
            os.path.expanduser("~\\AppData\\Local\\Programs")
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.endswith('.exe'):
                            app_path = os.path.join(root, file)
                            app_name = os.path.splitext(file)[0]
                            apps.append({
                                'name': app_name,
                                'path': app_path,
                                'type': 'executable'
                            })
        
        return apps[:50]  # Limit to first 50 apps
    
    def _discover_macos_apps(self) -> List[Dict[str, str]]:
        """Discover macOS applications."""
        apps = []
        
        # Common macOS app locations
        app_paths = [
            "/Applications",
            "/System/Applications",
            os.path.expanduser("~/Applications")
        ]
        
        for app_path in app_paths:
            if os.path.exists(app_path):
                for item in os.listdir(app_path):
                    if item.endswith('.app'):
                        full_path = os.path.join(app_path, item)
                        app_name = os.path.splitext(item)[0]
                        apps.append({
                            'name': app_name,
                            'path': full_path,
                            'type': 'application'
                        })
        
        return apps
    
    def _discover_linux_apps(self) -> List[Dict[str, str]]:
        """Discover Linux applications."""
        apps = []
        
        # Common Linux app locations
        paths = [
            "/usr/bin",
            "/usr/local/bin",
            "/snap/bin",
            os.path.expanduser("~/.local/bin")
        ]
        
        for path in paths:
            if os.path.exists(path):
                for file in os.listdir(path):
                    file_path = os.path.join(path, file)
                    if os.path.isfile(file_path) and os.access(file_path, os.X_OK):
                        apps.append({
                            'name': file,
                            'path': file_path,
                            'type': 'executable'
                        })
        
        return apps[:50]  # Limit to first 50 apps
    
    def is_app_running(self, app_name: str) -> bool:
        """Check if an application is currently running."""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if app_name.lower() in proc.info['name'].lower():
                    return True
            return False
        except Exception as e:
            logger.error(f"Error checking if app is running: {e}")
            return False
    
    def close_app(self, app_name: str) -> bool:
        """Close an application by name."""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if app_name.lower() in proc.info['name'].lower():
                    proc.terminate()
                    logger.info(f"Terminated process: {proc.info['name']}")
                    return True
            return False
        except Exception as e:
            logger.error(f"Error closing app: {e}")
            return False

