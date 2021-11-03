from PyQt5.QtCore import Qt, QVariant, QRegExp, QSortFilterProxyModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMessageBox, QPushButton, QInputDialog, QLineEdit, QDialog, QFormLayout, QLabel, QListView, \
    QDialogButtonBox, QHBoxLayout, QCheckBox
from functools import partial


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

def ask_selection(parent, items, items_selected=None, title="Please select", msg="Available options:", use_filter = False):
    # https://stackoverflow.com/questions/41310023/pyside-popup-showing-list-and-multiple-select
    class MyDialog(QDialog):
        def __init__(self, title, message, items, parent=None, items_selected=None, use_filter = False):
            super(MyDialog, self).__init__(parent=parent)
            form = QFormLayout(self)
            if use_filter:
                filter_label = QLabel("Filter:")
                filter_line_edit = QLineEdit()
                filter_layout = QHBoxLayout()
                filter_layout.addWidget(filter_label)
                filter_layout.addWidget(filter_line_edit)
                filter_line_edit.textChanged.connect(self.update_display)
                form.addRow(filter_layout)
            self.dont_update = False
            self.select_all_check_box = QCheckBox("Select All")
            form.addRow(self.select_all_check_box)
            self.select_all_check_box.setChecked(True)
            enabl_select_all_check_box = partial(self.select_all, self.select_all_check_box)
            disable_select_all_check_box = partial(self.unselect_all, self.select_all_check_box)
            self.select_all_check_box.stateChanged.connect(
                lambda x: enabl_select_all_check_box() if x else disable_select_all_check_box()
            )
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
            self.proxy = QSortFilterProxyModel()
            self.proxy.setSourceModel(model)
            self.proxy.setFilterKeyColumn(0)
            self.listView.setModel(self.proxy)
            buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
            form.addRow(buttonBox)
            buttonBox.accepted.connect(self.accept)
            buttonBox.rejected.connect(self.reject)

        def select_all(self, checkbox):
            if self.dont_update:
                self.dont_update = False
                return
            model = self.listView.model()
            for i in range(model.rowCount()):
                source_index = model.mapToSource(model.index(i,0))
                model.sourceModel().item(source_index.row()).setCheckState(Qt.Checked)

        def unselect_all(self, checkbox):
            if self.dont_update:
                self.dont_update = False
                return
            model = self.listView.model()
            for i in range(model.rowCount()):
                source_index = model.mapToSource(model.index(i,0))
                model.sourceModel().item(source_index.row()).setCheckState(Qt.Unchecked)

        def update_display(self, text):
            regex = "{}".format(text)
            self.proxy.setFilterRegExp(QRegExp(regex, Qt.CaseInsensitive))
            model = self.listView.model()
            check = 2
            for i in range(model.rowCount()):
                source_index = model.mapToSource(model.index(i,0))
                if not model.sourceModel().item(source_index.row()).checkState():
                    check = 0
                    break
            print(self.select_all_check_box.checkState(), self.dont_update, check)
            if self.select_all_check_box.checkState() != check:
                self.dont_update = True
                self.select_all_check_box.setChecked(check)

        def selection_mask(self):
            mask = []
            model = self.listView.model().sourceModel()
            i = 0
            while model.item(i):
                if model.item(i).checkState():
                    mask.append(True)
                else:
                    mask.append(False)
                i += 1
            return mask

    dial = MyDialog(title=title, message=msg, items=items, parent=parent, items_selected=items_selected, use_filter=use_filter)
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
