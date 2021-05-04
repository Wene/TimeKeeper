#!/usr/bin/env python3

from PyQt5.QtCore import *
from PyQt5.QtSerialPort import *


class SerialInterface(QObject):
    new_line = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.port = QSerialPort()
        self.is_open = False
        self.buffer = str()

    def open(self, name='', port=''):
        if self.is_open:
            self.port.close()
            self.is_open = False
        all_ports = QSerialPortInfo.availablePorts()
        for info in all_ports:
            use_this = False
            if name:
                if info.description() == name:
                    use_this = True
            elif port:
                if info.portName() == port:
                    use_this = True
            if use_this:
                self.port.setPort(info)
                self.port.setBaudRate(9600)
                self.port.open(QSerialPort.ReadWrite)
                self.is_open = True
                self.port.readyRead.connect(self.read_data)
                break
        if self.is_open:
            return True
        else:
            return False

    def close(self):
        if self.is_open:
            self.port.close()
            self.is_open = False

    def read_data(self):
        new_bytes = self.port.readAll()
        self.buffer += new_bytes.data().decode('utf-8')
        while '\n' in self.buffer:
            pos = self.buffer.find('\n')
            send_text = self.buffer[:pos].rstrip()
            self.buffer = self.buffer[pos:].lstrip()
            self.new_line.emit(send_text)

    @pyqtSlot(str)
    def send(self, text: str):
        if self.is_open:
            text += '\n'
            data = text.encode('utf-8')
            self.port.write(data)
