import numpy as np
import pandas as pd

import params_disp_df
import preprocess_azm

############ New Line Chart Query


def get_chart_df(dbcon, param_list_dict, gc):
    import sql_utils
    df_list = []
    print(param_list_dict)
    for key in param_list_dict:
        where = None
        param_dict = param_list_dict[key]
        param_name = param_dict["name"]
        param_alias_name = param_name
        table_name = preprocess_azm.get_table_for_column(param_name.split("/")[0])
        if "selected_ue" in param_dict:
            if param_dict["selected_ue"] is not None:
                selected_logs = gc.device_configs[param_dict["selected_ue"]]["log_hash"]
                where = "where log_hash in ({})".format(','.join([str(selected_log) for selected_log in selected_logs]))
                title_ue_suffix = gc.device_configs[param_dict["selected_ue"]]["name"]
                if title_ue_suffix not in param_alias_name:
                    param_alias_name = param_alias_name + "_" + title_ue_suffix
                param_name = param_name+" as "+param_alias_name
        sql = "SELECT log_hash, time as Time, {} FROM {}".format(param_name, table_name)
        sql = sql_utils.add_first_where_filt(sql, where)
        df = pd.read_sql(sql, dbcon, parse_dates=["Time"])
        df["log_hash"] = df["log_hash"].astype(np.int64)
        df = df.sort_values(by="Time")
        df_merge = df.copy()
        df_merge = df_merge.dropna().sort_values(by="Time")
        df = pd.merge_asof(left=df.reset_index(), right=df_merge.reset_index(), left_on=['Time'], right_on=['Time'],by='log_hash',direction="backward", allow_exact_matches=True, tolerance=pd.Timedelta('2s'), suffixes=('_not_use', '')) 
        df = df[["log_hash", "Time", param_alias_name]]
        if "data" in param_dict and param_dict["data"] == True:
            df = df.fillna(0)
        df_list.append(df)

    return df_list


def get_table_df_by_time(dbcon, time_before, param_list_dict, gc):
    first_table = None
    not_null_first_col = True
    parameter_to_columns_list = [("Time", ["time"],)]
    for key in param_list_dict:
        where = None
        param_dict = param_list_dict[key]
        param_name = param_dict["name"]
        param_alias_name = param_name
        table_name = preprocess_azm.get_table_for_column(param_name.split("/")[0])
        if "selected_ue" in param_dict:
            if param_dict["selected_ue"] is not None:
                selected_logs = gc.device_configs[param_dict["selected_ue"]]["log_hash"]
                where = "and log_hash in ({})".format(','.join([str(selected_log) for selected_log in selected_logs]))
                title_ue_suffix = gc.device_configs[param_dict["selected_ue"]]["name"]
                if title_ue_suffix not in param_alias_name:
                    param_alias_name = param_alias_name + "(" + title_ue_suffix + ")"
        if first_table is None:
            first_table = table_name
        parameter_to_columns = (param_alias_name, [param_name], table_name, where)
        parameter_to_columns_list.append(parameter_to_columns)

    return params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        default_table=first_table,
        not_null_first_col=not_null_first_col,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )
