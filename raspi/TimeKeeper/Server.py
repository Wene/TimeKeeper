#!/usr/bin/env python3

import re
from PyQt5.QtCore import *
from PyQt5.QtNetwork import *


class NetRequest(QObject):
    def __init__(self, socket: QTcpSocket, parent=None):
        super().__init__(parent)
        self.socket = socket
        self.type = None
        self.params = []

    def events_request(self, time_from, time_to):
        self.type = 'events'
        self.params.clear()
        self.params.append(time_from)
        self.params.append(time_to)

    def owners_request(self):
        self.type = 'owners'
        self.params.clear()

    def set_owner(self, badge_hex: str, name: str, valid_since: int):
        self.type = 'set owner'
        self.params.clear()
        self.params.append(badge_hex)
        self.params.append(name)
        self.params.append(valid_since)

    def answer(self, text: str):
        self.socket.write(f'<<< {self.type}\n'.encode())
        data = QByteArray(text.encode())
        self.socket.write(data)
        self.socket.write('<<< done\n'.encode())
        self.deleteLater()


class Connection(QObject):
    new_request = pyqtSignal(NetRequest)

    def __init__(self, socket: QTcpSocket, parent=None):
        super().__init__(parent)
        self.socket = socket
        self.socket.readyRead.connect(self.read)
        self.socket.disconnected.connect(self.cleanup)

        self.address = self.socket.peerAddress()
        self.port = self.socket.peerPort()
        print(f'new connection established to [{self.address.toString()}]:{self.port}')

        self.line_buffer = []
        self.text_buffer = ''

    def parse_get_request(self, request: str):
        match = re.match(r'get events between (\d+) and (\d+)', request)
        if match:
            from_time = int(match.group(1))
            to_time = int(match.group(2))
            request = NetRequest(self.socket, self)
            request.events_request(from_time, to_time)
            return request

        match = re.match(r'get owners', request)
        if match:
            request = NetRequest(self.socket, self)
            request.owners_request()
            return request

        return None

    def process_set_request(self, request: str):
        match = re.match(r'set owner of (\w+) to "(.+)" valid since (\d+)', request)
        if match:
            badge_hex = match.group(1)
            name = match.group(2)
            valid_since = int(match.group(3))
            request = NetRequest(self.socket, self)
            request.set_owner(badge_hex, name, valid_since)
            self.new_request.emit(request)

    @pyqtSlot()
    def read(self):
        size = self.socket.bytesAvailable()
        if size > 0:
            data = self.socket.read(size)
            text = self.text_buffer + data.decode()
            self.text_buffer = ''
            lines = text.split('\n')
            self.line_buffer += lines[:-1]
            if '' != lines[-1]:
                self.text_buffer = lines[-1]
            if 0 < len(self.line_buffer):
                self.process_lines()

    def process_lines(self):
        while 0 < len(self.line_buffer):
            line = self.line_buffer.pop(0)
            if line.startswith('get'):
                request = self.parse_get_request(line)
                if request:
                    self.socket.write('<<< processing...\n'.encode())
                    self.new_request.emit(request)
                else:
                    self.socket.write('<<< request failed\n'.encode())
            elif line.startswith('set'):
                self.process_set_request(line)
            else:
                print(f'unknown request: "{line}"')

    @pyqtSlot()
    def cleanup(self):
        print(f'connection to [{self.address.toString()}]:{self.port} got disconnected')
        self.deleteLater()

    @pyqtSlot()
    def close(self):
        self.socket.close()


class Server(QObject):
    new_request = pyqtSignal(NetRequest)

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
            conn = Connection(socket, self)    # by setting self as parent, this instance will last until self gets deleted
            conn.new_request.connect(self.forward_request)

    @pyqtSlot(NetRequest)
    def forward_request(self, request):
        self.new_request.emit(request)
