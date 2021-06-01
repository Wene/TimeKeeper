#!/usr/bin/env python3

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import re


class OwnerEditor(QWidget):
    new_owner = pyqtSignal(str, str, int)
    request_owners_list = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        self.btn_load = QPushButton('Load all owners')
        self.btn_load.clicked.connect(self.request_owners_list)
        layout.addWidget(self.btn_load)

        self.edt_owner = QPlainTextEdit()
        layout.addWidget(self.edt_owner)

        self.sel_valid = QDateTimeEdit()
        self.sel_valid.setToolTip('New owners will be valid from this time onwards.')
        self.sel_valid.setDateTime(QDateTime.currentDateTime())
        self.sel_valid.setCalendarPopup(True)
        layout.addWidget(self.sel_valid)

        self.btn_store = QPushButton('Store new owners')
        self.btn_store.clicked.connect(self.store_owners)
        layout.addWidget(self.btn_store)

        self.enable(False)

    @pyqtSlot(list)
    def display_owners_list(self, owners: list):
        self.edt_owner.clear()
        for line in owners:
            self.edt_owner.appendPlainText(line)

    @pyqtSlot()
    def store_owners(self):
        full_text = self.edt_owner.toPlainText()
        lines = full_text.split('\n')
        valid_from: QDateTime = self.sel_valid.dateTime()
        timestamp = valid_from.toSecsSinceEpoch()
        for entry in lines:
            match = re.match(r'^(0x)?([0-9a-fA-F]+)\s+(.+)', entry.rstrip())
            if match:
                hex_str = '0x' + match.group(2).lower()
                name = match.group(3)
                self.new_owner.emit(hex_str, name, timestamp)

    @pyqtSlot(bool)
    def enable(self, en: bool):
        self.btn_load.setEnabled(en)
        self.btn_store.setEnabled(en)
        self.sel_valid.setEnabled(en)