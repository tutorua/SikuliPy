"""Android bridge stub for Phase 2 device support.

This module provides a lightweight wrapper around adb/scrcpy. It's a scaffold
with start/stop and connection helpers. The implementation will spawn subprocesses
and emit Qt signals for lifecycle and frames.
"""
from PyQt6.QtCore import QObject, pyqtSignal
import subprocess
import threading
import shutil
import os
import time


class AndroidBridge(QObject):
    """Basic Android control bridge (scaffold).

    Signals:
        connected(device_id)
        disconnected(device_id)
        frameReady(pixmap)
        error(message)
    """
    connected = pyqtSignal(str)
    disconnected = pyqtSignal(str)
    frameReady = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, adb_path='adb', scrcpy_path='scrcpy', parent=None):
        super().__init__(parent)
        self.adb_path = adb_path
        self.scrcpy_path = scrcpy_path
        self._scrcpy_proc = None
        self._reader_thread = None
        self._stop_event = threading.Event()

    def is_available(self):
        return shutil.which(self.adb_path) is not None

    def connect_ip(self, ip_port: str, timeout: int = 5):
        """Attempt to connect to device over TCP (adb connect ip:port).

        Returns True on success, False otherwise.
        """
        try:
            subprocess.run([self.adb_path, 'connect', ip_port], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=timeout)
            return True
        except Exception as e:
            self.error.emit(str(e))
            return False

    def start_scrcpy(self, device_id: str = None, args: list = None):
        """Start scrcpy process for the given device.

        This is a scaffold: real implementation should capture frames (via pipe or window embedding)
        and emit `frameReady` with a QImage/QPixmap for the UI.
        """
        if args is None:
            args = []
        cmd = [self.scrcpy_path]
        if device_id:
            cmd += ['-s', device_id]
        cmd += args

        try:
            self._scrcpy_proc = subprocess.Popen(cmd)
        except FileNotFoundError:
            self.error.emit(f"scrcpy not found: {self.scrcpy_path}")
            self._scrcpy_proc = None
        except Exception as e:
            self.error.emit(str(e))
            self._scrcpy_proc = None

    def stop(self):
        try:
            self._stop_event.set()
            if self._scrcpy_proc:
                try:
                    self._scrcpy_proc.terminate()
                    self._scrcpy_proc.wait(timeout=2)
                except Exception:
                    try:
                        self._scrcpy_proc.kill()
                    except Exception:
                        pass
                self._scrcpy_proc = None
        except Exception as e:
            self.error.emit(str(e))

    # placeholder methods for future input injection and file transfer
    def tap(self, x: int, y: int):
        """Inject a tap event via `adb shell input tap x y` (placeholder)."""
        try:
            subprocess.run([self.adb_path, 'shell', 'input', 'tap', str(x), str(y)], check=True)
        except Exception as e:
            self.error.emit(str(e))

    def push(self, local_path: str, remote_path: str):
        try:
            subprocess.run([self.adb_path, 'push', local_path, remote_path], check=True)
        except Exception as e:
            self.error.emit(str(e))
