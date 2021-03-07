#!/usr/bin/env python3

from PyQt5.QtCore import *
from PyQt5.QtSerialPort import *
import signal


class TimeKeeperService(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.serial = SerialInterface(self)
        self.serial.new_line.connect(self.process_line)

        # timer to give focus to the Python interpreter for processing signals
        self.python_signal_timer = QTimer()
        self.python_signal_timer.setInterval(1000)
        self.python_signal_timer.timeout.connect(lambda: None)

        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        self.reopen_timer = QTimer()
        self.reopen_timer.setInterval(3000)
        self.reopen_timer.timeout.connect(self.open_serial)

    def signal_handler(self, sig_num, stack_frame):
        self.stop()
        print('signal handled')
        QCoreApplication.quit()

    @pyqtSlot()
    def start(self):
        self.python_signal_timer.start()
        self.open_serial()

    @pyqtSlot()
    def open_serial(self):
        success = self.serial.open()
        if success:
            self.reopen_timer.stop()
            print('serial opened successfully')
        else:
            self.reopen_timer.start()
            print('could not open serial')

    @pyqtSlot()
    def stop(self):
        self.serial.close()

    @pyqtSlot(str)
    def process_line(self, line):
        if 'heartbeat request' == line:
            answer = 'heartbeat response'
            self.serial.send(answer)


class SerialInterface(QObject):
    new_line = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.port = QSerialPort()

        self.is_open = False

        self.buffer = str()

    def open(self, name='FT232R USB UART'):
        if self.is_open:
            self.port.close()
            self.is_open = False
        all_ports = QSerialPortInfo.availablePorts()
        for info in all_ports:
            if info.description() == name:
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


if '__main__' == __name__:
    import sys

    app = QCoreApplication(sys.argv)

    app.setOrganizationName('Wene')
    app.setApplicationName('TimeKeeper_service')

    service = TimeKeeperService()
    QTimer.singleShot(0, service.start)     # start as soon as the event loop is running

    sys.exit(app.exec_())
