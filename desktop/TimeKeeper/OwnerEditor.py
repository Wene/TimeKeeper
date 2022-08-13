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

        self.edt_filter = QLineEdit()
        self.edt_filter.setToolTip(self.tr('<p>If a filter is entered, only lines containing the filter text get '
                                           'loaded. If the filter is empty, everything gets loaded.</p>'))
        self.edt_filter.setPlaceholderText('Filter')
        self.edt_filter.textEdited.connect(self.update_filter)
        layout.addWidget(self.edt_filter)

        self.load_all_text = self.tr('Load all owners')
        self.load_filtered_text = self.tr('Load filtered owners')
        self.btn_load = QPushButton(self.load_all_text)
        self.btn_load.clicked.connect(self.request_owners_list)
        layout.addWidget(self.btn_load)

        self.edt_owner = QPlainTextEdit()
        layout.addWidget(self.edt_owner)

        self.sel_valid = QDateTimeEdit()
        self.sel_valid.setToolTip(self.tr('New owners will be valid from this time onwards.'))
        self.sel_valid.setDateTime(QDateTime.currentDateTime())
        self.sel_valid.setCalendarPopup(True)
        layout.addWidget(self.sel_valid)

        self.btn_store = QPushButton(self.tr('Store new owners'))
        self.btn_store.clicked.connect(self.store_owners)
        layout.addWidget(self.btn_store)

        self.enable(False)

    @pyqtSlot()
    def update_filter(self):
        if self.edt_filter.text():
            self.btn_load.setText(self.load_filtered_text)
        else:
            self.btn_load.setText(self.load_all_text)

    @pyqtSlot(list)
    def display_owners_list(self, owners: list):
        self.edt_owner.clear()
        filter_text = self.edt_filter.text()
        for line in owners:
            if filter_text:
                if filter_text in line:
                    self.edt_owner.appendPlainText(line)
            else:
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