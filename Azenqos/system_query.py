from PyQt5.QtSql import QSqlQuery, QSqlDatabase
import pandas as pd
import numpy as np
import azq_utils


def get_technology_df(dbcon, time_before):
    rat_to_table_and_primary_where_dict = {
        "NR": "nr_cell_meas",
        "LTE": "lte_cell_meas",
        "WCDMA": "wcdma_cell_meas",
        "GSM": "gsm_cell_meas",
    }
    rat_to_main_param_dict = {
        "NR": "nr_servingbeam_ss_rsrp_1",
        "LTE": "lte_inst_rsrp_1",
        "WCDMA": "wcdma_aset_ecio_1",
        "GSM": "gsm_rxlev_sub_dbm",
    }
    per_rat_df_list = []
    for rat in rat_to_table_and_primary_where_dict:
        try:
            sql = "select log_hash, time, {} as main_param from {}".format(
                rat_to_main_param_dict[rat], rat_to_table_and_primary_where_dict[rat])
            df = pd.read_sql(sql, dbcon, parse_dates=["Time"])
            df["rat"] = rat
            if rat == 'NR':
                df = df.ffill(limit=5)
            per_rat_df_list.append(df)
        except Exception as e:
            print("WARNING: gen per_rat_df failed:", e)
    df = pd.concat(per_rat_df_list, ignore_index=True)
    df.sort_values(["log_hash", "time", "rat"], inplace=True)
    df = df[~pd.isnull(df.main_param)]
    return df
