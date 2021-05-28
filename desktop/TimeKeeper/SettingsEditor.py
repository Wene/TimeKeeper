#!/usr/bin/env python3

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class SettingsEditor(QWidget):
    host_selected = pyqtSignal(tuple)

    def __init__(self, settings: QSettings, parent=None):
        super().__init__(parent)
        self.settings = settings

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel('Default connection'))

        self.sel_host = QComboBox()
        self.sel_host.addItem('(none)', None)
        self.sel_host.currentIndexChanged.connect(self.store_settings)
        self.sel_host.currentIndexChanged.connect(self.process_selection)
        layout.addWidget(self.sel_host)

        layout.addStretch()

    @pyqtSlot()
    def process_selection(self):
        data = self.sel_host.currentData(Qt.UserRole)
        if data:
            self.host_selected.emit(data)

    @pyqtSlot()
    def load_settings(self):
        self.settings.beginGroup('Settings')
        host = self.settings.value('host', None)
        if host:
            for i in range(self.sel_host.count()):
                if self.sel_host.itemText(i) == host:
                    self.sel_host.setCurrentIndex(i)
        self.settings.endGroup()

    @pyqtSlot()
    def store_settings(self):
        self.settings.beginGroup('Settings')
        self.settings.setValue('host', self.sel_host.currentText())
        self.settings.endGroup()

    @pyqtSlot(str, tuple)
    def new_host(self, name: str, data: tuple):
        for i in range(self.sel_host.count()):
            existing_name = self.sel_host.itemText(i)
            if existing_name == name:
                return
        self.sel_host.addItem(name, data)
        self.load_settings()
