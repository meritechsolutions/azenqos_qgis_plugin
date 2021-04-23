from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *  # QAbstractTableModel, QVariant, Qt, pyqtSignal, QThread
from PyQt5.QtGui import *


def msgbox(msg, title="Message", parent=None):
    msgBox = QMessageBox(parent)
    msgBox.setWindowTitle(title)
    msgBox.setText(msg)
    msgBox.addButton(QPushButton("OK"), QMessageBox.YesRole)
    reply = msgBox.exec_()


def ask_text(parent, title, msg):
    text, okPressed = QInputDialog.getText(parent, title, msg, QLineEdit.Normal, "")
    if okPressed:
        return text
    return None
