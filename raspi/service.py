#!/usr/bin/env python3

from PyQt5.QtCore import *
from PyQt5.QtSerialPort import *
import signal


class TimeLogger(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.filename = 'logfile.tsv'

    def log_badge(self, timestamp, badge):
        with open(self.filename, 'a') as f:
            line = f'{timestamp}\t{badge}'
            print(line, file=f)


class TimeKeeperService(QObject):
    update_time = pyqtSignal(QDateTime)

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

        self.last_time_str = ''
        self.time_update_timer = QTimer()
        self.time_update_timer.setInterval(50)
        self.time_update_timer.timeout.connect(self.update_now)
        self.time_update_timer.start()
        self.update_time.connect(self.update_clock)

        self.resume_timer = QTimer()
        self.resume_timer.setInterval(3500)
        self.resume_timer.setSingleShot(True)
        self.resume_timer.timeout.connect(self.resume)

        self.logger = TimeLogger(self)

    def signal_handler(self, sig_num, stack_frame):
        self.reopen_timer.stop()
        self.time_update_timer.stop()
        self.resume_timer.stop()
        self.stop()
        QCoreApplication.quit()

    @pyqtSlot()
    def resume(self):
        self.time_update_timer.start()

    @pyqtSlot()
    def update_now(self):
        new_date_time = QDateTime.currentDateTime()
        new_time_str = new_date_time.toString('yyyy-MM-dd hh:mm:ss')
        if self.last_time_str != new_time_str:
            self.last_time_str = new_time_str
            self.update_time.emit(new_date_time)

    @pyqtSlot(QDateTime)
    def update_clock(self, date_time: QDateTime):
        time_str = date_time.toString('hh:mm:ss')
        date_str = date_time.toString('dd.MM.yyyy')
        time_cmd = f'print 0 {time_str}'
        date_cmd = f'print 1 {date_str}'
        self.serial.send(time_cmd)
        self.serial.send(date_cmd)

    @pyqtSlot()
    def start(self):
        self.python_signal_timer.start()
        self.open_serial()

    @pyqtSlot()
    def open_serial(self):
        success = self.serial.open(port='ttyS0')
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
    def process_line(self, line: str):
        id_identifier = 'Card ID: '
        if 'heartbeat request' == line:
            self.serial.send('heartbeat response')
        elif line.startswith(id_identifier):
            id_str = line[len(id_identifier):]
            id_int = int(id_str, 0)
            self.time_update_timer.stop()
            self.resume_timer.start()
            self.serial.send(f'print 0 {id_str}')
            self.serial.send(f'print 1 {str(id_int)}')
            self.logger.log_badge(self.last_time_str, id_str)


class SerialInterface(QObject):
    new_line = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.port = QSerialPort()
        self.is_open = False
        self.buffer = str()

    def open(self, name='FT232R USB UART', port=None):
        if self.is_open:
            self.port.close()
            self.is_open = False
        all_ports = QSerialPortInfo.availablePorts()
        for info in all_ports:
            use_this = False
            if port:
                if info.portName() == port:
                    use_this = True
            elif info.description() == name:
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


if '__main__' == __name__:
    import sys

    app = QCoreApplication(sys.argv)

    app.setOrganizationName('Wene')
    app.setApplicationName('TimeKeeper_service')

    service = TimeKeeperService()
    QTimer.singleShot(0, service.start)     # start as soon as the event loop is running

    sys.exit(app.exec_())
