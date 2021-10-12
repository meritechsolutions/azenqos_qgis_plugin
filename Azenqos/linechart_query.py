import numpy as np
import pandas as pd

import params_disp_df
import preprocess_azm


def get_nr_df(dbcon):
    df_list = []
    sql_list = [
        "SELECT log_hash, time as Time, nr_servingbeam_ss_rsrp_1 as RSRP, nr_servingbeam_ss_rsrq_1 as RSRQ, nr_servingbeam_ss_sinr_1 as SINR FROM nr_cell_meas where RSRP is not null",
    ]
    for sql in sql_list:
        df = pd.read_sql(sql, dbcon, parse_dates=["Time"])
        df["log_hash"] = df["log_hash"].astype(np.int64)
        df_list.append(df)

    return df_list


def get_nr_df_by_time(dbcon, time_before):
    parameter_to_columns_list = [
        ("Time", ["time"],),
        (
            ["RSRP", "RSRQ", "SINR"],
            [
                "nr_servingbeam_ss_rsrp_1",
                "nr_servingbeam_ss_rsrq_1",
                "nr_servingbeam_ss_sinr_1",
            ],
        ),
    ]
    return params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        default_table="nr_cell_meas",
        not_null_first_col=True,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )


def get_nr_data_df(dbcon):
    df_list = []
    sql_list = [
        "SELECT log_hash, time as Time, data_download_overall/1000 as 'Data Download', data_upload_overall/1000 as'Data Upload' FROM data_app_throughput",
        "SELECT log_hash, time as Time, (IFNULL(nr_p_plus_scell_nr_pdsch_tput_mbps,0) + IFNULL(nr_p_plus_scell_lte_dl_pdcp_tput_mbps,0)) as 'NR LTE DL', (IFNULL(nr_p_plus_scell_nr_pusch_tput_mbps,0) + IFNULL(nr_p_plus_scell_lte_ul_pdcp_tput_mbps,0)) as 'NR LTE UL', nr_p_plus_scell_nr_pdsch_tput_mbps as 'NR DL', nr_p_plus_scell_nr_pusch_tput_mbps as 'NR UL', nr_p_plus_scell_lte_dl_pdcp_tput_mbps as 'LTE DL', nr_p_plus_scell_lte_ul_pdcp_tput_mbps as 'LTE UL' FROM nr_cell_meas",
    ]
    for sql in sql_list:
        df = pd.read_sql(sql, dbcon, parse_dates=["Time"])
        df["log_hash"] = df["log_hash"].astype(np.int64)
        df = df.fillna(0)
        df_list.append(df)
    return df_list


def get_nr_data_df_by_time(dbcon, time_before):
    parameter_to_columns_list = [
        ("Time", ["time"],),
        (
            ["Data Download", "Data Upload",],
            ["data_download_overall/1000", "data_upload_overall/1000",],
            "data_app_throughput",
        ),
        (
            ["NR LTE DL", "NR LTE UL", "NR DL", "NR UL", "LTE DL", "LTE UL"],
            [
                "(IFNULL(nr_p_plus_scell_nr_pdsch_tput_mbps,0) + IFNULL(nr_p_plus_scell_lte_dl_pdcp_tput_mbps,0))",
                "(IFNULL(nr_p_plus_scell_nr_pusch_tput_mbps,0) + IFNULL(nr_p_plus_scell_lte_ul_pdcp_tput_mbps,0))",
                "nr_p_plus_scell_nr_pdsch_tput_mbps",
                "nr_p_plus_scell_nr_pusch_tput_mbps",
                "nr_p_plus_scell_lte_dl_pdcp_tput_mbps",
                "nr_p_plus_scell_lte_ul_pdcp_tput_mbps",
            ],
            "nr_cell_meas",
        ),
    ]
    return params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        default_table="data_app_throughput",
        not_null_first_col=True,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )


############# Line Chart LTE


def get_lte_df(dbcon):
    SQL = "SELECT log_hash, time as Time, lte_sinr_1  as 'SINR', lte_inst_rsrp_1 as RSRP, lte_inst_rsrq_1 as RSRQ, lte_inst_rssi_1 AS RSSI FROM lte_cell_meas order by time"
    df = pd.read_sql(SQL, dbcon, parse_dates=["Time"])
    df["log_hash"] = df["log_hash"].astype(np.int64)
    return df


