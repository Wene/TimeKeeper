#!/usr/bin/env python3

from PyQt5.QtCore import *
from TimeKeeper import TimeKeeperService


if '__main__' == __name__:
    import sys

    app = QCoreApplication(sys.argv)

    app.setOrganizationName('Wene')
    app.setApplicationName('TimeKeeper_service')

    service = TimeKeeperService()
    QTimer.singleShot(0, service.start)     # start as soon as the event loop is running

    sys.exit(app.exec_())
