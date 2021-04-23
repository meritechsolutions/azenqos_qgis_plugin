import os
from functools import partial

from PyQt5 import QtCore
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi

import azq_utils
import datatable
import main_window


class module_dialog(QDialog):
    def __init__(self, parent, row_sr, gc, mdi):
        super(module_dialog, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.gc = gc
        self.mdi = mdi
        self.check = True
        self.row_sr = row_sr
        self.param = (
            "PY_EVAL " + self.row_sr["module"] + "." + self.row_sr["function_def"]
        )
        self.setupUi()

    def setupUi(self):
        dirname = os.path.dirname(__file__)
        self.ui = loadUi(azq_utils.get_local_fp("module_dialog.ui"), self)
        self.setWindowIcon(QIcon(QPixmap(os.path.join(dirname, "icon.png"))))
        self.setWindowTitle("AZENQOS Server module")
        self.ui.module_le.setText(self.row_sr["module"])
        self.ui.module_le.setEnabled(False)
        self.ui.title_le.setText(self.row_sr["module"])
        self.ui.param_te.setPlainText(
            "PY_EVAL " + self.row_sr["module"] + "." + self.row_sr["function_def"]
        )
        enable_slot = partial(self.enable_mod, self.ui.checkBox)
        disable_slot = partial(self.disable_mod, self.ui.checkBox)
        self.ui.checkBox.stateChanged.connect(
            lambda x: enable_slot() if x else disable_slot()
        )
        self.ui.checkBox.setChecked(True)
        self.ui.pushButton.clicked.connect(self.run_module)

    def run_module(self):
        mod_str = self.ui.param_te.toPlainText()
        title = self.ui.title_le.text()
        swa = main_window.SubWindowArea(self.mdi, self.gc)
        window = datatable.create_table_window_from_api_expression_ret(
            None,
            title,
            self.gc,
            self.gc.login_dialog.server,
            self.gc.login_dialog.token,
            self.gc.login_dialog.lhl,
            mod_str,
        )
        self.add_subwindow_with_widget(swa, window)

    def enable_mod(self, checkbox):
        self.ui.param_te.setEnabled(False)
        self.ui.param_te.setPlainText(self.param)

    def disable_mod(self, checkbox):
        self.ui.param_te.setEnabled(True)

    def add_subwindow_with_widget(self, swa, widget):
        swa.setWidget(widget)
        self.mdi.addSubWindow(swa)
        swa.show()
        self.gc.openedWindows.append(widget)
