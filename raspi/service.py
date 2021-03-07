#!/usr/bin/env python3

from PyQt5.QtCore import *
from PyQt5.QtSerialPort import *
import signal


class TimeKeeperService(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.serial = SerialInterface(self)

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


class SerialInterface(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.port = QSerialPort()
        self.is_open = False

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
                self.port.readyRead.connect(self.read_and_print)
                break
        if self.is_open:
            return True
        else:
            return False

    def close(self):
        if self.is_open:
            self.port.close()
            self.is_open = False

    def read_and_print(self):
        byte_array = self.port.readAll()
        print(byte_array.data().decode())


if '__main__' == __name__:
    import sys

    app = QCoreApplication(sys.argv)

    app.setOrganizationName('Wene')
    app.setApplicationName('TimeKeeper_service')

    service = TimeKeeperService()
    QTimer.singleShot(0, service.start)     # start as soon as the event loop is running

    sys.exit(app.exec_())