def get_lte_df_by_time(dbcon, time_before):
    parameter_to_columns_list = [
        (
            ["Time", "SINR", "RSRP", "RSRQ", "RSSI",],
            [
                "time",
                "lte_sinr_1 ",
                "lte_inst_rsrp_1",
                "lte_inst_rsrq_1",
                "lte_inst_rssi_1",
            ],
        ),
    ]
    return params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        default_table="lte_cell_meas",
        not_null_first_col=True,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )


def get_lte_data_df(dbcon):
    df_list = []
    sql_list = [
        "SELECT log_hash, time as Time, data_download_overall/1000 as 'Data Download', data_upload_overall/1000 as'Data Upload' FROM data_app_throughput order by time",
        "SELECT log_hash, time as Time, lte_l1_throughput_mbps_1 as 'L1 Throughput', lte_bler_1 as'LTE Bler' FROM lte_l1_dl_tp order by time",
    ]
    for sql in sql_list:
        df = pd.read_sql(sql, dbcon, parse_dates=["Time"])
        df["log_hash"] = df["log_hash"].astype(np.int64)
        df = df.fillna(0)
        df_list.append(df)
    return df_list


def get_lte_data_df_by_time(dbcon, time_before):
    parameter_to_columns_list = [
        ("Time", ["time"],),
        (
            ["Data Download", "Data Upload",],
            ["data_download_overall/1000", "data_upload_overall/1000",],
            "data_app_throughput",
        ),
        (
            ["L1 Throughput", "LTE Bler",],
            ["lte_l1_throughput_mbps_1", "lte_bler_1",],
            "lte_l1_dl_tp",
        ),
    ]
    return params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        default_table="data_app_throughput",
        not_null_first_col=True,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )


############# Line Chart WCDMA


def get_wcdma_df(dbcon):
    df_list = []
    sql_list = [
        "SELECT log_hash, time as Time, wcdma_aset_ecio_avg as EcIo, wcdma_aset_rscp_avg as RSCP FROM wcdma_cell_meas",
        "SELECT log_hash, time as Time, wcdma_rssi as RSSI FROM wcdma_rx_power",
        "SELECT log_hash, time as Time, wcdma_bler_average_percent_all_channels as Bler FROM wcdma_bler",
    ]
    for sql in sql_list:
        df = pd.read_sql(sql, dbcon, parse_dates=["Time"])
        df["log_hash"] = df["log_hash"].astype(np.int64)
        df_list.append(df)

    return df_list


def get_wcdma_df_by_time(dbcon, time_before):
    parameter_to_columns_list = [
        ("Time", ["time"],),
        (
            ["EcIo", "RSCP",],
            ["wcdma_aset_ecio_avg", "wcdma_aset_rscp_avg",],
            "wcdma_cell_meas",
        ),
        (["RSSI",], ["wcdma_rssi",], "wcdma_rx_power",),
        (["Bler",], ["wcdma_bler_average_percent_all_channels",], "wcdma_bler",),
    ]
    return params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        default_table="wcdma_cell_meas",
        not_null_first_col=True,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )


def get_wcdma_data_df(dbcon):
    df_list = []
    sql_list = [
        "SELECT log_hash, time as Time, data_wcdma_rlc_dl_throughput as 'RLC Download Thoughput' FROM data_wcdma_rlc_stats",
        "SELECT log_hash, time as Time, data_app_dl_throughput_1 as 'App Download Thoughput' FROM data_app_throughput",
        "SELECT log_hash, time as Time, data_hsdpa_thoughput as 'HSDPA Thoughput' FROM wcdma_hsdpa_stats",
    ]
    for sql in sql_list:
        df = pd.read_sql(sql, dbcon, parse_dates=["Time"])
        df["log_hash"] = df["log_hash"].astype(np.int64)
        df = df.fillna(0)
        df_list.append(df)
    return df_list


