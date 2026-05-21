"""Device manager scaffold.

Holds a list of connected/known devices and provides simple discovery APIs.
"""
from PyQt6.QtCore import QObject, pyqtSignal
import subprocess
import shutil


class DeviceManager(QObject):
    devicesChanged = pyqtSignal()

    def __init__(self, adb_path='adb', parent=None):
        super().__init__(parent)
        self.adb_path = adb_path
        self.devices = []  # list of device ids / dicts

    def list_android_devices(self):
        """Return a list of device ids from `adb devices` (scaffolded)."""
        if shutil.which(self.adb_path) is None:
            return []
        try:
            out = subprocess.check_output([self.adb_path, 'devices'], universal_newlines=True, stderr=subprocess.DEVNULL)
            lines = out.splitlines()[1:]
            devices = []
            for l in lines:
                l = l.strip()
                if not l:
                    continue
                parts = l.split('\t')
                if parts:
                    devices.append(parts[0])
            self.devices = devices
            self.devicesChanged.emit()
            return devices
        except Exception:
            return []
