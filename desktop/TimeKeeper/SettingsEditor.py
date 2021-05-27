#!/usr/bin/env python3

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class SettingsEditor(QWidget):
    def __init__(self, settings: QSettings, parent=None):
        super().__init__(parent)
        self.settings = settings

        layout = QVBoxLayout(self)

        self.sel_host = QComboBox()
        self.sel_host.addItem('(no hosts found so far)')
        self.sel_host.setEnabled(False)
        self.sel_host.currentIndexChanged.connect(self.store_settings)
        layout.addWidget(self.sel_host)
        self.hosts_found = False

        layout.addStretch()

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
        if self.hosts_found:
            self.settings.setValue('host', self.sel_host.currentText())
        self.settings.endGroup()

    @pyqtSlot(str)
    def new_host(self, name: str):
        if not self.hosts_found:
            self.hosts_found = True
            self.sel_host.clear()
            self.sel_host.setEnabled(True)
        for i in range(self.sel_host.count()):
            existing_name = self.sel_host.itemText(i)
            if existing_name == name:
                return
        self.sel_host.addItem(name)
        self.load_settings()

    def get_host_name(self):
        if self.hosts_found:
            return self.sel_host.currentText()
        else:
            return None
