"""
Dev autoreload runner using watchdog.

Starts the app and restarts it on source file changes.
"""

import os
import sys
import time
import signal
import threading
import subprocess
from pathlib import Path


def run_with_reloader():
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except Exception:
        print("Please install watchdog: pip install watchdog")
        sys.exit(1)

    project_root = Path(__file__).resolve().parent.parent
    src_dir = project_root / "src"

    process = None
    restart_lock = threading.Lock()
    debounce_timer = None

    def start_app():
        nonlocal process
        if process and process.poll() is None:
            return
        env = os.environ.copy()
        # Start child in its own process group so we can terminate cleanly
        process = subprocess.Popen(
            [sys.executable, str(src_dir / "main.py")],
            start_new_session=True
        )

    def restart_app():
        nonlocal process
        with restart_lock:
            # Kill existing app if running
            if process and process.poll() is None:
                try:
                    # Terminate the whole process group
                    os.killpg(process.pid, signal.SIGTERM)
                    # Wait up to 5s for graceful exit
                    for _ in range(50):
                        if process.poll() is not None:
                            break
                        time.sleep(0.1)
                    # Force kill if still alive
                    if process.poll() is None:
                        os.killpg(process.pid, signal.SIGKILL)
                except Exception:
                    try:
                        process.terminate()
                        process.wait(timeout=2)
                    except Exception:
                        pass
            start_app()

    class ChangeHandler(FileSystemEventHandler):
        def on_any_event(self, event):
            nonlocal debounce_timer
            if event.is_directory:
                return
            if not any(event.src_path.endswith(ext) for ext in [".py", ".ui", ".qss"]):
                return
            # Debounce rapid successive events
            def _do_restart():
                print(f"Change detected: {event.src_path}. Restarting...")
                restart_app()
            if debounce_timer and debounce_timer.is_alive():
                debounce_timer.cancel()
            debounce_timer = threading.Timer(0.3, _do_restart)
            debounce_timer.start()

    observer = Observer()
    observer.schedule(ChangeHandler(), str(src_dir), recursive=True)
    observer.start()

    try:
        start_app()
        while True:
            observer.join(1)
    except KeyboardInterrupt:
        observer.stop()
    finally:
        observer.stop()
        observer.join()
        if process and process.poll() is None:
            process.terminate()


if __name__ == "__main__":
    run_with_reloader()


