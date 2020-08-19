import pandas as pd
import os
import sys
import traceback
import collections
from datetime import datetime

# get pandas dataframe suitable for show in 'datatable.py' through PdTableModel
''' parameter_to_column_table_set:
        PARAMS = [
            ("Beam ID", "nr_servingbeam_pci_"),
            ("Band", "nr_band_"),
            ("Band Type", "nr_band_type_"),
            ("ARFCN", "nr_dl_arfcn_"),
            ("Frequency", "nr_dl_frequency_"),
            ("PCI", "nr_servingbeam_pci_"),
            ("RSRP", "nr_servingbeam_ss_rsrp_"),
            ("RSRQ", "nr_servingbeam_ss_rsrq_"),
            ("SINR", "nr_servingbeam_ss_sinr_"),
            ("Bandwidth", "nr_bw_"),
            ("SSB SCS", "nr_ssb_scs_"),
            ("SCS", "nr_numerology_scs_"),
            ("PUSCH Power", "nr_pusch_tx_power_"),
            ("PUCCH Power", "nr_pucch_tx_power_"),
            ("SRS Power", "nr_srs_tx_power_"),
        ]
'''

def get(dbcon, parameter_to_columns_list, time_before, default_table=None, common_param_index_suffix_list=[], not_null_first_col=False, custom_lookback_dur_millis=None):
    df_list = []
    for param_set in parameter_to_columns_list:
        param_name = param_set[0]
        param_cols = list(param_set[1])
        print("param_cols:", param_cols)
        assert isinstance(param_name, str)
        assert isinstance(param_cols, list)            
        param_table = default_table
        param_where_and = ""
        if not_null_first_col:
            param_where_and = "and {} is not null".format(param_cols[0])
        if len(param_set) >= 3:
            if param_set[2]:
                param_table = param_set[2]
        if len(param_set) >= 4:
            if param_set[3]:
                param_where_and = param_set[3]
        cols_part = ", ".join(param_cols)
        time_after_and = ""
        if custom_lookback_dur_millis:
            assert isinstance(custom_lookback_dur_millis, int)
            dt_before = pd.to_datetime(time_before)
            #print("dt_before:", dt_before)
            dt_after = dt_before - pd.Timedelta(custom_lookback_dur_millis, 'ms')
            #print("dt_after:", dt_after)
            time_after_and = "and time >= '{}'".format(dt_after)
            
        sqlstr = "select '{}' as param, {} from {} where time <= '{}' {} {} order by time desc limit 1".format(
            param_name,
            cols_part,
            param_table,
            time_before,
            time_after_and,
            param_where_and
        )
        
        #print("params_disp_df sql:", sqlstr)        
        df = pd.read_sql(sqlstr, dbcon)
        #print("params_disp_df sql df head:\n", df.head())
        if len(df) == 0:
            df = pd.DataFrame({"param":[param_name]})
            for i in range(1, len(param_cols)+1):
                df[i] = None

        if len(df.columns) > 1:
            #pass
            df.columns = ["param"] + list(range(1, len(df.columns)))


        #print("params_disp_df df final head:\n", df.head())
        df_list.append(df)

    return pd.concat(df_list, sort=False)
