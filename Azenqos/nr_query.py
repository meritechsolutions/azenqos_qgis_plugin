from PyQt5.QtSql import QSqlQuery, QSqlDatabase
import re
import sqlite3
import pandas as pd
import global_config as gc
import params_disp_df


class NrDataQuery:
    def __init__(self, database, currentDateTimeString):
        self.timeFilter = ""
        self.azenqosDatabase = database
        if currentDateTimeString:
            self.timeFilter = currentDateTimeString

    def getRadioParameters(self):
        with sqlite3.connect(gc.databasePath) as dbcon:
            return get_nr_radio_params_disp_df(dbcon, self.timeFilter)
    
    def getServingAndNeighbors(self):
        with sqlite3.connect(gc.databasePath) as dbcon:
            return get_nr_serv_and_neigh_disp_df(dbcon, self.timeFilter)
        
    def defaultData(self, fieldsList, dataList):
        fieldCount = len(fieldsList)
        if fieldCount > 0:
            for index in range(fieldCount):
                columnName = fieldsList[index]
                dataList.append([columnName, "", "", ""])
            return dataList


################################## df get functions


def get_nr_radio_params_disp_df(dbcon, time_before):
    n_param_args = 8
    parameter_to_columns_list = [
        ("Time", ["time"] ),            
        (  # these params below come together so query them all in one query
            [
                "Band",
                "ARFCN",
                "PCI",
                "RSRP",
                "RSRQ",
                "SINR"
            ],
            list(map(lambda x: "nr_band_{}".format(x+1), range(n_param_args))) +
            list(map(lambda x: "nr_dl_arfcn_{}".format(x+1), range(n_param_args))) +
            list(map(lambda x: "nr_servingbeam_pci_{}".format(x+1), range(n_param_args))) +
            list(map(lambda x: "nr_servingbeam_ss_rsrp_{}".format(x+1), range(n_param_args))) +
            list(map(lambda x: "nr_servingbeam_ss_rsrq_{}".format(x+1), range(n_param_args))) +
            list(map(lambda x: "nr_servingbeam_ss_sinr_{}".format(x+1), range(n_param_args)))
        ),
        (  # these params below come together but not same row with rsrp etc above so query them all in their own set below
            [
                "PUSCH TxPower",
                "PUCCH TxPower",
                "SRS TxPower"
            ],
            list(map(lambda x: "nr_pusch_tx_power_{}".format(x+1), range(n_param_args)))+
            list(map(lambda x: "nr_pucch_tx_power_{}".format(x+1), range(n_param_args)))+
            list(map(lambda x: "nr_srs_tx_power_{}".format(x+1), range(n_param_args)))
        )
    ]            
    return params_disp_df.get(dbcon, parameter_to_columns_list, time_before, default_table="nr_cell_meas", not_null_first_col=True, custom_lookback_dur_millis=gc.DEFAULT_LOOKBACK_DUR_MILLIS)


def get_nr_serv_and_neigh_disp_df(dbcon, time_before):
    df_list = []

    pcell_scell_col_prefix_sr = pd.Series(["nr_dl_arfcn_", "nr_servingbeam_pci_", "nr_servingbeam_ss_rsrp_", "nr_servingbeam_ss_rsrq_", "nr_servingbeam_ss_sinr_"])
    pcell_scell_col_prefix_renamed = ["ARFCN","PCI", "RSRP","RSRQ","SINR"]
    parameter_to_columns_list = [
        ("Time", ["time"] ),
        (
            ["PCell","SCell1","SCell2","SCell3","SCell4","SCell5","SCell6","SCell7"],
            list(pcell_scell_col_prefix_sr+"1")+list(pcell_scell_col_prefix_sr+"2")+list(pcell_scell_col_prefix_sr+"3")+list(pcell_scell_col_prefix_sr+"4")+list(pcell_scell_col_prefix_sr+"5")+list(pcell_scell_col_prefix_sr+"6")+list(pcell_scell_col_prefix_sr+"7")+list(pcell_scell_col_prefix_sr+"8"),
        )
    ]
    df = params_disp_df.get(dbcon, parameter_to_columns_list, time_before, default_table="nr_cell_meas", not_null_first_col=True, custom_lookback_dur_millis=gc.DEFAULT_LOOKBACK_DUR_MILLIS)
    #print("df.head():\n%s" % df.head())
    df.columns = ["CellGroup"]+pcell_scell_col_prefix_renamed
    #print("df.head():\n%s" % df.head())
    df_list.append(df)

    dcell_col_suffix_sr = pd.Series(["_pci_1", "_ss_rsrp_1", "_ss_rsrq_1", "_ss_sinr_1"])  # a mistake during elm sheets made this unnecessary _1 required
    dcell_col_renamed = ["PCI", "RSRP","RSRQ","SINR"]
    dparameter_to_columns_list = [
        (
            ["DCell1","DCell2","DCell3","DCell4"],
            list("nr_detectedbeam1"+dcell_col_suffix_sr) + list("nr_detectedbeam2"+dcell_col_suffix_sr) + list("nr_detectedbeam3"+dcell_col_suffix_sr) + list("nr_detectedbeam4"+dcell_col_suffix_sr),
        )

    ]
    dcell_df = params_disp_df.get(dbcon, dparameter_to_columns_list, time_before, default_table="nr_cell_meas", not_null_first_col=True, custom_lookback_dur_millis=gc.DEFAULT_LOOKBACK_DUR_MILLIS)
    #print("0dcell_df.head():\n%s" % dcell_df.head())
    dcell_df.columns = ["CellGroup"]+dcell_col_renamed
    #print("dcell_df.head():\n%s" % dcell_df.head())
    df_list.append(dcell_df)

    final_df = pd.concat(df_list, sort=False)
    return final_df
