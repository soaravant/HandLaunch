#!/usr/bin/env python3
"""
Copies latest built artifacts into website/downloads for Vercel static hosting.
Assumes PyInstaller onefile outputs in dist/.
"""
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
OUT = ROOT / "website" / "downloads"

OUT.mkdir(parents=True, exist_ok=True)

def copy_if_exists(src: Path, dest: Path):
    if src.exists():
        print(f"Copy {src} -> {dest}")
        shutil.copy2(src, dest)
        return True
    return False

def main():
    # Windows exe (if built on Windows CI)
    copy_if_exists(DIST / "HandLaunch.exe", OUT / "HandLaunch-win.exe")

    # macOS onefile binary -> zip as HandLaunch-mac.zip
    mac_bin = DIST / "HandLaunch"
    if mac_bin.exists():
        zip_path = OUT / "HandLaunch-mac.zip"
        print(f"Zipping {mac_bin} -> {zip_path}")
        with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            zf.write(mac_bin, arcname="HandLaunch")

    # Linux artifact would be created on Linux CI; copy if present
    # Expect either AppImage or tar.gz in dist/
    for candidate in ["HandLaunch.AppImage", "HandLaunch-linux.tar.gz"]:
        p = DIST / candidate
        if p.exists():
            copy_if_exists(p, OUT / p.name)

    print("Done. Files placed in website/downloads/.")

if __name__ == "__main__":
    main()


