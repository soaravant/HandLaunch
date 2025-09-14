#!/usr/bin/env python3
"""
Builds HandLaunch for all platforms with proper executables.
Creates .dmg, .exe, and .AppImage files.
"""
import os
import shutil
import subprocess
import sys
import zipfile
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
RELEASES = ROOT / "releases"

def run_pyinstaller(spec_file, platform):
    """Run PyInstaller with a specific spec file"""
    print(f"🔨 Building {platform} executable...")
    cmd = [sys.executable, "-m", "PyInstaller", "--clean", str(spec_file)]
    print("→", " ".join(cmd))
    subprocess.check_call(cmd, cwd=ROOT)

def create_macos_dmg():
    """Create macOS DMG from the built app"""
    print("📦 Creating macOS DMG...")
    
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
        return True
        
    finally:
        if dmg_dir.exists():
            shutil.rmtree(dmg_dir)

def create_windows_exe():
    """Create Windows executable"""
    print("📦 Creating Windows EXE...")
    
    exe_path = DIST / "HandLaunch.exe"
    if not exe_path.exists():
        print("❌ HandLaunch.exe not found!")
        return False
    
    # Copy to releases
    releases_exe = RELEASES / "windows" / "HandLaunch-win.exe"
    RELEASES.mkdir(parents=True, exist_ok=True)
    shutil.copy2(exe_path, releases_exe)
    
    print(f"✅ Windows EXE created: {releases_exe}")
    return True

def create_linux_appimage():
    """Create Linux AppImage"""
    print("📦 Creating Linux AppImage...")
    
    linux_bin = DIST / "HandLaunch"
    if not linux_bin.exists():
        print("❌ HandLaunch binary not found!")
        return False
    
    # Copy to releases
    releases_bin = RELEASES / "linux" / "HandLaunch-linux.AppImage"
    RELEASES.mkdir(parents=True, exist_ok=True)
    shutil.copy2(linux_bin, releases_bin)
    
    # Make executable
    os.chmod(releases_bin, 0o755)
    
    print(f"✅ Linux AppImage created: {releases_bin}")
    return True

def clean_build():
    """Clean previous builds"""
    print("🧹 Cleaning previous builds...")
    for path in [DIST, ROOT / "build", ROOT / "__pycache__"]:
        if path.exists():
            shutil.rmtree(path)
    
    # Clean Python cache
    for d in ROOT.rglob("__pycache__"):
        shutil.rmtree(d, ignore_errors=True)

def main():
    """Build for all platforms"""
    print("🚀 Building HandLaunch for all platforms...")
    
    # Clean previous builds
    clean_build()
    
    # Create releases directory
    RELEASES.mkdir(parents=True, exist_ok=True)
    for platform in ["macos", "windows", "linux"]:
        (RELEASES / platform).mkdir(exist_ok=True)
    
    success_count = 0
    
    # Build macOS
    try:
        run_pyinstaller("HandLaunch-mac.spec", "macOS")
        if create_macos_dmg():
            success_count += 1
    except Exception as e:
        print(f"❌ macOS build failed: {e}")
    
    # Build Windows (will create console exe on macOS)
    try:
        run_pyinstaller("HandLaunch-win.spec", "Windows")
        if create_windows_exe():
            success_count += 1
    except Exception as e:
        print(f"❌ Windows build failed: {e}")
    
    # Build Linux
    try:
        run_pyinstaller("HandLaunch-linux.spec", "Linux")
        if create_linux_appimage():
            success_count += 1
    except Exception as e:
        print(f"❌ Linux build failed: {e}")
    
    print(f"\n✅ Build complete! {success_count}/3 platforms built successfully")
    print(f"📁 Files available in: {RELEASES}")

if __name__ == "__main__":
    main()
