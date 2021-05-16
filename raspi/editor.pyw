#!/usr/bin/env python3

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtNetwork import *
from TimeKeeper import DB


class Network(QObject):
    host_found = pyqtSignal(str, QHostAddress, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ask_sockets = []
        self.search_timer = QTimer()
        self.search_timer.setInterval(2000)
        self.search_timer.timeout.connect(self.continue_asking)

        self.host_socket = QTcpSocket(self)

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
        self.host_socket.connected.connect(self.connection_test)
        self.host_socket.readyRead.connect(self.read)

    @pyqtSlot()
    def connection_test(self):
        self.host_socket.write('ping'.encode())

    @pyqtSlot()
    def read(self):
        size = self.host_socket.bytesAvailable()
        data = self.host_socket.read(size)
        text = data.decode()
        print(f'got answer: {text}')


class Form(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings()
        self.setWindowTitle('TimeKeeper Editor')

        layout = QVBoxLayout(self)

        lay_conn = QHBoxLayout()
        layout.addLayout(lay_conn)
        self.selector = QComboBox()
        self.selector.addItem('Searching for TimeKeeper...')
        self.selector.setEnabled(False)
        lay_conn.addWidget(self.selector)
        self.btn_connect = QPushButton('&Connect')
        self.btn_connect.setEnabled(False)
        self.btn_connect.clicked.connect(self.establish_connection)
        lay_conn.addWidget(self.btn_connect)

        self.editor = QPlainTextEdit()
        self.editor.setReadOnly(True)
        self.editor.setUndoRedoEnabled(False)
        layout.addWidget(self.editor)

        btn_layout = QHBoxLayout()
        layout.addLayout(btn_layout)

        self.btn_read = QPushButton('Read')
        self.btn_read.clicked.connect(self.read_db)
        btn_layout.addWidget(self.btn_read)
        self.btn_quit = QPushButton('Quit')
        self.btn_quit.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_quit)

        self.db = DB(self, 'timekeeper.db')

        self.network = Network(self)
        self.network.host_found.connect(self.new_host_found)
        self.network.start_asking()

        self.resize(self.settings.value('windowSize', QSize(50, 50)))
        self.move(self.settings.value('windowPosition', QPoint(50, 50)))

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.settings.setValue('windowSize', self.size())
        self.settings.setValue('windowPosition', self.pos())

    @pyqtSlot()
    def read_db(self):
        data = self.db.get_events_between_timestamps(0, QDateTime.currentDateTime().toSecsSinceEpoch())
        for line in data:
            line_str = '|'.join(line)
            self.editor.appendPlainText(line_str)

    @pyqtSlot(str, QHostAddress, int)
    def new_host_found(self, name: str, address: QHostAddress, port: int):
        if not self.selector.isEnabled():     # TODO: find another indicator for empty list since selector gets disabled when in use, too
            self.selector.clear()
            self.selector.setEnabled(True)
            self.btn_connect.setEnabled(True)
        already_existing = False
        for i in range(self.selector.count()):
            existing_name = self.selector.itemText(i)
            if existing_name == name:
                already_existing = True
                self.network.stop_asking()
                break
        if not already_existing:
            self.selector.addItem(name, (address, port))

    @pyqtSlot()
    def establish_connection(self):
        address, port = self.selector.currentData(Qt.UserRole)
        self.network.connect_to_host(address, port)
        self.selector.setEnabled(False)
        self.btn_connect.setEnabled(False)


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
