from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *  # QAbstractTableModel, QVariant, Qt, pyqtSignal, QThread
from PyQt5.QtGui import *


def msgbox(self, msg, title="Message"):
    msgBox = QMessageBox()
    msgBox.setWindowTitle(title)
    msgBox.setText(msg)
    msgBox.addButton(QPushButton('OK'), QMessageBox.YesRole)
    reply = msgBox.exec_()
