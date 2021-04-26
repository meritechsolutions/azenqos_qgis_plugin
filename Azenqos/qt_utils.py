from PyQt5.QtWidgets import QMessageBox, QPushButton, QInputDialog, QLineEdit


def msgbox(msg, title="Message", parent=None):
    msgBox = QMessageBox(parent)
    msgBox.setWindowTitle(title)
    msgBox.setText(msg)
    msgBox.addButton(QPushButton("OK"), QMessageBox.YesRole)
    reply = msgBox.exec_()
    return reply


def ask_text(parent, title, msg):
    text, okPressed = QInputDialog.getText(parent, title, msg, QLineEdit.Normal, "")
    if okPressed:
        return text
    return None


def ask_yes_no(parent, title, msg, yes_text="Yes", no_text="No", cancel_text="Cancel" , question=False):
    reply = None
    if question:
        reply = QMessageBox.question(parent, title, msg, QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.Yes)
    else:
        msgBox = QMessageBox(parent)
        msgBox.setWindowTitle(title)
        msgBox.setText(msg)
        msgBox.addButton(
            QPushButton(yes_text), QMessageBox.YesRole
        )
        msgBox.addButton(QPushButton(no_text), QMessageBox.NoRole)
        reply = msgBox.exec_()
    return reply
