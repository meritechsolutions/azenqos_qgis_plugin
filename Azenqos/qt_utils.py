from PyQt5.QtWidgets import QMessageBox, QPushButton, QInputDialog, QLineEdit


def msgbox(msg, title="Message", parent=None):
    msgBox = QMessageBox(parent)
    msgBox.setWindowTitle(title)
    msgBox.setText(msg)
    msgBox.addButton(QPushButton("OK"), QMessageBox.YesRole)


def ask_text(parent, title, msg):
    text, okPressed = QInputDialog.getText(parent, title, msg, QLineEdit.Normal, "")
    if okPressed:
        return text
    return None
