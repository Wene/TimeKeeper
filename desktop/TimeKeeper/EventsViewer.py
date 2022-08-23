#!/usr/bin/env python3

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from os import path


class EventsViewer(QWidget):
    update_request = pyqtSignal(int, int)

    def __init__(self, settings: QSettings, parent=None):
        super().__init__(parent)
        self.settings = settings

        layout = QVBoxLayout(self)

        self.edt_text_filter = QLineEdit()
        self.edt_text_filter.setPlaceholderText(self.tr('Filter'))
        self.edt_text_filter.setToolTip(self.tr('<p>If a filter is entered, only lines containing the filter text get '
                                                'loaded. If the filter is empty, everything gets loaded.</p>'))
        self.edt_text_filter.textEdited.connect(self.text_filter_edited)
        layout.addWidget(self.edt_text_filter)

        # Filter section
        lay_filter = QHBoxLayout()
        layout.addLayout(lay_filter)
        today = QDate.currentDate()
        month_start = QDate(today.year(), today.month(), 1)

        self.sel_date_from = QDateEdit()
        self.sel_date_from.setToolTip(self.tr('Filter date starting with this date'))
        self.sel_date_from.setCalendarPopup(True)
        self.sel_date_from.setDate(month_start)
        lay_filter.addWidget(self.sel_date_from)

        self.sel_date_to = QDateEdit()
        self.sel_date_to.setToolTip(self.tr('Filter date ending with this date'))
        self.sel_date_to.setCalendarPopup(True)
        self.sel_date_to.setDate(today)
        lay_filter.addWidget(self.sel_date_to)

        self.update_unfiltered_text = self.tr('Update unfiltered')
        self.update_filtered_text = self.tr('Update filtered')
        self.btn_update = QPushButton(self.update_unfiltered_text)
        self.btn_update.clicked.connect(self.update)
        lay_filter.addWidget(self.btn_update)

        # Export button
        self.btn_export = QPushButton(self.tr('Export'))
        self.btn_export.clicked.connect(self.export)
        layout.addWidget(self.btn_export)

        # Content view
        self.content = QPlainTextEdit()
        self.content.setReadOnly(True)
        self.content.setUndoRedoEnabled(False)
        layout.addWidget(self.content)

        # Initialize settings
        self.enable(False)

    @pyqtSlot()
    def text_filter_edited(self):
        filter_text = self.edt_text_filter.text()
        if filter_text:
            self.btn_update.setText(self.update_filtered_text)
        else:
            self.btn_update.setText(self.update_unfiltered_text)

    @pyqtSlot()
    def update(self):
        date_from: QDate = self.sel_date_from.date()
        time_from = date_from.startOfDay().toSecsSinceEpoch()
        date_to: QDate = self.sel_date_to.date()
        time_to = date_to.endOfDay().toSecsSinceEpoch()
        self.update_request.emit(time_from, time_to)

    @pyqtSlot()
    def export(self):
        self.settings.beginGroup('EventsViewer')
        last_export_path = self.settings.value('last_path', '')
        file_path, _ = QFileDialog.getSaveFileName(self, self.tr('Save file as'),
                                                   last_export_path,
                                                   self.tr('Tab separated files (*.tsv);;All files (*.*)'))
        if file_path:
            last_export_path, file_name = path.split(file_path)
            self.settings.setValue('last_path', last_export_path)

            with open(file_path, 'w') as f:
                f.write(self.content.toPlainText())

        self.settings.endGroup()

    @pyqtSlot(list)
    def display_data(self, data: list):
        self.content.clear()
        filter_text = self.edt_text_filter.text()
        for line in data:
            if filter_text:
                if filter_text.casefold() in line.casefold():
                    self.content.appendPlainText(line)
            else:
                self.content.appendPlainText(line)

    @pyqtSlot(bool)
    def enable(self, en: bool):
        self.sel_date_from.setEnabled(en)
        self.sel_date_to.setEnabled(en)
        self.btn_update.setEnabled(en)
        self.btn_export.setEnabled(en)
