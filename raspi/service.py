#!/usr/bin/env python3

from PyQt5.QtCore import *
from PyQt5.QtSerialPort import *


class SerialInterface(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.port = QSerialPort()
        self.open = False

    def init(self, name='FT232R USB UART'):
        if self.open:
            self.port.close()
            self.open = False
        all_ports = QSerialPortInfo.availablePorts()
        for info in all_ports:
            if info.description() == name:
                self.port.setPort(info)
                self.port.setBaudRate(9600)
                self.port.open(QSerialPort.ReadWrite)
                self.open = True
                self.port.readyRead.connect(self.read_and_print)
                break
        if not self.open:
            print('Serial port not found')
            QCoreApplication.quit()

    def read_and_print(self):
        byte_array = self.port.readAll()
        print(byte_array.data().decode())


if '__main__' == __name__:
    import sys
    import signal

    app = QCoreApplication(sys.argv)

    app.setOrganizationName('Wene')
    app.setApplicationName('TimeKeeper_service')

    serial_interface = SerialInterface()
    QTimer.singleShot(0, serial_interface.init)     # init as soon as the event loop is running

    # interrupt the Qt event loop every second and allow Python to handle OS signals
    timer = QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(1000)

    def on_quit(sig_num, stack_frame):
        app.quit()

    signal.signal(signal.SIGTERM, on_quit)
    signal.signal(signal.SIGINT, on_quit)

    sys.exit(app.exec_())
