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
import sql_utils

nr_param_list = ["nr_servingbeam_ss_rsrp_1", "nr_servingbeam_ss_rsrq_1", "nr_servingbeam_ss_sinr_1", "nr_dl_arfcn_1", "nr_servingbeam_pci_1"]
nr_neigh_macth_param_dict = {"nr_servingbeam_ss_rsrp_1":"nr_detectedbeam_ss_rsrp_1", "nr_servingbeam_ss_rsrq_1":"nr_detectedbeam_ss_rsrq_1", "nr_dl_arfcn_1":"nr_detectedbeam_dl_arfcn_1", "nr_servingbeam_pci_1":"nr_detectedbeam_pci_1"}

lte_param_list = ["lte_inst_rsrp_1", "lte_inst_rsrq_1", "lte_sinr_1", "lte_earfcn_1", "lte_physical_cell_id_1"]
lte_neigh_macth_param_dict = {"lte_inst_rsrp_1":"lte_neigh_rsrp", "lte_inst_rsrq_1":"lte_neigh_rsrq", "lte_earfcn_1":"lte_neigh_earfcn", "lte_physical_cell_id_1":"lte_neigh_physical_cell_id"}

wcdma_param_list = ["wcdma_aset_ecio_1", "wcdma_aset_rscp_1", "wcdma_aset_cellfreq_1", "wcdma_aset_sc_1"]
wcdma_neigh_macth_param_dict = {"wcdma_aset_ecio_1":"wcdma_mset_ecio", "wcdma_aset_rscp_1":"wcdma_mset_rscp", "wcdma_aset_cellfreq_1":"wcdma_mset_cellfreq", "wcdma_aset_sc_1":"wcdma_mset_sc"}

gsm_param_list = ["gsm_rxlev_sub_dbm", "gsm_rxqual_sub", "gsm_bsic", "gsm_arfcn_bcch"]
gsm_neigh_macth_param_dict = {"gsm_rxlev_sub_dbm":"gsm_neighbor_rxlev_dbm", "gsm_bsic":"gsm_neighbor_bsic", "gsm_arfcn_bcch":"gsm_neighbor_arfcn"}

