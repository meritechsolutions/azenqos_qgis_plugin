import os
from pathlib import Path
import json

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QMenu, QCompleter, QComboBox
from PyQt5.uic import loadUi


from add_param_dialog import CustomQCompleter
import azq_utils
import preprocess_azm
import custom_last_instant_table_dataframe_model


class custom_last_instant_table_dialog(QtWidgets.QDialog):
    update_table = pyqtSignal(object)
    on_result = pyqtSignal(object, object, object)


    def __init__(self, gc, param_list=[[{},{},{}],[{},{},{}],[{},{},{}]], window_name="Custom window", selected_ue=None):
        super(custom_last_instant_table_dialog, self).__init__(None)
        self.gc = gc
        self.param_list = param_list
        self.param_df = preprocess_azm.get_number_param()
        self.param_df = self.param_df.reset_index(drop=True)
        self.cell_type = "text"
        self.param = self.param_df["var_name"][0]
        self.param_name = self.param
        self.n_arg_max = "1"
        self.arg = "1"
        self.selected_row = None
        self.selected_col = None

        self.window_name = "Custom window"
        self.selected_ue = selected_ue
        self.selected_logs = None
        if self.selected_ue is not None:
            self.selected_logs = self.gc.device_configs[self.selected_ue]["log_hash"]
        self.window_name = window_name
        self.setupUi()

    def setupUi(self):
        dirname = os.path.dirname(__file__)
        self.ui = loadUi(azq_utils.get_module_fp("custom_last_instant_table_dialog.ui"), self)
        self.setWindowIcon(QIcon(QPixmap(os.path.join(dirname, "icon.png"))))
        self.setWindowTitle("Custom Table")
        self.ui.addRowButton.clicked.connect(self.on_add_row_parameter_button_click)
        self.ui.addColButton.clicked.connect(self.on_add_col_parameter_button_click)
        self.ui.windowNameLineEdit.setText(self.window_name) 
        self.update_table.connect(self.on_update_table)
        self.model = custom_last_instant_table_dataframe_model.PandasModel(self.param_list)
        self.update_table.emit(self.model)
        self.ui.elemTypecomboBox.addItem("text")
        self.ui.elemTypecomboBox.addItem("element")
        
        self.ui.paramComboBox.setEditable(True)
        self.ui.paramComboBox.setInsertPolicy(QComboBox.NoInsert)
        completer = CustomQCompleter(self.ui.paramComboBox)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setModel(self.ui.paramComboBox.model())
        self.ui.paramComboBox.setCompleter(completer)

        for index, row in self.param_df.iterrows():
            self.ui.paramComboBox.addItem(row.var_name)

        self.ui.elemTypecomboBox.setEnabled(False)
        self.ui.textLineEdit.setEnabled(False)
        self.ui.paramComboBox.setEnabled(False)
        self.ui.argComboBox.setEnabled(False)
        self.ui.addParamButton.setEnabled(False)
        self.ui.paramLabel.hide()
        self.ui.paramComboBox.hide()
        self.ui.argLabel.hide()
        self.ui.argComboBox.hide()
        self.ui.tableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.elemTypecomboBox.currentTextChanged.connect(self.on_combobox_changed)
        self.ui.paramComboBox.currentIndexChanged.connect(self.select_param)
        self.ui.argComboBox.currentIndexChanged.connect(self.select_arg)
        self.ui.tableView.customContextMenuRequested.connect(self.on_right_table_click)
        self.ui.tableView.clicked.connect(self.on_table_click)
        self.ui.addParamButton.clicked.connect(self.on_param_add)
        self.ui.saveButton.clicked.connect(self.on_save_parameter_button_click)
        self.ui.loadButton.clicked.connect(self.on_load_parameter_button_click)
        self.accepted.connect(self.on_ok_button_click)

    def on_combobox_changed(self, value):
        print("combobox changed", value)
        if value.lower() == "text":
            self.ui.paramLabel.hide()
            self.ui.paramComboBox.hide()
            self.ui.argLabel.hide()
            self.ui.argComboBox.hide()
            self.ui.textLineEdit.show()
            self.ui.textLabel.show()
            self.cell_type = "text"
        elif value.lower() == "element":
            self.ui.paramLabel.show()
            self.ui.paramComboBox.show()
            self.ui.argLabel.show()
            self.ui.argComboBox.show()
            self.ui.textLineEdit.hide()
            self.ui.textLabel.hide()
            self.cell_type = "element"

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

    def on_right_table_click(self, QPos=None):
        index = self.ui.tableView.indexAt(QPos)
        if index.isValid():
            col = index.column()
            row = index.row()
            menu = QMenu()
            delete_row = menu.addAction("Delete Row")
            delete_column = menu.addAction("Delete Column")
            action = menu.exec_(self.ui.tableView.mapToGlobal(QPos))
            if action == delete_row:
                del self.param_list[row] 
            elif action == delete_column:
                for row in self.param_list:
                    del row[col]
            self.model.setItems(self.param_list)

    def on_param_add(self):
        value = self.param_name
        param = self.param
        arg = self.arg
        if self.cell_type == "text":
            value = self.ui.textLineEdit.text()
            param = None
            arg = None
        self.param_list[self.selected_row][self.selected_col] = {"type":self.cell_type, "value":value, "param":param, "arg":arg, "color":"#FFFFFF", "percent":None}
        self.model.setItems(self.param_list)
    
    def on_table_click(self, item):
        self.ui.elemTypecomboBox.setEnabled(True)
        self.ui.textLineEdit.setEnabled(True)
        self.ui.paramComboBox.setEnabled(True)
        self.ui.argComboBox.setEnabled(True)
        self.ui.addParamButton.setEnabled(True)
        self.selected_row = item.row()
        self.selected_col = item.column()
        selected_cell = self.param_list[self.selected_row][self.selected_col]
        if len(selected_cell.keys()) > 0 and "type" in selected_cell.keys():
            self.ui.elemTypecomboBox.setCurrentText(selected_cell["type"])
            self.ui.textLineEdit.setText(selected_cell["value"])
            param_index = self.ui.paramComboBox.findText(selected_cell["param"], Qt.MatchFixedString)
            if param_index >= 0:
                self.ui.paramComboBox.setCurrentIndex(param_index)
            arg_index = self.ui.argComboBox.findText(selected_cell["arg"], Qt.MatchFixedString)
            if arg_index >= 0:
                self.ui.argComboBox.setCurrentIndex(arg_index)


    def on_add_row_parameter_button_click(self):
        col_len = len(self.param_list[0])
        new_row = []
        for i in range(col_len):
            new_row.append({})
        self.param_list.append(new_row)
        self.model.setItems(self.param_list)

    def on_add_col_parameter_button_click(self):
        for row in self.param_list:
            row.append({})
        self.model.setItems(self.param_list)
    
    def on_save_parameter_button_click(self):
        filename = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save file as ...", os.path.join(Path.home(),"custom_window.json"), "custom window file (*.json)"
        )
        if filename:
            if filename[0]:
                filepath = filename[0]
                try:
                    with open(filepath, 'w') as f:
                        json.dump(self.param_list, f)
                except:
                    pass

    def on_load_parameter_button_click(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open file ...", os.path.join(Path.home(),""), "custom window file (*.json)"
        )
        if filename:
            if filename[0]:
                filepath = filename[0]
                try:
                    with open(filepath, 'r') as f:
                        self.param_list = json.load(f)
                        self.model.setItems(self.param_list)
                        super().accept()
                except:
                    pass

    def on_update_table(self, model):
        self.ui.tableView.setModel(model)
    
    def on_ok_button_click(self):
        self.window_name = self.ui.windowNameLineEdit.text()
        self.on_result.emit(self.param_list, self.window_name, self.selected_ue)