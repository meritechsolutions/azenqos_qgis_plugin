import os
import contextlib
import sqlite3

import pandas as pd
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QDialog, QCompleter, QComboBox
from PyQt5.uic import loadUi

from add_param_dialog import CustomQCompleter
import azq_utils
import db_preprocess

lte_param_list = ["lte_inst_rsrp_1", "lte_inst_rsrq_1", "lte_sinr_1", "lte_earfcn_1", "lte_physical_cell_id_1"]
lte_neigh_macth_param_dict = {"lte_inst_rsrp_1":"lte_neigh_rsrp", "lte_inst_rsrq_1":"lte_neigh_rsrq", "lte_earfcn_1":"lte_neigh_earfcn", "lte_physical_cell_id_1":"lte_neigh_physical_cell_id"}

class lte_pci_wise_dialog(QDialog):

    def __init__(self, parent, gc):
        super(lte_pci_wise_dialog, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.gc = gc
        self.param = lte_param_list[0]
        self.pci_list = None
        self.setupUi()
        
    def setupUi(self):
        dirname = os.path.dirname(__file__)
        self.setWindowIcon(QIcon(QPixmap(os.path.join(dirname, "icon.png"))))
        self.ui = loadUi(azq_utils.get_module_fp("lte_pci_wise_dialog.ui"), self)
        self.setWindowTitle("LTE PCI Footprint")
        self.ui.param_cb.setEditable(True)
        self.ui.param_cb.setInsertPolicy(QComboBox.NoInsert)
        completer = CustomQCompleter(self.ui.param_cb)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setModel(self.ui.param_cb.model())
        self.ui.param_cb.setCompleter(completer)
        for param in lte_param_list:
            self.ui.param_cb.addItem(param)
        self.ui.param_cb.currentIndexChanged.connect(self.selectParam)
        self.accepted.connect(self.create_pci_wise_layer)

    def selectParam(self):
        self.setParam()

    def setParam(self):
        self.param = self.ui.param_cb.currentText()
    
    def create_pci_wise_layer(self):
        self.pci_list = self.ui.pci_le.text().strip()
        self.pci_list = self.pci_list.replace("[","")
        self.pci_list = self.pci_list.replace("]","")
        if self.pci_list is  None or self.pci_list == "":
            raise Exception("please enter pci")
        if not isinstance(self.pci_list, list):
            self.pci_list = self.pci_list.split(",")
            self.pci_list = map(lambda x: x.strip(), self.pci_list)
        
        if self.gc.databasePath is not None:
            with contextlib.closing(sqlite3.connect(self.gc.databasePath)) as dbcon:
                if self.param == 'lte_physical_cell_id_1':
                    sqlstr_for_get_pci = "select log_hash, time, {}, geom from lte_cell_meas".format(self.param)
                else:
                    sqlstr_for_get_pci = "select log_hash, time, {}, geom, lte_physical_cell_id_1 from lte_cell_meas".format(self.param)
                lte_cell_meas_df = pd.read_sql(sqlstr_for_get_pci, dbcon, parse_dates=['time'])
                valid_pci_list = lte_cell_meas_df.lte_physical_cell_id_1.dropna().astype(int).astype(str).unique()
                self.pci_list = list(set(self.pci_list) & set(valid_pci_list))
                df = lte_cell_meas_df[lte_cell_meas_df[self.param].notnull()]
                df_location = pd.read_sql("select time, log_hash, positioning_lat, positioning_lon from location where positioning_lat is not null and positioning_lon is not null", dbcon, parse_dates=['time'])
                if self.gc.is_indoor:
                    df = db_preprocess.add_pos_lat_lon_to_indoor_df(df, df_location).rename(
                    columns={"positioning_lat": "lat", "positioning_lon": "lon"}).reset_index(drop=True)
                    if "geom" in df.columns:
                        del df["geom"]
                for pci in self.pci_list:
                    print('pci :', pci)
                    pci = int(pci)
                    per_pci_df = df.loc[df["lte_physical_cell_id_1"]==pci].reset_index(drop=True)
                    layer_name = "{} per PCI: {}".format(self.param, pci)
                    theme_param = self.param
                    if len(per_pci_df) > 0:
                        azq_utils.create_layer_in_qgis(self.gc.databasePath, per_pci_df, layer_name, theme_param = theme_param)
                    if self.param in lte_neigh_macth_param_dict.keys():
                        nb_param = lte_neigh_macth_param_dict[self.param]
                        layer_name = "{} per PCI: {}".format(nb_param, pci)
                        sqlstr_lte_nb = "select * from lte_neigh_meas order by log_hash, time"
                        lte_nb_df = pd.read_sql(sqlstr_lte_nb, dbcon, parse_dates=['time'])
                        if self.gc.is_indoor:
                            lte_nb_df = db_preprocess.add_pos_lat_lon_to_indoor_df(lte_nb_df, df_location).rename(
                            columns={"positioning_lat": "lat", "positioning_lon": "lon"}).reset_index(drop=True)
                            if "geom" in lte_nb_df.columns:
                                del lte_nb_df["geom"]
                        all_nb_per_pci_df = []
                        for i in range(1, 17):
                            nb_args = nb_param + "_{}".format(i)
                            lte_neigh_physical_cell_id = "lte_neigh_physical_cell_id_{}".format(i)
                            nb_per_pci_df = lte_nb_df.loc[lte_nb_df[lte_neigh_physical_cell_id] == pci]

                            if self.param == 'lte_physical_cell_id_1':
                                nb_per_pci_df = nb_per_pci_df.rename(columns={nb_args: "lte_physical_cell_id_1"})
                                nb_per_pci_df = nb_per_pci_df[["log_hash", "time", "lte_physical_cell_id_1"]]
                            else:
                                nb_per_pci_df = nb_per_pci_df.rename(columns={nb_args: self.param, lte_neigh_physical_cell_id: "lte_physical_cell_id_1"})
                                nb_per_pci_df = nb_per_pci_df[["log_hash", "time", "lte_physical_cell_id_1", self.param]]

                            all_nb_per_pci_df.append(nb_per_pci_df)

                        all_nb_per_pci_df = pd.concat(all_nb_per_pci_df, ignore_index=True)
                        if len(all_nb_per_pci_df) > 0:
                            azq_utils.create_layer_in_qgis(self.gc.databasePath, all_nb_per_pci_df, layer_name, theme_param = theme_param)
        
