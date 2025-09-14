"""
App mapper widget for managing gesture to application mappings.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QLabel, QComboBox,
    QFileDialog, QMessageBox, QHeaderView
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QFileInfo
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QFileIconProvider
from loguru import logger
import os
import platform
from pathlib import Path
from core.config_manager import ConfigManager


class AppMapperWidget(QWidget):
    """Widget for managing gesture to application mappings."""
    
    # Signals
    mapping_changed = pyqtSignal(str, str)  # gesture, app_path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mappings = {}
        self.available_apps = []
        # Fix path resolution - go up from src/gui/components to project root
        self.icon_path = Path(__file__).parent.parent.parent.parent / "resources" / "icons"
        self.config_manager = ConfigManager()
        
        self.setup_ui()
        self.load_mappings()
        self.discover_apps()
        
        logger.info(f"App mapper widget initialized, icon path: {self.icon_path}")
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Gesture to Application Mappings")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
        
        # Mappings table
        self.mappings_table = QTableWidget()
        self.mappings_table.setColumnCount(3)
        self.mappings_table.setHorizontalHeaderLabels(["Gesture", "Application", "Path"])
        
        # Set table properties
        header = self.mappings_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        
        self.mappings_table.setAlternatingRowColors(True)
        self.mappings_table.setIconSize(QSize(20, 20))
        self.mappings_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        layout.addWidget(self.mappings_table)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add Mapping")
        self.add_button.clicked.connect(self.add_mapping)
        
        self.edit_button = QPushButton("Edit Mapping")
        self.edit_button.clicked.connect(self.edit_mapping)
        self.edit_button.setEnabled(False)
        
        self.remove_button = QPushButton("Remove Mapping")
        self.remove_button.clicked.connect(self.remove_mapping)
        self.remove_button.setEnabled(False)
        
        self.refresh_button = QPushButton("Refresh Apps")
        self.refresh_button.clicked.connect(self.discover_apps)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addWidget(self.refresh_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Connect table selection to button state
        self.mappings_table.itemSelectionChanged.connect(self.on_selection_changed)
    
    def load_mappings(self):
        """Load gesture mappings from config; seed sensible OS defaults if empty."""
        cfg = self.config_manager.get_gesture_mappings() or {}
        # Consider empty if all values are empty strings
        is_empty = True
        if cfg:
            for v in cfg.values():
                if v:
                    is_empty = False
                    break
        if not cfg or is_empty:
            defaults = self._get_os_default_mappings()
            self.mappings = defaults
            try:
                self.config_manager.set_gesture_mappings(defaults)
            except Exception as e:
                logger.warning(f"Failed to persist default mappings: {e}")
        else:
            self.mappings = cfg
        self.refresh_table()

    def _get_os_default_mappings(self) -> dict:
        """Return default mappings per OS with commonly available apps."""
        sysname = platform.system()
        if sysname == "Darwin":
            return {
                "open_palm": "/Applications/Safari.app",
                "fist": "/System/Library/CoreServices/Finder.app",
                "peace_sign": "/System/Applications/TextEdit.app",
                "thumbs_up": "/System/Applications/Mail.app",
                "pointing": "/Applications/Utilities/Terminal.app"
            }
        if sysname == "Windows":
            # Prefer Chrome for open_palm, Firefox for peace_sign
            chrome_candidates = [
                "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
            ]
            firefox_candidates = [
                "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
                "C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe",
            ]
            def first_existing(paths):
                for p in paths:
                    if p.endswith('.exe') and (os.path.exists(p) or p in ("notepad.exe","explorer.exe","calc.exe","msedge.exe","wmplayer.exe")):
                        return p
                return "notepad.exe"
            chrome = first_existing(chrome_candidates) if any(os.path.exists(p) for p in chrome_candidates) else "chrome.exe"
            firefox = first_existing(firefox_candidates) if any(os.path.exists(p) for p in firefox_candidates) else "firefox.exe"
            # Windows Media Player fallback executable name
            wmp = "wmplayer.exe"
            return {
                "open_palm": chrome,
                "fist": "explorer.exe",
                "peace_sign": firefox,
                "thumbs_up": wmp,
                "pointing": "notepad.exe"
            }
        # Linux (GNOME-friendly). Commands expected on PATH.
        return {
            "open_palm": "firefox",
            "fist": "nautilus",
            "peace_sign": "google-chrome" if os.path.exists("/usr/bin/google-chrome") else "chrome",
            "thumbs_up": "vlc",
            "pointing": "gedit"
        }
    
    def discover_apps(self):
        """Discover available applications."""
        import platform
        import os
        
        self.available_apps = []
        
        if platform.system() == "Darwin":  # macOS
            # Helper to pick first existing path from candidates
            def first_existing_path(paths: list) -> str:
                for p in paths:
                    if os.path.exists(p):
                        return p
                return ""

            # Common macOS applications with multiple candidate locations
            common_apps = [
                ("Safari", ["/Applications/Safari.app"]),
                ("Chrome", ["/Applications/Google Chrome.app"]),
                ("Firefox", ["/Applications/Firefox.app"]),
                ("Calculator", ["/System/Applications/Calculator.app", "/Applications/Calculator.app"]),
                ("TextEdit", ["/System/Applications/TextEdit.app", "/Applications/TextEdit.app"]),
                ("Mail", ["/System/Applications/Mail.app", "/Applications/Mail.app"]),
                ("Notes", ["/System/Applications/Notes.app", "/Applications/Notes.app"]),
                ("Finder", ["/System/Library/CoreServices/Finder.app"]),
                ("Terminal", ["/Applications/Utilities/Terminal.app", "/System/Applications/Utilities/Terminal.app"]),
                ("Activity Monitor", ["/Applications/Utilities/Activity Monitor.app"]),
                ("VLC", ["/Applications/VLC.app"]),
                ("Spotify", ["/Applications/Spotify.app"]),
                ("Messages", ["/System/Applications/Messages.app", "/Applications/Messages.app"]),
                ("FaceTime", ["/System/Applications/FaceTime.app", "/Applications/FaceTime.app"]),
                ("Photos", ["/System/Applications/Photos.app", "/Applications/Photos.app"]),
            ]

            for name, candidates in common_apps:
                chosen = first_existing_path(candidates)
                if chosen:
                    self.available_apps.append({"name": name, "path": chosen})
        
        elif platform.system() == "Windows":
            # Windows applications
            common_apps = [
                ("Chrome", "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"),
                ("Firefox", "C:\\Program Files\\Mozilla Firefox\\firefox.exe"),
                ("Notepad", "notepad.exe"),
                ("Calculator", "calc.exe"),
                ("File Explorer", "explorer.exe"),
                ("VLC Media Player", "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe"),
            ]
            
            for name, path in common_apps:
                if os.path.exists(path) or path.endswith('.exe'):
                    self.available_apps.append({"name": name, "path": path})
        
        else:  # Linux
            # Linux applications
            common_apps = [
                ("Firefox", "firefox"),
                ("Chrome", "google-chrome"),
                ("Gedit", "gedit"),
                ("Calculator", "gnome-calculator"),
                ("File Manager", "nautilus"),
                ("VLC", "vlc"),
                ("Terminal", "gnome-terminal"),
            ]
            
            for name, command in common_apps:
                self.available_apps.append({"name": name, "path": command})
        
        logger.info(f"Discovered {len(self.available_apps)} applications")
    
    def refresh_table(self):
        """Refresh the mappings table."""
        self.mappings_table.setRowCount(len(self.mappings))
        
        for row, (gesture, app_path) in enumerate(self.mappings.items()):
            # Gesture name with icon
            gesture_item = QTableWidgetItem(self._get_gesture_display_name(gesture))
            gesture_item.setFlags(gesture_item.flags() & ~Qt.ItemIsEditable)
            
            # Set gesture icon using emoji
            gesture_item.setIcon(self._get_gesture_emoji_icon(gesture))
            logger.debug(f"Set gesture emoji icon for {gesture}")
            
            self.mappings_table.setItem(row, 0, gesture_item)
            
            # Application name with icon
            app_name = self._get_app_name_from_path(app_path)
            app_item = QTableWidgetItem(app_name)
            app_item.setFlags(app_item.flags() & ~Qt.ItemIsEditable)
            
            # Set app icon
            app_icon = self._get_app_icon(app_path)
            if not app_icon.isNull():
                app_item.setIcon(app_icon)
            
            self.mappings_table.setItem(row, 1, app_item)
            
            # Application path
            path_item = QTableWidgetItem(app_path)
            path_item.setFlags(path_item.flags() & ~Qt.ItemIsEditable)
            self.mappings_table.setItem(row, 2, path_item)
        
        logger.info("Refreshed mappings table")
    
    def _get_gesture_display_name(self, gesture_id: str) -> str:
        """Get display name for gesture ID."""
        display_names = {
            "open_palm": "Open Palm",
            "fist": "Fist",
            "peace_sign": "Peace Sign",
            "thumbs_up": "Thumbs Up",
            "pointing": "Pointing"
        }
        return display_names.get(gesture_id, gesture_id)
    
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
            # Most Linux distros
            font.setFamily("Noto Color Emoji")
        font.setPointSize(16)
        painter.setFont(font)
        
        # Draw emoji centered
        painter.drawText(pixmap.rect(), Qt.AlignCenter, emoji)
        painter.end()
        
        return QIcon(pixmap)
    
    def _get_app_name_from_path(self, app_path: str) -> str:
        """Extract application name from path."""
        if not app_path:
            return "Not Set"
        
        # Find app in discovered apps
        for app in self.available_apps:
            if app["path"] == app_path:
                return app["name"]
        
        # Extract from path
        import os
        base = os.path.basename(app_path)
        # Strip .app suffix for nicer display
        name, ext = os.path.splitext(base)
        return name if ext.lower() == ".app" else base
    
    def _get_app_icon(self, app_path: str) -> QIcon:
        """Get application icon."""
        if not app_path:
            return QIcon()
        
        try:
            if platform.system() == "Darwin" and app_path.endswith('.app'):
                # First, try via NSWorkspace for guaranteed correct app icon
                ns_icon = self._get_macos_icon_via_nsworkspace(app_path)
                if ns_icon is not None and not ns_icon.isNull():
                    return ns_icon
                # For macOS .app bundles, try to get the icon from the bundle
                resources_path = os.path.join(app_path, "Contents", "Resources")
                
                if os.path.exists(resources_path):
                    # Try common icon names
                    icon_names = [
                        "AppIcon.icns", "icon.icns", "App.icns", "application.icns",
                        "AppIcon.png", "icon.png", "App.png", "application.png"
                    ]
                    
                    for icon_name in icon_names:
                        icon_path = os.path.join(resources_path, icon_name)
                        if os.path.exists(icon_path):
                            return QIcon(icon_path)
                    
                    # Try to find any .icns or .png file in Resources
                    for file in os.listdir(resources_path):
                        if file.endswith(('.icns', '.png')):
                            icon_path = os.path.join(resources_path, file)
                            return QIcon(icon_path)

                # Try using QFileIconProvider on the bundle path
                try:
                    provider = QFileIconProvider()
                    return provider.icon(QFileInfo(app_path))
                except Exception:
                    logger.debug("QFileIconProvider fallback failed")
            
            # Fallback to default app icon
            return QIcon()
        except Exception as e:
            logger.warning(f"Could not load icon for {app_path}: {e}")
            return QIcon()

    def _get_macos_icon_via_nsworkspace(self, app_path: str) -> QIcon:
        """Fetch macOS app icon using NSWorkspace and convert to QIcon.
        Returns QIcon() if unavailable.
        """
        try:
            from AppKit import NSWorkspace, NSBitmapImageRep, NSPNGFileType
            icon = NSWorkspace.sharedWorkspace().iconForFile_(app_path)
            if icon is None:
                return QIcon()
            icon.setSize_((64, 64))
            tiff_data = icon.TIFFRepresentation()
            if tiff_data is None:
                return QIcon()
            bitmap = NSBitmapImageRep.imageRepWithData_(tiff_data)
            png_data = bitmap.representationUsingType_properties_(NSPNGFileType, None)
            if png_data is None:
                return QIcon()
            data_bytes = bytes(png_data)
            pixmap = QPixmap()
            if not pixmap.loadFromData(data_bytes, "PNG"):
                return QIcon()
            return QIcon(pixmap)
        except Exception as e:
            logger.debug(f"NSWorkspace icon fetch failed for {app_path}: {e}")
            return QIcon()
    
    def on_selection_changed(self):
        """Handle table selection change."""
        has_selection = len(self.mappings_table.selectedItems()) > 0
        self.edit_button.setEnabled(has_selection)
        self.remove_button.setEnabled(has_selection)
    
    def add_mapping(self):
        """Add a new gesture mapping."""
        from gui.components.app_mapping_dialog import AppMappingDialog
        
        dialog = AppMappingDialog(self, self.available_apps, list(self.mappings.keys()))
        if dialog.exec():
            gesture, app_path = dialog.get_mapping()
            if gesture and app_path:
                self.mappings[gesture] = app_path
                self.refresh_table()
                self.mapping_changed.emit(gesture, app_path)
                # Persist change
                try:
                    self.config_manager.set_gesture_mapping(gesture, app_path)
                except Exception as e:
                    logger.warning(f"Failed to persist mapping: {e}")
                logger.info(f"Added mapping: {gesture} -> {app_path}")
    
    def edit_mapping(self):
        """Edit selected mapping."""
        selected_items = self.mappings_table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        gesture_item = self.mappings_table.item(row, 0)
        gesture_id = self._get_gesture_id_from_display_name(gesture_item.text())
        
        if gesture_id:
            from gui.components.app_mapping_dialog import AppMappingDialog
            
            dialog = AppMappingDialog(
                self, 
                self.available_apps, 
                list(self.mappings.keys()),
                gesture_id,
                self.mappings[gesture_id]
            )
            if dialog.exec():
                gesture, app_path = dialog.get_mapping()
                if gesture and app_path:
                    self.mappings[gesture] = app_path
                    self.refresh_table()
                    self.mapping_changed.emit(gesture, app_path)
                    try:
                        self.config_manager.set_gesture_mapping(gesture, app_path)
                    except Exception as e:
                        logger.warning(f"Failed to persist mapping: {e}")
                    logger.info(f"Updated mapping: {gesture} -> {app_path}")
    
    def remove_mapping(self):
        """Remove selected mapping."""
        selected_items = self.mappings_table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        gesture_item = self.mappings_table.item(row, 0)
        gesture_id = self._get_gesture_id_from_display_name(gesture_item.text())
        
        if gesture_id:
            reply = QMessageBox.question(
                self,
                "Remove Mapping",
                f"Are you sure you want to remove the mapping for '{gesture_item.text()}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.mappings[gesture_id] = ""
                self.refresh_table()
                self.mapping_changed.emit(gesture_id, "")
                try:
                    self.config_manager.set_gesture_mapping(gesture_id, "")
                except Exception as e:
                    logger.warning(f"Failed to persist mapping removal: {e}")
                logger.info(f"Removed mapping for: {gesture_id}")
    
    def _get_gesture_id_from_display_name(self, display_name: str) -> str:
        """Get gesture ID from display name."""
        gesture_map = {
            "Open Palm": "open_palm",
            "Fist": "fist",
            "Peace Sign": "peace_sign",
            "Thumbs Up": "thumbs_up",
            "Pointing": "pointing"
        }
        return gesture_map.get(display_name, display_name)
    
    def get_app_for_gesture(self, gesture: str) -> str:
        """Get application path for gesture."""
        return self.mappings.get(gesture, "")
    
    def set_mapping(self, gesture: str, app_path: str):
        """Set mapping for gesture."""
        self.mappings[gesture] = app_path
        self.refresh_table()
        self.mapping_changed.emit(gesture, app_path)
        try:
            self.config_manager.set_gesture_mapping(gesture, app_path)
        except Exception as e:
            logger.warning(f"Failed to persist mapping via set_mapping: {e}")
    
    def get_all_mappings(self) -> dict:
        """Get all mappings."""
        return self.mappings.copy()
