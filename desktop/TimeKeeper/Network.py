#!/usr/bin/env python3

from PyQt5.QtCore import *
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

        self.secret = ''

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

    def connect_to_host(self, address: QHostAddress, port: int, secret: str):
        self.host_socket.connectToHost(address, port)
        self.host_socket.readyRead.connect(self.read)
        self.secret = secret

    @pyqtSlot()
    def close_connection(self):
        self.host_socket.close()

    @pyqtSlot(int, int)
    def get_events(self, time_from=0, time_to=None):
        if time_to is None:
            time_to = QDateTime.currentDateTime().toSecsSinceEpoch()
        self.host_socket.write(f'get events between {time_from} and {time_to}\n'.encode())

    @pyqtSlot()
    def get_owner(self):
        self.host_socket.write('get owners\n'.encode())

    @pyqtSlot(str, str, int)
    def set_owner(self, badge_hex: str, name: str, valid_since: int):
        self.host_socket.write(f'set owner of {badge_hex} to "{name}" valid since {valid_since}\n'.encode())

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
