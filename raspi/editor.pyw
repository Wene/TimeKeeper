#!/usr/bin/env python3

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtNetwork import *
from TimeKeeper import DB


class Network(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.listener = QUdpSocket()
        self.listener.bind(QHostAddress.Any, 9363)
        self.listener.readyRead.connect(self.incoming)

    @pyqtSlot()
    def incoming(self):
        while self.listener.hasPendingDatagrams():
            data = self.listener.receiveDatagram()
            text = str(data.data(), encoding='utf8')
            sender = data.senderAddress()
            port = data.senderPort()
            identifier = 'TimeKeeper server name: '
            if text.startswith(identifier):
                name = text[len(identifier):]
                print(f'got connection from {name.rstrip()}')


class Form(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings()
        self.setWindowTitle('TimeKeeper Editor')

        layout = QVBoxLayout(self)
        self.editor = QPlainTextEdit()
        self.editor.setReadOnly(True)
        self.editor.setUndoRedoEnabled(False)
        layout.addWidget(self.editor)

        btn_layout = QHBoxLayout()
        layout.addLayout(btn_layout)

        self.btn_read = QPushButton('Read')
        self.btn_read.clicked.connect(self.read_db)
        btn_layout.addWidget(self.btn_read)
        self.btn_quit = QPushButton('Quit')
        self.btn_quit.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_quit)

        self.db = DB(self, 'timekeeper.db')
        self.network = Network(self)

        self.resize(self.settings.value('windowSize', QSize(50, 50)))
        self.move(self.settings.value('windowPosition', QPoint(50, 50)))

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.settings.setValue('windowSize', self.size())
        self.settings.setValue('windowPosition', self.pos())

    @pyqtSlot()
    def read_db(self):
        data = self.db.get_events_between_timestamps(0, QDateTime.currentDateTime().toSecsSinceEpoch())
        for line in data:
            line_str = '|'.join(line)
            self.editor.appendPlainText(line_str)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    app.setOrganizationName('Wene')
    app.setApplicationName('TimeKeeper_editor')

    translator = QTranslator()
    lib_path = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
    translator.load("qt_de.qm", lib_path)
    translator.load("qtbase_de.qm", lib_path)
    app.installTranslator(translator)

    window = Form()
    window.show()

    sys.exit(app.exec_())
