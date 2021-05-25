#!/usr/bin/env python3

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtNetwork import *


class Network(QObject):
    host_found = pyqtSignal(str, QHostAddress, int)
    disconnected = pyqtSignal()
    connected = pyqtSignal()
    new_data = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ask_sockets = []
        self.search_timer = QTimer()
        self.search_timer.setInterval(2000)
        self.search_timer.timeout.connect(self.continue_asking)

        self.host_socket = QTcpSocket(self)
        self.host_socket.connected.connect(self.connected)
        self.host_socket.disconnected.connect(self.connection_lost)

        self.line_cache = []
        self.text_cache = ''

    def ask(self, sok: QUdpSocket):
        sok.writeDatagram('I\'m looking for TimeKeeper hosts.'.encode('utf8'),
                          QHostAddress('FF02::1'), 9363)

    @pyqtSlot()
    def start_asking(self):
        for address in QNetworkInterface.allAddresses():
            if address.protocol() == QAbstractSocket.IPv6Protocol:
                if address.isLinkLocal():
                    sok = QUdpSocket(self)
                    self.ask_sockets.append(sok)
                    sok.bind(address, 0)
                    sok.readyRead.connect(self.incoming)
                    self.ask(sok)
        self.search_timer.start()

    @pyqtSlot()
    def stop_asking(self):
        self.search_timer.stop()
        sok: QUdpSocket
        for sok in self.ask_sockets:
            sok.close()
        self.ask_sockets.clear()

    @pyqtSlot()
    def continue_asking(self):
        sok: QUdpSocket
        for sok in self.ask_sockets:
            self.ask(sok)

    @pyqtSlot()
    def incoming(self):
        sok: QUdpSocket
        for sok in self.ask_sockets:
            while sok.hasPendingDatagrams():
                data = sok.receiveDatagram()
                sender = data.senderAddress()
                port = data.senderPort()
                text = str(data.data(), encoding='utf8')
                identifier = 'Hi, this is TimeKeeper '
                if text.startswith(identifier):
                    name = text[len(identifier):]
                    self.host_found.emit(name, sender, port)

    def connect_to_host(self, address: QHostAddress, port: int):
        self.host_socket.connectToHost(address, port)
        self.host_socket.readyRead.connect(self.read)

    def close_connection(self):
        self.host_socket.close()

    @pyqtSlot()
    def get_events(self, time_from=0, time_to=None):
        if time_to is None:
            time_to = QDateTime.currentDateTime().toSecsSinceEpoch()
        self.host_socket.write(f'get events between {time_from} and {time_to}'.encode())

    @pyqtSlot()
    def read(self):
        size = self.host_socket.bytesAvailable()
        if size > 0:
            data = self.host_socket.read(size)
            text = self.text_cache + data.decode()
            self.text_cache = ''
            lines = text.split('\n')
            for line in lines:
                if '<<< processing...' == line:
                    self.line_cache.clear()
                elif '<<< done' == line:
                    self.new_data.emit(self.line_cache)
                    self.line_cache.clear()
                elif '' != line:
                    self.line_cache.append(line)
            if '' != lines[-1]:
                self.text_cache = self.line_cache.pop()

    @pyqtSlot()
    def connection_lost(self):
        self.disconnected.emit()


class Form(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings()
        self.setWindowTitle('TimeKeeper Editor')

        layout = QVBoxLayout(self)

        lay_conn = QHBoxLayout()
        layout.addLayout(lay_conn)
        self.sel_host = QComboBox()
        self.sel_host.addItem('Searching for TimeKeeper...')
        self.selector_empty = True
        self.sel_host.setEnabled(False)
        lay_conn.addWidget(self.sel_host)
        self.btn_connect = QPushButton('&Connect')
        self.btn_connect.setCheckable(True)
        self.btn_connect.clicked.connect(self.establish_connection)
        self.btn_connect.setEnabled(False)
        lay_conn.addWidget(self.btn_connect)

        lay_getters = QHBoxLayout()
        layout.addLayout(lay_getters)
        self.sel_from = QDateEdit()
        self.sel_from.setCalendarPopup(True)
        self.sel_from.setDate(QDate.currentDate())
        lay_getters.addWidget(self.sel_from)
        self.sel_to = QDateEdit()
        self.sel_to.setCalendarPopup(True)
        self.sel_to.setDate(QDate.currentDate())
        lay_getters.addWidget(self.sel_to)
        self.btn_get_events = QPushButton('Get Events')
        self.btn_get_events.clicked.connect(self.get_events)
        self.btn_get_events.setEnabled(False)
        lay_getters.addWidget(self.btn_get_events)

        self.editor = QPlainTextEdit()
        self.editor.setReadOnly(True)
        self.editor.setUndoRedoEnabled(False)
        layout.addWidget(self.editor)

        self.btn_quit = QPushButton('Quit')
        self.btn_quit.clicked.connect(self.close)
        layout.addWidget(self.btn_quit)

        self.network = Network(self)
        self.network.host_found.connect(self.new_host_found)
        self.network.start_asking()
        self.network.disconnected.connect(self.connection_closed)
        self.network.new_data.connect(self.show_data)
        self.network.connected.connect(self.connection_established)

        self.resize(self.settings.value('windowSize', QSize(50, 50)))
        self.move(self.settings.value('windowPosition', QPoint(50, 50)))

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.settings.setValue('windowSize', self.size())
        self.settings.setValue('windowPosition', self.pos())

    @pyqtSlot()
    def get_events(self):
        date_from: QDate = self.sel_from.date()
        time_from = date_from.startOfDay().toSecsSinceEpoch()
        date_to: QDate = self.sel_to.date()
        time_to = date_to.endOfDay().toSecsSinceEpoch()
        self.network.get_events(time_from, time_to)

    @pyqtSlot(str, QHostAddress, int)
    def new_host_found(self, name: str, address: QHostAddress, port: int):
        if self.selector_empty:
            self.selector_empty = False
            self.sel_host.clear()
            self.sel_host.setEnabled(True)
            self.btn_connect.setEnabled(True)
        already_existing = False
        for i in range(self.sel_host.count()):
            existing_name = self.sel_host.itemText(i)
            if existing_name == name:
                already_existing = True
                self.network.stop_asking()
                break
        if not already_existing:
            self.sel_host.addItem(name, (address, port))

    @pyqtSlot()
    def establish_connection(self):
        if self.btn_connect.isChecked():
            address, port = self.sel_host.currentData(Qt.UserRole)
            self.network.connect_to_host(address, port)
            self.sel_host.setEnabled(False)
        else:
            self.network.close_connection()

    @pyqtSlot()
    def connection_closed(self):
        self.sel_host.setEnabled(True)
        self.btn_get_events.setEnabled(False)

    @pyqtSlot()
    def connection_established(self):
        self.btn_get_events.setEnabled(True)

    @pyqtSlot(list)
    def show_data(self, lines: list):
        self.editor.clear()
        for line in lines:
            self.editor.appendPlainText(line)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    app.setOrganizationName('Wene')
    app.setApplicationName('TimeKeeper_editor')

    translator = QTranslator()
    lib_path = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
    translator.load("qt_de.qm", lib_path)
    translator.load("qtbase_de.qm", lib_path)
    app.installTranslator(translator)

    window = Form()
    window.show()

    sys.exit(app.exec_())
