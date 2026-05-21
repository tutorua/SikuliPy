"""Devices pane UI scaffold — lists devices and allows connect/disconnect actions."""
from PyQt6.QtWidgets import QDockWidget, QWidget, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from sikulipy.devices.device_manager import DeviceManager


class DevicesPane(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Devices", parent)
        self.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)

        container = QWidget()
        layout = QVBoxLayout(container)

        self.device_list = QListWidget()
        layout.addWidget(QLabel("Connected Devices:"))
        layout.addWidget(self.device_list)

        btn_bar = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh")
        self.connect_btn = QPushButton("Connect")
        btn_bar.addWidget(self.refresh_btn)
        btn_bar.addWidget(self.connect_btn)
        layout.addLayout(btn_bar)

        container.setLayout(layout)
        self.setWidget(container)

        self.manager = DeviceManager()
        self.refresh_btn.clicked.connect(self.refresh)
        self.connect_btn.clicked.connect(self.on_connect)

    def refresh(self):
        devices = self.manager.list_android_devices()
        self.device_list.clear()
        for d in devices:
            self.device_list.addItem(d)

    def on_connect(self):
        item = self.device_list.currentItem()
        if not item:
            return
        device_id = item.text()
        # placeholder: user may double-click or press a connect button to open stream
        print(f"Connect to device: {device_id}")
