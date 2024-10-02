import contextlib
import sqlite3
import os
from pathlib import Path
import json
import copy

import numpy as np
import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.uic import loadUi
from functools import partial

import azq_utils
import preprocess_azm
import add_custom_table_param_dialog
import custom_table_dataframe_model


class custom_table_dialog(QtWidgets.QDialog):
    update_table = pyqtSignal(object)
    on_result = pyqtSignal(object, object, object, object, object)


    def __init__(self, gc, param_list=[], window_name="Custom window", selected_ue=None, main_not_null = False):
        super(custom_table_dialog, self).__init__(None)
        self.gc = gc
        self.param_list = param_list
        self.select_param = None
        self.select_arg = None
        self.window_name = "Custom window"
        self.selected_ue = selected_ue
        self.selected_logs = None
        self.main_not_null = main_not_null
        if self.selected_ue is not None:
            self.selected_logs = self.gc.device_configs[self.selected_ue]["log_hash"]
        self.window_name = window_name
        self.setupUi()

    def setupUi(self):
        dirname = os.path.dirname(__file__)
        self.ui = loadUi(azq_utils.get_module_fp("custom_table_dialog.ui"), self)
        self.setWindowIcon(QIcon(QPixmap(os.path.join(dirname, "icon.png"))))
        self.setWindowTitle("Custom Table")
        self.ui.editButton.setEnabled(False)
        self.ui.removeButton.setEnabled(False)
        self.ui.addButton.clicked.connect(self.on_add_parameter_button_click)
        self.ui.editButton.clicked.connect(self.on_edit_parameter_button_click)
        self.ui.removeButton.clicked.connect(self.on_remove_parameter_button_click)
        self.ui.windowNameLineEdit.setText(self.window_name) 
        self.update_table.connect(self.on_update_table)
        self.model = custom_table_dataframe_model.DataFrameModel(self.param_list)
        self.update_table.emit(self.model)
        self.ui.tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        selection_model = self.ui.tableView.selectionModel()
        selection_model.selectionChanged.connect(self.on_table_click)
        self.ui.saveButton.clicked.connect(self.on_save_parameter_button_click)
        self.ui.loadButton.clicked.connect(self.on_load_parameter_button_click)
        if self.main_not_null:
            self.ui.mainNotNullCheckBox.setChecked(True)
        if self.param_list is not None and len(self.param_list) > 0:
            self.model.setItems(self.param_list)
        enableMainNotNullSlot = partial(self.check_main_not_null, self.ui.mainNotNullCheckBox)
        disableMainNotNullSlot = partial(self.uncheck_main_not_null, self.ui.mainNotNullCheckBox)
        self.ui.mainNotNullCheckBox.stateChanged.connect(
            lambda x: enableMainNotNullSlot() if x else disableMainNotNullSlot()
        )
        self.accepted.connect(self.on_ok_button_click)

    def uncheck_main_not_null(self, checkbox):
        self.main_not_null = False

    def check_main_not_null(self, checkbox):
        self.main_not_null = True

    def on_table_click(self):
        index = self.ui.tableView.selectedIndexes()
        if len(index) > 0:
            index = index[0]
        if index.isValid():
            self.select_row_index = index.row()
            self.select_param = self.param_list[index.row()]["parameter"]
            self.select_arg = self.param_list[index.row()]["arg"]
            self.merge_method = self.param_list[index.row()]["merge_method"]
            self.tolerance = self.param_list[index.row()]["tolerance"]
            self.ui.editButton.setEnabled(True)
            self.ui.removeButton.setEnabled(True)

    def on_add_parameter_button_click(self):
        dlg = add_custom_table_param_dialog.add_custom_table_param_dialog(self.on_param_added)
        dlg.show()

    def on_edit_parameter_button_click(self):
        dlg = add_custom_table_param_dialog.add_custom_table_param_dialog(self.on_param_edited, self.select_param, arg=self.select_arg, merge_method=self.merge_method, tolerance=self.tolerance)
        dlg.show()

    def on_remove_parameter_button_click(self):
        del self.param_list[self.select_row_index]
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
                except:
                    pass

    def on_param_added(self, param_dict):
        found = False
        for param in self.param_list:
            if param["parameter name"] == param_dict["parameter name"] and param["merge_method"] == param_dict["merge_method"] and param["tolerance"] == param_dict["tolerance"]:
                found = True
                break
        if not found:
            self.param_list.append(param_dict)
            self.model.setItems(self.param_list)

    def on_param_edited(self, param_dict):
        self.param_list[self.select_row_index] = param_dict
        self.model.setItems(self.param_list)

    def on_update_table(self, model):
        self.ui.tableView.setModel(model)
    
    def merge_custom_param_to_df(self, param_list):
        main_df = None
        param_df_list = copy.deepcopy(param_list)
        # param_df_list = param_list.copy()
        if self.gc.databasePath is not None:
            with contextlib.closing(sqlite3.connect(self.gc.databasePath)) as dbcon:
                for param_dict in param_df_list:
                    param_name = param_dict["parameter name"]
                    table_name = preprocess_azm.get_table_for_column(param_name.split("/")[0])
                    sql = "SELECT log_hash, time, {} FROM {}".format(param_name, table_name)
                    if self.selected_logs is not None:
                        import sql_utils
                        where = "where log_hash in ({})".format(','.join([str(selected_log) for selected_log in self.selected_logs]))
                        sql = sql_utils.add_first_where_filt(sql, where)
                    df = pd.read_sql(sql, dbcon, parse_dates=["time"])
                    df["log_hash"] = df["log_hash"].astype(np.int64)
                    df = df.sort_values(by="time")
                    if param_dict["main parameter"]:
                        main_param_name = param_name
                        main_df = df
                    else:
                        param_dict["df"] = df

                if main_df is None:
                    main_df = param_df_list[0]["df"]
                    main_param_name = param_df_list[0]["parameter name"]
                    param_df_list[0]["main parameter"] = True
                    del param_df_list[0]
                if self.main_not_null:
                    main_df = main_df.dropna().sort_values(by="time")
                df_merge = main_df.copy()
                df_merge = df_merge.dropna().sort_values(by="time")
                main_df = pd.merge_asof(left=main_df.reset_index(), right=df_merge.reset_index(), left_on=['time'], right_on=['time'],by='log_hash', direction="backward", allow_exact_matches=True, tolerance=pd.Timedelta('2s'), suffixes=('_not_use', '')) 
                main_df = main_df[["log_hash", "time", main_param_name]]
                main_df = main_df.rename(columns={main_param_name:main_param_name+"_main"})
                if len(main_df) > 0:
                    tmp_df_1 = main_df.copy()

                    for param_dict in param_df_list:
                        if param_dict["main parameter"] == False:
                            main_df = main_df.reset_index(drop=True)
                            df = param_dict["df"]
                            param_name = param_dict["parameter name"]
                            tolerance = param_dict["tolerance"]+"ms"
                            merge_method = param_dict["merge_method"]
                            param_name_alias = param_name+"_"+merge_method+"_"+tolerance
                            tmp_df = tmp_df_1.copy()
                            tmp_df["time_tmp"] = tmp_df["time"]
                            tmp_col = tmp_df.columns.tolist()
                            main_col = main_df.columns.tolist()
                            tmp_df = pd.merge_asof(left=df.sort_values(by="time"), right=tmp_df.sort_values(by="time"), left_on=['time'], right_on=['time'], by='log_hash', direction="forward", allow_exact_matches=True, tolerance=pd.Timedelta(tolerance))
                            tmp_col.remove("time")
                            tmp_df = tmp_df[tmp_col+[param_name]]
                            tmp_df = eval("tmp_df.groupby(tmp_col)."+merge_method)
                            tmp_df = tmp_df.reset_index()
                            tmp_df = tmp_df.rename(columns={param_name:param_name_alias, "time_tmp":"time"})
                            main_df = main_df.merge(tmp_df, how="left", on="time", suffixes=("", "_not_use"))
                            main_df = main_df[main_col+[param_name_alias]]

                # for df in df_list:
                #     main_df = main_df.reset_index(drop=True)
                #     print("main_df",main_df, "df",df)
                #     main_df = pd.merge_asof(left=main_df, right=df, left_on=['time'], right_on=['time'], by='log_hash', allow_exact_matches=True, tolerance=pd.Timedelta('1s'))
                return main_df 

    def on_ok_button_click(self):
        df = self.merge_custom_param_to_df(self.param_list)
        self.window_name = self.ui.windowNameLineEdit.text()
        self.on_result.emit(df, self.param_list, self.window_name, self.selected_ue, self.main_not_null)