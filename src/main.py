#!/usr/bin/env python3
"""
HandLaunch - Main application entry point.

This module initializes and runs the HandLaunch desktop application.
"""

import sys
import os
from pathlib import Path
from loguru import logger

# Add src directory to Python path
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from gui.main_window import MainWindow


def setup_logging():
    """Configure logging for the application."""
    # Remove default logger
    logger.remove()
    
    # Add console logger
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # Add file logger
    log_dir = Path("data/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    logger.add(
        log_dir / "hand_launch.log",
        rotation="1 day",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG"
    )


def main():
    """Main application entry point."""
    # Setup logging
    setup_logging()
    logger.info("Starting HandLaunch application")
    
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("HandLaunch")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("HandLaunch")
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    try:
        main_window = MainWindow()
        main_window.show()
        logger.info("Main window created and shown")
        
        # Run application
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
