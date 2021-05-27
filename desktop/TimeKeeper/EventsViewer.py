#!/usr/bin/env python3

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class EventsViewer(QWidget):
    update_request = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        # Filter section
        lay_filter = QHBoxLayout()
        layout.addLayout(lay_filter)
        today = QDate.currentDate()
        month_start = QDate(today.year(), today.month(), 1)

        self.sel_date_from = QDateEdit()
        self.sel_date_from.setToolTip('Filter date starting with this date')
        self.sel_date_from.setCalendarPopup(True)
        self.sel_date_from.setDate(month_start)
        lay_filter.addWidget(self.sel_date_from)

        self.sel_date_to = QDateEdit()
        self.sel_date_to.setToolTip('Filter date ending with this date')
        self.sel_date_to.setCalendarPopup(True)
        self.sel_date_to.setDate(today)
        lay_filter.addWidget(self.sel_date_to)

        self.btn_update = QPushButton('Update')
        self.btn_update.clicked.connect(self.update)
        lay_filter.addWidget(self.btn_update)

        # Export button
        self.btn_export = QPushButton('Export')
        self.btn_export.clicked.connect(self.export)
        layout.addWidget(self.btn_export)

        # Content view
        self.content = QPlainTextEdit()
        self.content.setReadOnly(True)
        self.content.setUndoRedoEnabled(False)
        layout.addWidget(self.content)

    @pyqtSlot()
    def update(self):
        date_from: QDate = self.sel_date_from.date()
        time_from = date_from.startOfDay().toSecsSinceEpoch()
        date_to: QDate = self.sel_date_to.date()
        time_to = date_to.endOfDay().toSecsSinceEpoch()
        self.update_request.emit(time_from, time_to)

    @pyqtSlot()
    def export(self):
        pass

