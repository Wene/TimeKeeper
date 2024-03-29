#!/usr/bin/env python3

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class SettingsEditor(QWidget):
    host_selected = pyqtSignal(tuple, str)
    host_removed = pyqtSignal()

    def __init__(self, settings: QSettings, parent=None):
        super().__init__(parent)
        self.settings = settings

        layout = QVBoxLayout(self)

        self.sel_lang = QComboBox()
        self.sel_lang.addItem(self.tr('English'), 'en')
        self.sel_lang.addItem(self.tr('German'), 'de')
        self.sel_lang.setToolTip(self.tr('Restart application to apply changed language setting.'))
        lay_lang = QHBoxLayout()
        lay_lang.addWidget(self.sel_lang)
        grp_lang = QGroupBox(self.tr('Language'))
        grp_lang.setLayout(lay_lang)
        layout.addWidget(grp_lang)

        grp_conn = QGroupBox(self.tr('Default connection'))
        lay_conn = QVBoxLayout()
        grp_conn.setLayout(lay_conn)
        layout.addWidget(grp_conn)

        self.sel_host = QComboBox()
        self.sel_host.addItem(self.tr('(none)'), None)
        lay_conn.addWidget(self.sel_host)

        lay_secret = QHBoxLayout()
        lay_conn.addLayout(lay_secret)
        self.edt_secret = QLineEdit()
        self.edt_secret.setEchoMode(QLineEdit.Password)
        self.edt_secret.editingFinished.connect(self.store_settings)
        lay_secret.addWidget(self.edt_secret)
        self.chk_show = QCheckBox(self.tr('Show'))
        self.chk_show.setChecked(False)
        self.chk_show.stateChanged.connect(self.show_secret)
        lay_secret.addWidget(self.chk_show)

        layout.addStretch()

        self.load_settings()
        self.sel_lang.currentIndexChanged.connect(self.store_settings)
        self.sel_host.textActivated.connect(self.store_settings)
        self.sel_host.currentIndexChanged.connect(self.process_selection)

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
            self.host_selected.emit(data, self.edt_secret.text())
        else:
            self.host_removed.emit()

    def load_settings(self):
        self.settings.beginGroup('Settings')
        language = self.settings.value('language', 'en')
        host = self.settings.value('host', None)
        self.edt_secret.setText(self.settings.value('secret', ''))
        self.settings.endGroup()
        if host:
            for i in range(self.sel_host.count()):
                if self.sel_host.itemText(i) == host:
                    self.sel_host.setCurrentIndex(i)
                    break
        for i in range(self.sel_lang.count()):
            if self.sel_lang.itemData(i) == language:
                self.sel_lang.setCurrentIndex(i)
                break

    @pyqtSlot()
    def store_settings(self):
        self.settings.beginGroup('Settings')
        if self.sel_host.currentData(Qt.UserRole):
            self.settings.setValue('host', self.sel_host.currentText())
        else:
            self.settings.remove('host')
        self.settings.setValue('language', self.sel_lang.currentData(Qt.UserRole))
        self.settings.setValue('secret', self.edt_secret.text())
        self.settings.endGroup()

    @pyqtSlot(str, tuple)
    def new_host(self, name: str, data: tuple):
        for i in range(self.sel_host.count()):
            existing_name = self.sel_host.itemText(i)
            if existing_name == name:
                return
        self.sel_host.addItem(name, data)
        self.load_settings()
