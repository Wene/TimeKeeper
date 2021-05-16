#!/usr/bin/env python3

import re
from PyQt5.QtCore import *
from PyQt5.QtNetwork import *


class Response(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

    @pyqtSlot(QByteArray)
    def answer(self, data: QByteArray):
        # TODO: send the data somehow
        pass


class Connection(QObject):
    def __init__(self, socket: QTcpSocket, parent=None):
        super().__init__(parent)
        self.socket = socket
        self.socket.readyRead.connect(self.read)
        self.socket.disconnected.connect(self.cleanup)

        self.address = self.socket.peerAddress()
        self.port = self.socket.peerPort()
        print(f'new connection established to [{self.address.toString()}]:{self.port}')

    def parse_request(self, request: str):
        match = re.match(r'get events between (\d+) and (\d+)', request)
        if match:
            from_time = int(match.group(1))
            to_time = int(match.group(2))
            response = Response(self)
            # TODO: do something to request the data
            # TODO: connect whatever providing the answer with to response.answer
            return True
        else:
            return False

    @pyqtSlot()
    def read(self):
        size = self.socket.bytesAvailable()
        if size > 0:
            data = self.socket.read(size)
            text = data.decode()
            answer = 'unknown request'
            if 'ping' == text:
                answer = 'pong'
            elif text.startswith('get'):
                result = self.parse_request(text)
                if result:
                    answer = 'processing...'
                else:
                    answer = 'request failed'
            self.socket.write(answer.encode())

    @pyqtSlot()
    def cleanup(self):
        print(f'connection to [{self.address.toString()}]:{self.port} got disconnected')
        self.deleteLater()

    @pyqtSlot()
    def close(self):
        self.socket.close()


class Server(QObject):
    def __init__(self, name: str, parent=None):
        super().__init__(parent)
        self.mcast_listener = QUdpSocket(self)
        self.mcast_listener.bind(QHostAddress.Any, 9363)
        self.mcast_listener.readyRead.connect(self.incoming)

        self.name = name

        self.tcp_server = QTcpServer(self)
        self.tcp_server.listen(QHostAddress.Any, 9363)
        self.tcp_server.newConnection.connect(self.connect)

    @pyqtSlot()
    def incoming(self):
        while self.mcast_listener.hasPendingDatagrams():
            data = self.mcast_listener.receiveDatagram()
            text = str(data.data(), encoding='utf8')
            sender = data.senderAddress()
            port = data.senderPort()
            print(f'got "{text.rstrip()}" from [{sender.toString()}]:{port}')
            if 'I\'m looking for TimeKeeper hosts.' == text:
                self.mcast_listener.writeDatagram(f'Hi, this is TimeKeeper {self.name}'.encode('utf8'), sender, port)

    @pyqtSlot()
    def connect(self):
        while self.tcp_server.hasPendingConnections():
            socket = self.tcp_server.nextPendingConnection()
            Connection(socket, self)    # by setting self as parent, this instance will last until self gets deleted
