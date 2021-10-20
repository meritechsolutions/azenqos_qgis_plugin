from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMessageBox, QPushButton, QInputDialog, QLineEdit, QDialog, QFormLayout, QLabel, QListView, \
    QDialogButtonBox


def msgbox(msg, title="Message", parent=None):
    msgBox = QMessageBox(parent)
    msgBox.setWindowTitle(title)
    msgBox.setText(msg)
    msgBox.addButton(QPushButton("OK"), QMessageBox.YesRole)
    reply = msgBox.exec_()
    return reply


def ask_text(parent, title="Input text", msg="Input text", existing_content="", multiline=False):
    text = None
    okPressed = None
    if multiline:
        text, okPressed = QInputDialog.getMultiLineText(parent, title, msg, existing_content)
    else:
        text, okPressed = QInputDialog.getText(parent, title, msg, QLineEdit.Normal, existing_content)
    if okPressed:
        return text
    return None

def ask_selection(parent, items, items_selected=None, title="Please select", msg="Available options:"):
    # https://stackoverflow.com/questions/41310023/pyside-popup-showing-list-and-multiple-select
    class MyDialog(QDialog):
        def __init__(self, title, message, items, parent=None, items_selected=None):
            super(MyDialog, self).__init__(parent=parent)
            form = QFormLayout(self)
            form.addRow(QLabel(message))
            self.listView = QListView(self)
            form.addRow(self.listView)
            model = QStandardItemModel(self.listView)
            self.setWindowTitle(title)
            if items_selected is None:
                items_selected = [False] * len(items)
            for i in range(len(items)):
                item = items[i]
                selected = items_selected[i]
                # create an item with a caption
                standardItem = QStandardItem(item)
                standardItem.setCheckable(True)
                print("i {} selected {}".format(i, selected))
                standardItem.setCheckState(Qt.Checked if selected else Qt.Unchecked)
                model.appendRow(standardItem)
            self.listView.setModel(model)
            buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
            form.addRow(buttonBox)
            buttonBox.accepted.connect(self.accept)
            buttonBox.rejected.connect(self.reject)

        def selection_mask(self):
            mask = []
            model = self.listView.model()
            i = 0
            while model.item(i):
                if model.item(i).checkState():
                    mask.append(True)
                else:
                    mask.append(False)
                i += 1
            return mask

    dial = MyDialog(title=title, message=msg, items=items, parent=parent, items_selected=items_selected)
    if dial.exec_() == QDialog.Accepted:
        return dial.selection_mask()
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
