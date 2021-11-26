import PyQt5
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon, QPixmap, QIntValidator
from PyQt5.QtWidgets import QDialog, QMessageBox, QComboBox, QCompleter

import os
from functools import partial

import azq_utils
import preprocess_azm
from add_param_dialog import CustomQCompleter


class add_custom_table_param_dialog(QDialog):
    def __init__(self, on_param_added, param=None, arg=None, merge_method=None, tolerance=None, title = "Add Parameter", custom_checkbox_neme = None):
        super(add_custom_table_param_dialog, self).__init__(None)
        self.param_df = preprocess_azm.get_number_param().reset_index(drop=True)
        self.param = self.param_df["var_name"][0]
        self.param_name = None
        self.merge_method = "last()"
        self.tolerance = "2000"
        self.on_param_added = on_param_added
        self.title = title
        self.custom_checkbox_neme = custom_checkbox_neme
        self.n_arg_max = "1"
        self.arg = "1"
        if param is not None:
            self.param = param
        if arg is not None:
            self.arg = arg
        if merge_method is not None:
            self.merge_method = merge_method
        if tolerance is not None:
            self.tolerance = tolerance
        self.is_checked = False
        self.setAttribute(PyQt5.QtCore.Qt.WA_DeleteOnClose)
        self.setupUi()

    def setupUi(self):
        dirname = os.path.dirname(__file__)
        self.ui = loadUi(azq_utils.get_module_fp("add_param_dialog.ui"), self)
        self.setWindowIcon(QIcon(QPixmap(os.path.join(dirname, "icon.png"))))
        self.setWindowTitle("Select Parameter")
        self.ui.customCheckbox.hide()
        self.ui.toleranceLineEdit.setValidator(QIntValidator())
        self.ui.toleranceLineEdit.setEnabled(True)
        self.set_merge_method(self.merge_method)
        self.ui.toleranceLineEdit.setText(self.tolerance) 
        
        self.ui.paramComboBox.setEditable(True)
        self.ui.paramComboBox.setInsertPolicy(QComboBox.NoInsert)
        completer = CustomQCompleter(self.ui.paramComboBox)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setModel(self.ui.paramComboBox.model())
        self.ui.paramComboBox.setCompleter(completer)
        self.ui.lastRadioButton.toggled.connect(lambda:self.radio_button_state(self.ui.lastRadioButton))
        self.ui.avgRadioButton.toggled.connect(lambda:self.radio_button_state(self.ui.avgRadioButton))
        self.ui.maxRadioButton.toggled.connect(lambda:self.radio_button_state(self.ui.maxRadioButton))
        self.ui.minRadioButton.toggled.connect(lambda:self.radio_button_state(self.ui.minRadioButton))

        if self.custom_checkbox_neme is not None and isinstance(self.custom_checkbox_neme, str):
            self.ui.customCheckbox.show()
            self.ui.customCheckbox.setText(self.custom_checkbox_neme)
            self.custom_checkbox.setChecked(False)
            enableSlot = partial(self.check, self.ui.customCheckbox)
            disableSlot = partial(self.uncheck, self.ui.customCheckbox)
            self.ui.customCheckbox.stateChanged.connect(
                lambda x: enableSlot() if x else disableSlot()
            )
            
        self.ui.paramComboBox.setEditable(True)
        for index, row in self.param_df.iterrows():
            self.ui.paramComboBox.addItem(row.var_name)
        self.ui.paramComboBox.setCurrentText(self.param)
        self.select_param()
        self.ui.argComboBox.setCurrentIndex(int(self.arg)-1)
        self.select_arg()
        self.ui.paramComboBox.currentIndexChanged.connect(self.select_param)
        self.ui.argComboBox.currentIndexChanged.connect(self.select_arg)

        self.accepted.connect(self.on_ok_button_click)
    
    def radio_button_state(self, radio_button):
        if radio_button.isChecked() == True:
            if radio_button.text() == "Last":
                self.merge_method = "last()"
            elif radio_button.text() == "Average":
                self.merge_method = "mean()"
            elif radio_button.text() == "Max":
                self.merge_method = "max()"
            elif radio_button.text() == "Min":
                self.merge_method = "min()"

    def set_merge_method(self, merge_method):
        if merge_method == "last()":
            self.ui.lastRadioButton.setChecked(True)
        elif merge_method == "mean()":
            self.ui.avgRadioButton.setChecked(True)
        elif merge_method == "max()":
            self.ui.maxRadioButton.setChecked(True)
        elif merge_method == "min()":
            self.ui.minRadioButton.setChecked(True)

    def select_param(self):
        self.set_param()
        self.ui.argComboBox.clear()
        self.n_arg_max = self.param_df.loc[
            self.param_df["var_name"] == self.param, "n_arg_max"
        ].item()
        for i in range(int(self.n_arg_max)):
            n = i + 1
            self.ui.argComboBox.addItem(str(n))
        self.param_name = self.param
        if int(self.n_arg_max) > 1:
            self.param_name = self.param + "_" + self.arg

    def select_arg(self):
        self.set_arg()
        if int(self.n_arg_max) > 1:
            self.param_name = self.param + "_" + self.arg

    def set_param(self):
        self.param = self.ui.paramComboBox.currentText()

    def set_arg(self):
        self.arg = self.ui.argComboBox.currentText()

    def check(self, checkbox):
        self.is_checked = True

    def uncheck(self, checkbox):
        self.is_checked = False

    def on_ok_button_click(self):
        self.on_param_added(param_dict = {"parameter name":self.param_name, "parameter":self.param, "arg":self.arg, "main parameter":False, "merge_method":self.merge_method, "tolerance":self.ui.toleranceLineEdit.text()})



