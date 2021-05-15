#!/usr/bin/env python3

from PyQt5.QtCore import *
from PyQt5.QtNetwork import *

class Server(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mcast_listener = QUdpSocket(self)
        self.mcast_listener.bind(QHostAddress.Any, 9363)
        self.mcast_listener.readyRead.connect(self.incoming)
        print('Server created')

    @pyqtSlot()
    def incoming(self):
        while self.mcast_listener.hasPendingDatagrams():
            data = self.mcast_listener.receiveDatagram()
            text = str(data.data(), encoding='utf8')
            sender = data.senderAddress()
            port = data.senderPort()
            print(f'got "{text.rstrip()}" from [{sender.toString()}]:{port}')
            if 'I\'m looking for TimeKeeper hosts.' == text:
                self.mcast_listener.writeDatagram('Here I am!'.encode('utf8'), sender, port)
