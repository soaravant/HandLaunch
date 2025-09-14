"""
Configuration management module for GestureLauncher.

This module handles loading, saving, and managing application configuration.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger


class ConfigManager:
    """Manages application configuration."""
    
    def __init__(self):
        self.config_dir = Path("data/config")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.default_config_file = self.config_dir / "default_config.json"
        self.user_config_file = self.config_dir / "user_config.json"
        
        self.default_config = self._get_default_config()
        self.user_config = self._load_user_config()
        
        logger.info("Config manager initialized")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "camera": {
                "index": 0,
                "width": 640,
                "height": 480,
                "fps": 30,
                "brightness": 0.5,
                "contrast": 0.5,
                "saturation": 0.5
            },
            "gesture_detection": {
                "min_confidence": 0.7,
                "min_tracking_confidence": 0.5,
                "max_hands": 2,
                "gesture_threshold": 0.8,
                "detection_enabled": True
            },
            "application": {
                "start_minimized": False,
                "minimize_to_tray": True,
                "auto_start": False,
                "theme": "dark",
                "language": "en"
            },
            "gesture_mappings": {
                "open_palm": "",
                "fist": "",
                "peace_sign": "",
                "thumbs_up": "",
                "pointing": ""
            },
            "logging": {
                "level": "INFO",
                "file_logging": True,
                "console_logging": True,
                "max_log_size": "10MB",
                "backup_count": 5
            }
        }
    
    def _load_user_config(self) -> Dict[str, Any]:
        """Load user configuration from file."""
        try:
            if self.user_config_file.exists():
                with open(self.user_config_file, 'r') as f:
                    config = json.load(f)
                logger.info("Loaded user configuration")
                return config
            else:
                # Create default user config
                self._save_user_config(self.default_config)
                return self.default_config.copy()
        except Exception as e:
            logger.error(f"Failed to load user config: {e}")
            return self.default_config.copy()
    
    def _save_user_config(self, config: Dict[str, Any]):
        """Save user configuration to file."""
        try:
            with open(self.user_config_file, 'w') as f:
                json.dump(config, f, indent=4)
            logger.info("Saved user configuration")
        except Exception as e:
            logger.error(f"Failed to save user config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        keys = key.split('.')
        value = self.user_config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """Set configuration value."""
        keys = key.split('.')
        config = self.user_config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        
        # Save to file
        self._save_user_config(self.user_config)
        
        logger.info(f"Set config {key} = {value}")
    
    def get_camera_config(self) -> Dict[str, Any]:
        """Get camera configuration."""
        return self.get("camera", {})
    
    def set_camera_config(self, config: Dict[str, Any]):
        """Set camera configuration."""
        self.set("camera", config)
    
    def get_gesture_detection_config(self) -> Dict[str, Any]:
        """Get gesture detection configuration."""
        return self.get("gesture_detection", {})
    
    def set_gesture_detection_config(self, config: Dict[str, Any]):
        """Set gesture detection configuration."""
        self.set("gesture_detection", config)
    
    def get_application_config(self) -> Dict[str, Any]:
        """Get application configuration."""
        return self.get("application", {})
    
    def set_application_config(self, config: Dict[str, Any]):
        """Set application configuration."""
        self.set("application", config)
    
    def get_gesture_mappings(self) -> Dict[str, str]:
        """Get gesture to application mappings."""
        return self.get("gesture_mappings", {})
    
    def set_gesture_mappings(self, mappings: Dict[str, str]):
        """Set gesture to application mappings."""
        self.set("gesture_mappings", mappings)
    
    def set_gesture_mapping(self, gesture: str, app_path: str):
        """Set mapping for a specific gesture."""
        mappings = self.get_gesture_mappings()
        mappings[gesture] = app_path
        self.set_gesture_mappings(mappings)
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return self.get("logging", {})
    
    def set_logging_config(self, config: Dict[str, Any]):
        """Set logging configuration."""
        self.set("logging", config)
    
    def reset_to_defaults(self):
        """Reset configuration to defaults."""
        self.user_config = self.default_config.copy()
        self._save_user_config(self.user_config)
        logger.info("Configuration reset to defaults")
    
    def export_config(self, file_path: str):
        """Export configuration to file."""
        try:
            with open(file_path, 'w') as f:
                json.dump(self.user_config, f, indent=4)
            logger.info(f"Configuration exported to {file_path}")
        except Exception as e:
            logger.error(f"Failed to export config: {e}")
    
    def import_config(self, file_path: str):
        """Import configuration from file."""
        try:
            with open(file_path, 'r') as f:
                config = json.load(f)
            
            # Validate config structure
            if self._validate_config(config):
                self.user_config = config
                self._save_user_config(self.user_config)
                logger.info(f"Configuration imported from {file_path}")
                return True
            else:
                logger.error("Invalid configuration file")
                return False
        except Exception as e:
            logger.error(f"Failed to import config: {e}")
            return False
    
    def _validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate configuration structure."""
        required_sections = ["camera", "gesture_detection", "application", "gesture_mappings"]
        
        for section in required_sections:
            if section not in config:
                return False
        
        return True
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get complete configuration."""
        return self.user_config.copy()
    
    def update_config(self, updates: Dict[str, Any]):
        """Update configuration with new values."""
        def deep_update(base_dict, update_dict):
            for key, value in update_dict.items():
                if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                    deep_update(base_dict[key], value)
                else:
                    base_dict[key] = value
        
        deep_update(self.user_config, updates)
        self._save_user_config(self.user_config)
        logger.info("Configuration updated")
