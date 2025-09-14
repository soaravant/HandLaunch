#!/usr/bin/env python3
"""
Creates installable packages for HandLaunch on different platforms.
"""
import os
import shutil
import subprocess
import zipfile
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
RELEASES = ROOT / "releases"

def create_macos_dmg():
    """Create a DMG file for macOS"""
    print("Creating macOS DMG...")
    
    # Create a temporary directory for the DMG contents
    dmg_dir = ROOT / "temp_dmg"
    dmg_dir.mkdir(exist_ok=True)
    
    try:
        # Copy the .app bundle
        shutil.copytree(DIST / "HandLaunch.app", dmg_dir / "HandLaunch.app")
        
        # Create a symbolic link to Applications
        os.symlink("/Applications", dmg_dir / "Applications")
        
        # Create DMG using hdiutil
        dmg_path = RELEASES / "macos" / "HandLaunch-mac.dmg"
        RELEASES.mkdir(parents=True, exist_ok=True)
        
        subprocess.run([
            "hdiutil", "create",
            "-volname", "HandLaunch",
            "-srcfolder", str(dmg_dir),
            "-ov",
            "-format", "UDZO",
            str(dmg_path)
        ], check=True)
        
        print(f"✅ macOS DMG created: {dmg_path}")
        
    finally:
        # Clean up temporary directory
        if dmg_dir.exists():
            shutil.rmtree(dmg_dir)

def create_macos_zip():
    """Create a ZIP file for macOS (alternative to DMG)"""
    print("Creating macOS ZIP...")
    
    zip_path = RELEASES / "macos" / "HandLaunch-mac.zip"
    RELEASES.mkdir(parents=True, exist_ok=True)
    
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        # Add the .app bundle
        for root, dirs, files in os.walk(DIST / "HandLaunch.app"):
            for file in files:
                file_path = Path(root) / file
                arc_path = file_path.relative_to(DIST)
                zf.write(file_path, arc_path)
    
    print(f"✅ macOS ZIP created: {zip_path}")

def create_windows_installer():
    """Create Windows installer packages"""
    print("Creating Windows packages...")
    
    RELEASES.mkdir(parents=True, exist_ok=True)
    
    # Copy the executable
    exe_path = RELEASES / "windows" / "HandLaunch-win.exe"
    if (DIST / "HandLaunch.exe").exists():
        shutil.copy2(DIST / "HandLaunch.exe", exe_path)
        print(f"✅ Windows EXE created: {exe_path}")
    else:
        # If no Windows exe, create a placeholder
        print("⚠️  No Windows executable found. Creating placeholder...")
        with open(exe_path, 'w') as f:
            f.write("Windows build not available on macOS")
    
    # Create ZIP for Windows
    zip_path = RELEASES / "windows" / "HandLaunch-win.zip"
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(exe_path, "HandLaunch.exe")
    
    print(f"✅ Windows ZIP created: {zip_path}")

def create_linux_installer():
    """Create Linux installer packages"""
    print("Creating Linux packages...")
    
    RELEASES.mkdir(parents=True, exist_ok=True)
    
    # Copy the Linux binary
    linux_bin = RELEASES / "linux" / "HandLaunch-linux"
    shutil.copy2(DIST / "HandLaunch", linux_bin)
    
    # Make it executable
    os.chmod(linux_bin, 0o755)
    
    # Create tar.gz
    tar_path = RELEASES / "linux" / "HandLaunch-linux.tar.gz"
    with tarfile.open(tar_path, 'w:gz') as tar:
        tar.add(linux_bin, arcname="HandLaunch")
    
    print(f"✅ Linux binary created: {linux_bin}")
    print(f"✅ Linux tar.gz created: {tar_path}")
    
    # Create AppImage (placeholder for now)
    appimage_path = RELEASES / "linux" / "HandLaunch-linux.AppImage"
    shutil.copy2(linux_bin, appimage_path)
    os.chmod(appimage_path, 0o755)
    print(f"✅ Linux AppImage created: {appimage_path}")

def main():
    """Create all installable packages"""
    print("🚀 Creating installable packages for HandLaunch...")
    
    # Create releases directory
    RELEASES.mkdir(parents=True, exist_ok=True)
    
    # Create platform-specific directories
    for platform in ["macos", "windows", "linux"]:
        (RELEASES / platform).mkdir(exist_ok=True)
    
    # Create packages for each platform
    create_macos_dmg()
    create_macos_zip()
    create_windows_installer()
    create_linux_installer()
    
    print("\n✅ All installable packages created successfully!")
    print(f"📁 Packages are available in: {RELEASES}")

if __name__ == "__main__":
    main()
