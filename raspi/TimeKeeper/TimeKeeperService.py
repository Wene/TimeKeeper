#!/usr/bin/env python3

from PyQt5.QtCore import *
from .SerialInterface import SerialInterface
from .DB import DB
import signal


class TimeKeeperService(QObject):
    update_time = pyqtSignal(QDateTime)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings(self)
        self.port_name = self.settings.value('port_name', 'FT232R USB UART')
        self.port = self.settings.value('port', '')
        self.source_name = self.settings.value('source', 'main')
        self.settings.setValue('port_name', self.port_name)
        self.settings.setValue('port', self.port)
        self.settings.setValue('source', self.source_name)

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

        self.last_time_stamp = QDateTime.currentSecsSinceEpoch()
        self.time_update_timer = QTimer()
        self.time_update_timer.setInterval(50)
        self.time_update_timer.timeout.connect(self.update_now)
        self.time_update_timer.start()
        self.update_time.connect(self.update_clock)

        self.resume_timer = QTimer()
        self.resume_timer.setInterval(3500)
        self.resume_timer.setSingleShot(True)
        self.resume_timer.timeout.connect(self.resume)

        self.db = DB(self, 'timekeeper.db')

    def signal_handler(self, sig_num, stack_frame):
        self.reopen_timer.stop()
        self.time_update_timer.stop()
        self.resume_timer.stop()
        self.stop()
        print('service stopped')
        QCoreApplication.quit()

    @pyqtSlot()
    def resume(self):
        self.time_update_timer.start()

    @pyqtSlot()
    def update_now(self):
        new_date_time = QDateTime.currentDateTime()
        new_time_stamp = new_date_time.toSecsSinceEpoch()
        if self.last_time_stamp != new_time_stamp:
            self.last_time_stamp = new_time_stamp
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
        success = self.serial.open(name=self.port_name, port=self.port)
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
            name = self.db.get_valid_badge_owner(id_str, self.last_time_stamp)
            self.time_update_timer.stop()
            self.resume_timer.start()
            self.serial.send(f'print 1 {name}')
            self.db.log_event(self.last_time_stamp, id_str, self.source_name)

