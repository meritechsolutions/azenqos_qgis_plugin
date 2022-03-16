import contextlib
import sqlite3
import os
import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QPixmap, QAbstractItemView
from PyQt5.uic import loadUi

import azq_utils
import color_dialog
import add_event_linechart_dialog
import dataframe_model


class linechart_event_dialog(QtWidgets.QDialog):
    update_table = pyqtSignal(object)
    on_result = pyqtSignal(object, object, object, object)


    def __init__(self, gc, onEventAdded, event_list=[], selected_ue=None):
        super(linechart_event_dialog, self).__init__(None)
        self.gc = gc
        with contextlib.closing(sqlite3.connect(self.gc.databasePath)) as dbcon:
            all_event_list = pd.read_sql("select distinct name from events", dbcon).name.tolist()
        self.all_event_list = all_event_list
        self.event_list = event_list
        self.onEventAdded = onEventAdded
        self.select_event = None
        self.selected_ue = selected_ue
        self.selected_logs = None
        if self.selected_ue is not None:
            self.selected_logs = self.gc.device_configs[self.selected_ue]["log_hash"]
        self.setupUi()

    def setupUi(self):
        dirname = os.path.dirname(__file__)
        self.ui = loadUi(azq_utils.get_module_fp("add_linechart_event_dialog.ui"), self)
        self.setWindowIcon(QIcon(QPixmap(os.path.join(dirname, "icon.png"))))
        self.setWindowTitle("Line Chart Event")
        self.ui.removeButton.setEnabled(False)
        self.ui.addButton.clicked.connect(self.on_add_button_click)
        self.ui.removeButton.clicked.connect(self.on_remove_button_click)
        self.update_table.connect(self.on_update_table)
        self.model = dataframe_model.DataFrameModel(pd.DataFrame(self.event_list))
        self.update_table.emit(self.model)
        self.ui.tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.tableView.clicked.connect(self.on_color_click)
        selection_model = self.ui.tableView.selectionModel()
        selection_model.selectionChanged.connect(self.on_table_click)
        self.accepted.connect(self.on_ok_button_click)

    def on_add_button_click(self):
        dlg = add_event_linechart_dialog.add_event_linechart_dialog(self.all_event_list, self.on_event_added)
        dlg.setWindowModality(Qt.ApplicationModal)
        dlg.show()

    def on_remove_button_click(self):
        del self.event_list[self.select_row_index]
        self.model.setDataFrame(pd.DataFrame(self.event_list))

    def on_update_table(self, model):
        self.ui.tableView.setModel(model)

    def on_color_click(self,item):
        if item.column() == 1: 
            name = self.event_list[item.row()]["event name"]
            color = self.event_list[item.row()]["color"]
            dlg = color_dialog.ColorDialog(name, color, self.on_color_set)
            dlg.setWindowModality(Qt.ApplicationModal)
            dlg.show()

    def on_color_set(self, name, color):
        for event in self.event_list:
            if event["event name"] == name:
                event["color"] = color
        self.model.setDataFrame(pd.DataFrame(self.event_list))

    def on_event_added(self, event_dict):
        found = False
        for event in self.event_list:
            if event["event name"] == event_dict["event name"]:
                found = True
                break
        if not found:
            self.event_list.append(event_dict)
            self.model.setDataFrame(pd.DataFrame(self.event_list))

    def on_table_click(self):
        index = self.ui.tableView.selectedIndexes()
        if len(index) > 0:
            index = index[0]
        if index.isValid():
            self.select_row_index = index.row()
            self.ui.removeButton.setEnabled(True)

    
    def on_ok_button_click(self):
        self.onEventAdded(self.event_list)