class footprint_dialog(QDialog):

    def __init__(self, parent, gc, title, technology, selected_ue = None):
        super(footprint_dialog, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.gc = gc
        self.log_list = gc.log_list
        self.title = title
        self.technology = technology.lower()
        self.selected_ue = selected_ue
        self.selected_log = None
        if len(self.log_list):
            self.selected_log = str(self.log_list[0])
        if len(self.log_list) > 1 and self.selected_ue is not None:
            title_ue_suffix = "( UE" + str(self.selected_ue) + " )"
            if title_ue_suffix not in self.title:
                self.title = self.title + title_ue_suffix
            if int(self.selected_ue) <= len(self.log_list):
                self.selected_log = str(self.log_list[int(self.selected_ue)-1])
        if self.technology == "nr":
            self.nb_table = "nr_intra_neighbor"
            self.footprint_param = "nr_servingbeam_pci_1"
            self.label_name = "NR PCI"
            self.param_list = nr_param_list
            self.neigh_macth_param_dict = nr_neigh_macth_param_dict
        elif self.technology == "lte":
            self.nb_table = "lte_neigh_meas"
            self.footprint_param = "lte_physical_cell_id_1"
            self.label_name = "LTE PCI"
            self.param_list = lte_param_list
            self.neigh_macth_param_dict = lte_neigh_macth_param_dict
        elif self.technology == "wcdma":
            self.nb_table = "wcdma_cell_meas"
            self.footprint_param = "wcdma_aset_sc_1"
            self.label_name = "WCDMA PSC"
            self.param_list = wcdma_param_list
            self.neigh_macth_param_dict = wcdma_neigh_macth_param_dict
        elif self.technology == "gsm":
            self.nb_table = "gsm_cell_meas"
            self.footprint_param = "gsm_arfcn_bcch"
            self.label_name = "GSM BCCH"
            self.param_list = gsm_param_list
            self.neigh_macth_param_dict = gsm_neigh_macth_param_dict
        self.param = self.param_list[0]
        self.pci_list = None
        self.setupUi()
        
    def setupUi(self):
        dirname = os.path.dirname(__file__)
        self.setWindowIcon(QIcon(QPixmap(os.path.join(dirname, "icon.png"))))
        self.ui = loadUi(azq_utils.get_module_fp("lte_pci_wise_dialog.ui"), self)
        self.setWindowTitle(self.title)
        self.ui.param_cb.setEditable(True)
        self.ui.param_cb.setInsertPolicy(QComboBox.NoInsert)
        self.ui.pci_lb.setText(self.label_name+" List")
        completer = CustomQCompleter(self.ui.param_cb)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setModel(self.ui.param_cb.model())
        self.ui.param_cb.setCompleter(completer)
        for param in self.param_list:
            self.ui.param_cb.addItem(param)
        self.ui.param_cb.currentIndexChanged.connect(self.selectParam)
        self.accepted.connect(self.create_footprint_layer)

    def selectParam(self):
        self.setParam()

    def setParam(self):
        self.param = self.ui.param_cb.currentText()
    
    def create_footprint_layer(self):
        self.pci_list = self.ui.pci_le.text().strip()
        self.pci_list = self.pci_list.replace("[","")
        self.pci_list = self.pci_list.replace("]","")
        if self.pci_list is None or self.pci_list == "":
            raise Exception("please enter {}".format(self.label_name))
        if not isinstance(self.pci_list, list):
            self.pci_list = self.pci_list.split(",")
            self.pci_list = map(lambda x: x.strip(), self.pci_list)
        
        if self.gc.databasePath is not None:
            with contextlib.closing(sqlite3.connect(self.gc.databasePath)) as dbcon:
                if self.param == self.footprint_param:
                    sqlstr_for_get_pci = "select log_hash, time, {}, geom from {}_cell_meas".format(self.param, self.technology)
                else:
                    sqlstr_for_get_pci = "select log_hash, time, {}, geom, {} from {}_cell_meas".format(self.param, self.footprint_param, self.technology)

                sqlstr_for_get_location = "select time, log_hash, positioning_lat, positioning_lon from location where positioning_lat is not null and positioning_lon is not null"
                if self.selected_log is not None:
                    where = "where log_hash = '{}'".format(self.selected_log)
                    sqlstr_for_get_pci = sql_utils.add_first_where_filt(sqlstr_for_get_pci, where)
                    sqlstr_for_get_location = sql_utils.add_first_where_filt(sqlstr_for_get_location, where)
                cell_meas_df = pd.read_sql(sqlstr_for_get_pci, dbcon, parse_dates=['time'])
                valid_pci_list = cell_meas_df[self.footprint_param].dropna().astype(int).astype(str).unique()
                self.pci_list = list(set(self.pci_list) & set(valid_pci_list))
                df = cell_meas_df[cell_meas_df[self.param].notnull()]
                df_location = pd.read_sql(sqlstr_for_get_location, dbcon, parse_dates=['time'])
                if self.gc.is_indoor:
                    df = db_preprocess.add_pos_lat_lon_to_indoor_df(df, df_location).rename(
                    columns={"positioning_lat": "lat", "positioning_lon": "lon"}).reset_index(drop=True)
                    if "geom" in df.columns:
                        del df["geom"]
                for pci in self.pci_list:
                    print('pci :', pci)
                    pci = int(pci)
                    per_pci_df = df.loc[df[self.footprint_param]==pci].reset_index(drop=True)
                    layer_name = "{} per {}: {}".format(self.param, self.label_name,pci)
                    
                    if len(self.log_list) > 1 and self.selected_ue is not None:
                        title_ue_suffix = "( UE" + str(self.selected_ue) + " )"
                        layer_name = layer_name + title_ue_suffix
                    theme_param = self.param
                    if len(per_pci_df) > 0:
                        azq_utils.create_layer_in_qgis(self.gc.databasePath, per_pci_df, layer_name, theme_param = theme_param)
                    if self.param in self.neigh_macth_param_dict.keys():
                        nb_param = self.neigh_macth_param_dict[self.param]
                        layer_name = "{} per {}: {}".format(nb_param, self.label_name,pci)
                        sqlstr_lte_nb = "select * from {} order by log_hash, time".format(self.nb_table)
                        if self.selected_log is not None:
                            where = "where log_hash = '{}'".format(self.selected_log)
                            sqlstr_lte_nb = sql_utils.add_first_where_filt(sqlstr_lte_nb, where)
                        nb_df = pd.read_sql(sqlstr_lte_nb, dbcon, parse_dates=['time'])
                        if self.gc.is_indoor:
                            nb_df = db_preprocess.add_pos_lat_lon_to_indoor_df(nb_df, df_location).rename(
                            columns={"positioning_lat": "lat", "positioning_lon": "lon"}).reset_index(drop=True)
                            if "geom" in nb_df.columns:
                                del nb_df["geom"]
                        if self.param in nb_df.columns:
                            del nb_df[self.param]
                        if self.footprint_param in nb_df.columns:
                            del nb_df[self.footprint_param]
                        all_nb_per_pci_df = []
                        nb_n_arg = 17
                        if self.technology == "nr":
                            nb_n_arg = 7
                        for i in range(1, nb_n_arg):
                            if self.technology != "nr":
                                nb_args = nb_param + "_{}".format(i)
                                nb_footprint = "{}_{}".format(self.neigh_macth_param_dict[self.footprint_param],i)
                            else:
                                nb_args = nb_param.replace("detectedbeam", "detectedbeam{}".format(i))
                                nb_footprint = self.neigh_macth_param_dict[self.footprint_param].replace("detectedbeam", "detectedbeam{}".format(i))

                            nb_per_pci_df = nb_df.loc[nb_df[nb_footprint] == pci]

                            if self.param == self.footprint_param:
                                nb_per_pci_df = nb_per_pci_df.rename(columns={nb_args: self.footprint_param})
                                nb_per_pci_df[nb_param] = nb_per_pci_df[self.footprint_param]
                                nb_per_pci_df = nb_per_pci_df[["log_hash", "time", self.footprint_param, nb_param]]
                            else:
                                nb_per_pci_df = nb_per_pci_df.rename(columns={nb_args: self.param, nb_footprint: self.footprint_param})
                                nb_per_pci_df[nb_param] = nb_per_pci_df[self.param]
                                nb_per_pci_df[self.neigh_macth_param_dict[self.footprint_param]] = nb_per_pci_df[self.footprint_param]
                                nb_per_pci_df = nb_per_pci_df[["log_hash", "time", self.footprint_param, self.param, nb_param, self.neigh_macth_param_dict[self.footprint_param]]]

                            all_nb_per_pci_df.append(nb_per_pci_df)

                        all_nb_per_pci_df = pd.concat(all_nb_per_pci_df, ignore_index=True)
                        if len(all_nb_per_pci_df) > 0:
                            if len(self.log_list) > 1 and self.selected_ue is not None:
                                title_ue_suffix = "( UE" + str(self.selected_ue) + " )"
                                layer_name = layer_name + title_ue_suffix
                            azq_utils.create_layer_in_qgis(self.gc.databasePath, all_nb_per_pci_df, layer_name, theme_param = theme_param)
        
