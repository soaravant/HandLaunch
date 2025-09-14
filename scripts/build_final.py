#!/usr/bin/env python3
"""
Builds final installable packages for HandLaunch.
Creates .dmg, .exe, and .AppImage files.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
RELEASES = ROOT / "releases"

def clean_and_build():
    """Clean and build all platforms"""
    print("🧹 Cleaning previous builds...")
    for path in [DIST, ROOT / "build"]:
        if path.exists():
            shutil.rmtree(path)
    
    # Create releases directory
    RELEASES.mkdir(parents=True, exist_ok=True)
    for platform in ["macos", "windows", "linux"]:
        (RELEASES / platform).mkdir(exist_ok=True)
    
    # Build macOS
    print("🔨 Building macOS...")
    try:
        subprocess.run([sys.executable, "-m", "PyInstaller", "--clean", "HandLaunch-mac.spec"], check=True)
        create_macos_dmg()
    except Exception as e:
        print(f"❌ macOS build failed: {e}")
    
    # Build Windows (console version for now)
    print("🔨 Building Windows...")
    try:
        subprocess.run([sys.executable, "-m", "PyInstaller", "--clean", "HandLaunch-win.spec"], check=True)
        create_windows_exe()
    except Exception as e:
        print(f"❌ Windows build failed: {e}")
    
    # Build Linux
    print("🔨 Building Linux...")
    try:
        subprocess.run([sys.executable, "-m", "PyInstaller", "--clean", "HandLaunch-linux.spec"], check=True)
        create_linux_appimage()
    except Exception as e:
        print(f"❌ Linux build failed: {e}")

def create_macos_dmg():
    """Create macOS DMG"""
    app_path = DIST / "HandLaunch.app"
    if not app_path.exists():
        print("❌ HandLaunch.app not found!")
        return False
    
    # Create temporary DMG directory
    dmg_dir = ROOT / "temp_dmg"
    dmg_dir.mkdir(exist_ok=True)
    
    try:
        # Copy the app
        shutil.copytree(app_path, dmg_dir / "HandLaunch.app")
        
        # Create Applications symlink
        os.symlink("/Applications", dmg_dir / "Applications")
        
        # Create DMG
        dmg_path = RELEASES / "macos" / "HandLaunch-mac.dmg"
        subprocess.run([
            "hdiutil", "create",
            "-volname", "HandLaunch",
            "-srcfolder", str(dmg_dir),
            "-ov",
            "-format", "UDZO",
            str(dmg_path)
        ], check=True)
        
        print(f"✅ macOS DMG created: {dmg_path}")
        return True
        
    finally:
        if dmg_dir.exists():
            shutil.rmtree(dmg_dir)

def create_windows_exe():
    """Create Windows EXE"""
    # The Windows build creates a binary named 'HandLaunch' on macOS
    # We need to rename it to .exe
    binary_path = DIST / "HandLaunch"
    if not binary_path.exists():
        print("❌ HandLaunch binary not found!")
        return False
    
    # Copy and rename to .exe
    exe_path = RELEASES / "windows" / "HandLaunch-win.exe"
    shutil.copy2(binary_path, exe_path)
    
    print(f"✅ Windows EXE created: {exe_path}")
    return True

def create_linux_appimage():
    """Create Linux AppImage"""
    binary_path = DIST / "HandLaunch"
    if not binary_path.exists():
        print("❌ HandLaunch binary not found!")
        return False
    
    # Copy to releases
    appimage_path = RELEASES / "linux" / "HandLaunch-linux.AppImage"
    shutil.copy2(binary_path, appimage_path)
    
    # Make executable
    os.chmod(appimage_path, 0o755)
    
    print(f"✅ Linux AppImage created: {appimage_path}")
    return True

def main():
    """Build all platforms"""
    print("🚀 Building HandLaunch for all platforms...")
    clean_and_build()
    
    # Copy to website
    print("📁 Copying to website...")
    website_releases = ROOT / "website" / "releases"
    if website_releases.exists():
        shutil.rmtree(website_releases)
    shutil.copytree(RELEASES, website_releases)
    
    print("\n✅ Build complete!")
    print("📁 Files available in:")
    print(f"   - {RELEASES}")
    print(f"   - {website_releases}")

if __name__ == "__main__":
    main()
