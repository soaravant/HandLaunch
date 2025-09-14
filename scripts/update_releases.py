#!/usr/bin/env python3
"""
Updates the releases folder with the latest built artifacts.
Run this after building the application to update the website downloads.
"""
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
WEBSITE_RELEASES = ROOT / "website" / "releases"

def main():
    """Update releases with latest builds"""
    print("🔄 Updating releases with latest builds...")
    
    # Run the installer creation script
    subprocess.run([ROOT / "venv" / "bin" / "python3", "scripts/create_installers.py"], check=True)
    
    # Copy releases to website
    if WEBSITE_RELEASES.exists():
        shutil.rmtree(WEBSITE_RELEASES)
    
    shutil.copytree(ROOT / "releases", WEBSITE_RELEASES)
    
    print("✅ Releases updated successfully!")
    print(f"📁 Website releases available at: {WEBSITE_RELEASES}")

if __name__ == "__main__":
    main()
