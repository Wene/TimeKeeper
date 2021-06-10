#!/usr/bin/env python3

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class SettingsEditor(QWidget):
    host_selected = pyqtSignal(tuple)
    host_removed = pyqtSignal()

    def __init__(self, settings: QSettings, parent=None):
        super().__init__(parent)
        self.settings = settings

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel('Default connection'))

        self.sel_host = QComboBox()
        self.sel_host.addItem('(none)', None)
        self.sel_host.textActivated.connect(self.store_settings)
        self.sel_host.currentIndexChanged.connect(self.process_selection)
        layout.addWidget(self.sel_host)

        lay_secret = QHBoxLayout()
        layout.addLayout(lay_secret)
        self.edt_secret = QLineEdit()
        self.edt_secret.setEchoMode(QLineEdit.Password)
        lay_secret.addWidget(self.edt_secret)
        self.chk_show = QCheckBox('Show')
        self.chk_show.setChecked(False)
        self.chk_show.stateChanged.connect(self.show_secret)
        lay_secret.addWidget(self.chk_show)

        layout.addStretch()

    @pyqtSlot()
    def show_secret(self):
        if self.chk_show.isChecked():
            self.edt_secret.setEchoMode(QLineEdit.Normal)
        else:
            self.edt_secret.setEchoMode(QLineEdit.Password)

    @pyqtSlot()
    def process_selection(self):
        data = self.sel_host.currentData(Qt.UserRole)
        if data:
            self.host_selected.emit(data)
        else:
            self.host_removed.emit()

    @pyqtSlot()
    def load_settings(self):
        self.settings.beginGroup('Settings')
        host = self.settings.value('host', None)
        self.settings.endGroup()
        if host:
            for i in range(self.sel_host.count()):
                if self.sel_host.itemText(i) == host:
                    self.sel_host.setCurrentIndex(i)

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
