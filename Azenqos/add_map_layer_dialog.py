import PyQt5
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QDialog, QMessageBox

import os
import contextlib
import sqlite3
import pandas as pd

import azq_utils
import preprocess_azm
import db_preprocess

class add_map_layer_dialog(QDialog):
    def __init__(self, gc, param, n_arg_max):
        super(add_map_layer_dialog, self).__init__(None)
        self.gc = gc
        self.param = param
        self.param_name = param
        self.n_arg_max = n_arg_max
        self.arg = "1"
        self.setAttribute(PyQt5.QtCore.Qt.WA_DeleteOnClose)
        self.setupUi()

    def setupUi(self):
        dirname = os.path.dirname(__file__)
        self.ui = loadUi(azq_utils.get_module_fp("add_param_dialog_old.ui"), self)
        self.setWindowIcon(QIcon(QPixmap(os.path.join(dirname, "icon.png"))))
        self.setWindowTitle("Select Parameter Argument")
        self.ui.not_null_checkbox.hide()
        self.ui.data_checkbox.hide()
        self.ui.comboBox.addItem(self.param)
        self.ui.comboBox.setEditable(False)
        self.ui.comboBox.setEnabled(False)
        self.ui.comboBox_2.addItem(self.arg)
        for i in range(int(self.n_arg_max)):
            arg = str(i+1)
            self.ui.comboBox_2.addItem(arg)
        self.select_arg()
        self.ui.comboBox_2.currentIndexChanged.connect(self.select_arg)
        self.accepted.connect(self.on_accept_button_clicked)

    def select_arg(self):
        self.set_arg()
        if int(self.n_arg_max) > 1:
            self.param_name = self.param + "_" + self.arg

    def set_arg(self):
        self.arg = self.ui.comboBox_2.currentText()

    def on_accept_button_clicked(self):
        try:
            if len(self.gc.device_configs) > 1 :
                import select_log_dialog
                dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
                result = dlg.exec_()
                if not result:
                    return
                selected_ue = dlg.log
            create_param_layer(self.gc, self.param, selected_ue)
        except Exception as e:
            QMessageBox.warning(
                None,
                "Warning",
                e.args[0],
                QMessageBox.Ok,
            )
            return


call_type_dict = {"call_init":"call_init_time", "call_setup":"call_setup_duration", "call_established":"call_setup_duration", "call_end":"call_end_cause", "call_block":"call_end_cause", "call_drop":"call_end_cause"}

def create_param_layer(gc, param_name, selected_ue=None):
    if gc.databasePath is not None:
        with contextlib.closing(sqlite3.connect(gc.databasePath)) as dbcon:
            table_name = preprocess_azm.get_table_for_column(param_name.split("/")[0])
            sqlstr = "select log_hash, time, {} from {}".format(param_name , table_name)
            location_sqlstr = "select time, log_hash, positioning_lat, positioning_lon from location where positioning_lat is not null and positioning_lon is not null"
            layer_name = param_name
            pp_voice_table = None
            if param_name in call_type_dict.keys():
                param_name = call_type_dict[param_name]
                pp_voice_table = "pp_voice_report"
                sqlstr = "select * from pp_voice_report"
            if selected_ue is not None:
                import sql_utils
                title_ue_suffix = "(" + gc.device_configs[selected_ue]["name"] + ")"
                if title_ue_suffix not in param_name:
                    layer_name = layer_name + title_ue_suffix 
                    selected_logs = gc.device_configs[selected_ue]["log_hash"]
                    where = "where log_hash in ({})".format(','.join([str(selected_log) for selected_log in selected_logs]))
                    sqlstr = sql_utils.add_first_where_filt(sqlstr, where)
                    location_sqlstr = sql_utils.add_first_where_filt(location_sqlstr, where)
            df = pd.read_sql(sqlstr, dbcon, parse_dates=['time'])
            df = df.loc[df[param_name].notna()]
            theme_param = param_name
            if layer_name.startswith('call_init'):
                theme_param = None
                df = df.query('not call_init_time.isnull()')
            elif layer_name.startswith('call_setup'):
                df = df.query('not call_setup_duration.isnull()')
            elif layer_name.startswith('call_block'):
                df = df.query('detected_radio_voice_call_end_type == "Call Block"')
            elif layer_name.startswith('call_drop'):
                df = df.query('detected_radio_voice_call_end_type == "Call Drop"')
            elif layer_name.startswith('call_establish'):
                df = df.query('not call_established_time.isnull()')
            elif layer_name.startswith('call_end'):
                df = df[(df.detected_radio_voice_call_end_type == "Call End") & pd.notnull(df.call_established_time)]
            df_location = pd.read_sql(location_sqlstr, dbcon, parse_dates=['time'])
            if gc.is_indoor:
                df = db_preprocess.add_pos_lat_lon_to_indoor_df(df, df_location).rename(
                columns={"positioning_lat": "lat", "positioning_lon": "lon"}).reset_index(drop=True)
                if "geom" in df.columns:
                    del df["geom"]
            if len(df) == 0:
                raise Exception("No {} in this log".format(param_name))
            azq_utils.create_layer_in_qgis(gc.databasePath, df, layer_name, theme_param = theme_param, pp_voice_table=pp_voice_table)
