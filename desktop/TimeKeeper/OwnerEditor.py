#!/usr/bin/env python3

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class OwnerEditor(QWidget):
    add_owner = pyqtSignal(str, str, int)

    def __init__(self, parent=None):
        super().__init__(parent)

