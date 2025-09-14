#!/usr/bin/env python3
"""
PyInstaller build script for HandLaunch.

Builds macOS, Windows, and Linux binaries, placing artifacts in dist/.

Usage:
  python scripts/build.py --target macos|windows|linux|all --clean
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
DIST = ROOT / "dist"


def run(py_args: list[str]):
    """Run PyInstaller via current interpreter to avoid PATH issues."""
    cmd = [sys.executable, "-m", "PyInstaller", *py_args]
    print("→", " ".join(cmd))
    subprocess.check_call(cmd)


def clean():
    for p in [DIST, ROOT / "build", ROOT / "__pycache__"]:
        if p.exists():
            shutil.rmtree(p)
    for d in SRC.rglob("__pycache__"):
        shutil.rmtree(d, ignore_errors=True)


def build_common_args():
    return [
        "--name", "HandLaunch",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--add-data", f"data{os.pathsep}data",
        "--add-data", f"resources{os.pathsep}resources",
    ]


def build_macos():
    args = [
        *build_common_args(),
        "--windowed",
        str(SRC / "main.py"),
    ]
    run(args)


def build_windows():
    args = [
        *build_common_args(),
        "--windowed",
        str(SRC / "main.py"),
    ]
    run(args)


def build_linux():
    args = [
        *build_common_args(),
        str(SRC / "main.py"),
    ]
    run(args)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", choices=["macos", "windows", "linux", "all"], default="all")
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()

    if args.clean:
        clean()

    DIST.mkdir(parents=True, exist_ok=True)

    if args.target in ("macos", "all"):
        build_macos()
    if args.target in ("windows", "all"):
        build_windows()
    if args.target in ("linux", "all"):
        build_linux()

    # Move artifacts into dist/
    built = ROOT / "dist"
    built.mkdir(exist_ok=True)
    # PyInstaller puts files in dist/HandLaunch on macOS/Linux when not onefile; onefile outputs dist/HandLaunch
    # We'll just leave outputs where they are. Optionally rename here if needed.
    print("Build complete. See dist/ for artifacts.")


if __name__ == "__main__":
    main()


