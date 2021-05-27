#!/usr/bin/env python3

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from TimeKeeper import EventsViewer, OwnerEditor, SettingsEditor, Network


class MainForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings()
        self.setWindowTitle('TimeKeeper Client')

        self.network = Network(self)

        layout = QVBoxLayout(self)

        events = EventsViewer()
        owner = OwnerEditor()
        self.settings_widget = SettingsEditor(self.settings, self)

        tabs = QTabWidget()
        layout.addWidget(tabs)
        tabs.addTab(events, 'Events')
        tabs.addTab(owner, 'Owner')
        tabs.addTab(self.settings_widget, 'Settings')

        self.load_settings()

    def load_settings(self):
        self.resize(self.settings.value('windowSize', QSize(50, 50)))
        self.move(self.settings.value('windowPosition', QPoint(50, 50)))

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.settings.setValue('windowSize', self.size())
        self.settings.setValue('windowPosition', self.pos())


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    app.setOrganizationName('Wene')
    app.setApplicationName('TimeKeeper_client')

    translator = QTranslator()
    lib_path = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
    translator.load("qt_de.qm", lib_path)
    translator.load("qtbase_de.qm", lib_path)
    app.installTranslator(translator)

    window = MainForm()
    window.show()

    app.exec()
