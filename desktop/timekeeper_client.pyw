#!/usr/bin/env python3

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtNetwork import *
from TimeKeeper import EventsViewer, OwnerEditor, SettingsEditor, Network


class MainForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings()
        self.setWindowTitle('TimeKeeper Client')

        self.network = Network(self)
        self.network.host_found.connect(self.new_host)
        self.network.connected.connect(self.network_connected)
        self.network.disconnected.connect(self.network_disconnected)

        layout = QVBoxLayout(self)

        self.events = EventsViewer(self.settings)
        self.events.update_request.connect(self.network.get_events)
        self.network.new_data.connect(self.distinguish_data)

        self.owner = OwnerEditor()
        self.owner.request_owners_list.connect(self.network.get_owner)
        self.owner.new_owner.connect(self.debug_print_new_owner)

        self.settings_widget = SettingsEditor(self.settings)
        self.settings_widget.host_selected.connect(self.network.stop_asking)
        self.settings_widget.host_selected.connect(self.connect_to_host)
        self.settings_widget.host_removed.connect(self.network.close_connection)

        tabs = QTabWidget()
        layout.addWidget(tabs)
        tabs.addTab(self.events, 'Events')
        tabs.addTab(self.owner, 'Owner')
        tabs.addTab(self.settings_widget, 'Settings')

        self.load_settings()

        self.network.start_asking()

    def load_settings(self):
        self.resize(self.settings.value('windowSize', QSize(50, 50)))
        self.move(self.settings.value('windowPosition', QPoint(50, 50)))

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.settings.setValue('windowSize', self.size())
        self.settings.setValue('windowPosition', self.pos())

    @pyqtSlot(str, str, int)
    def debug_print_new_owner(self, hex_str: str, name: str, timestamp: int):
        print(f'{hex_str}\t{name}\t{timestamp}')

    @pyqtSlot(str, QHostAddress, int)
    def new_host(self, name: str, address: QHostAddress, port: int):
        self.settings_widget.new_host(name, (address, port))

    @pyqtSlot(tuple)
    def connect_to_host(self, data: tuple):
        address = data[0]
        port = data[1]
        self.network.connect_to_host(address, port)

    @pyqtSlot()
    def network_connected(self):
        self.owner.enable(True)
        self.events.enable(True)

    @pyqtSlot()
    def network_disconnected(self):
        self.owner.enable(False)
        self.events.enable(False)

    @pyqtSlot(list)
    def distinguish_data(self, data: list):
        type_name = data.pop(0)
        if '<<< events' == type_name:
            self.events.display_data(data)
        elif '<<< owners' == type_name:
            self.owner.display_owners_list(data)


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