def get_wcdma_data_df_by_time(dbcon, time_before):
    parameter_to_columns_list = [
        ("Time", ["time"],),
        (
            ["RLC Download Thoughput"],
            ["data_wcdma_rlc_dl_throughput",],
            "data_wcdma_rlc_stats",
        ),
        (
            ["App Download Thoughput",],
            ["data_app_dl_throughput_1",],
            "data_app_throughput",
        ),
        (["HSDPA Thoughput",], ["data_hsdpa_thoughput",], "wcdma_hsdpa_stats",),
    ]
    return params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        default_table="data_wcdma_rlc_stats",
        not_null_first_col=True,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )


############ Line Chart GSM


def get_gsm_df(dbcon):
    df_list = []
    sql_list = [
        "SELECT log_hash, time as Time, gsm_rxlev_sub_dbm as RxLev, gsm_rxqual_sub as RxQual FROM gsm_cell_meas"
    ]
    for sql in sql_list:
        df = pd.read_sql(sql, dbcon, parse_dates=["Time"])
        df["log_hash"] = df["log_hash"].astype(np.int64)
        df_list.append(df)

    return df_list


def get_gsm_df_by_time(dbcon, time_before):
    parameter_to_columns_list = [
        (
            ["Time", "RxLev", "RxQual",],
            ["time", "gsm_rxlev_sub_dbm", "gsm_rxqual_sub",],
        ),
    ]
    return params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        default_table="gsm_cell_meas",
        not_null_first_col=True,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )


def get_gsm_data_df(dbcon):
    df_list = []
    sql_list = [
        "SELECT log_hash, time as Time, data_gsm_rlc_dl_throughput as 'RLC Download Thoughput' FROM data_egprs_stats",
        "SELECT log_hash, time as Time, data_app_dl_throughput_1 as 'App Download Thoughput' FROM data_app_throughput",
    ]
    for sql in sql_list:
        df = pd.read_sql(sql, dbcon, parse_dates=["Time"])
        df["log_hash"] = df["log_hash"].astype(np.int64)
        df = df.fillna(0)
        df_list.append(df)
    return df_list


def get_gsm_data_df_by_time(dbcon, time_before):
    parameter_to_columns_list = [
        ("Time", ["time"],),
        (
            ["RLC Download Thoughput"],
            ["data_gsm_rlc_dl_throughput",],
            "data_egprs_stats",
        ),
        (
            ["App Download Thoughput",],
            ["data_app_dl_throughput_1",],
            "data_app_throughput",
        ),
    ]
    return params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        default_table="data_egprs_stats",
        not_null_first_col=True,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )


############ New Line Chart Query


def get_chart_df(dbcon, param_list_dict):
    df_list = []
    print(param_list_dict)
    for key in param_list_dict:
        param_dict = param_list_dict[key]
        param_name = param_dict["name"]
        table_name = preprocess_azm.get_table_for_column(param_name.split("/")[0])
        sql = "SELECT log_hash, time as Time, {} FROM {}".format(param_name, table_name)
        df = pd.read_sql(sql, dbcon, parse_dates=["Time"])
        df["log_hash"] = df["log_hash"].astype(np.int64)
        df = df.sort_values(by="Time")
        df_merge = df.copy()
        df_merge = df_merge.dropna().sort_values(by="Time")
        df = pd.merge_asof(left=df.reset_index(), right=df_merge.reset_index(), left_on=['Time'], right_on=['Time'],by='log_hash',direction="backward", allow_exact_matches=True, tolerance=pd.Timedelta('2s'), suffixes=('_not_use', '')) 
        df = df[["log_hash", "Time", param_name]]
        if "data" in param_dict and param_dict["data"] == True:
            df = df.fillna(0)
        df_list.append(df)

    return df_list


def get_table_df_by_time(dbcon, time_before, param_list_dict):
    first_table = None
    not_null_first_col = True
    parameter_to_columns_list = [("Time", ["time"],)]
    for key in param_list_dict:
        param_dict = param_list_dict[key]
        param_name = param_dict["name"]
        table_name = preprocess_azm.get_table_for_column(param_name.split("/")[0])
        if first_table is None:
            first_table = table_name
        parameter_to_columns = (param_name, [param_name], table_name)
        parameter_to_columns_list.append(parameter_to_columns)

    return params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        default_table=first_table,
        not_null_first_col=not_null_first_col,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )
