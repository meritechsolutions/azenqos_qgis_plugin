import pandas as pd

import params_disp_df


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
                rat_to_main_param_dict[rat], rat_to_table_and_primary_where_dict[rat]
            )
            df = pd.read_sql(sql, dbcon, parse_dates=["Time"])
            df["rat"] = rat
            if rat == "NR":
                df = df.ffill(limit=5)
            per_rat_df_list.append(df)
        except Exception as e:
            print("WARNING: gen per_rat_df failed:", e)
    df = pd.concat(per_rat_df_list, ignore_index=True)
    df.sort_values(["log_hash", "time", "rat"], inplace=True)
    df = df[~pd.isnull(df.main_param)]
    return df

def get_gsm_wcdma_system_info_df(dbcon, time_before):
    parameter_to_columns_list = [
        ("Time", ["time"], "serving_system"),
        (
            [
                "MCC",
                "MNC",
                "LAC",
                "Service Status",
                "Service Domain",
                "Service Capability",
                "System Mode",
                "Roaming Status",
                "System ID Type",
            ],
            [
                "serving_system_mcc",
                "serving_system_mnc",
                "serving_system_lac",
                "cm_service_status",
                "cm_service_domain",
                "cm_service_capability",
                "cm_system_mode",
                "cm_roaming_status",
                "cm_system_id_type",
            ],
            "serving_system",
        ),
    ]
    return params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        not_null_first_col=False,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )

def get_lte_system_info_df(dbcon, time_before):
    parameter_to_columns_list = [
        ("Time", ["time"], "lte_sib1_info"),
        (
            [
                "MCC",
                "MNC",
                "TAC",
                "ECI",
            ], 
            [
                "lte_sib1_mcc",
                "lte_sib1_mnc",
                "lte_sib1_tac",
                "lte_sib1_eci",
            ],
            "lte_sib1_info"
        ),
        (
            [
                "LAC",
                "Service Status",
                "Service Domain",
                "Service Capability",
                "System Mode",
                "Roaming Status",
                "System ID Type",
            ],
            [
                "serving_system_lac",
                "cm_service_status",
                "cm_service_domain",
                "cm_service_capability",
                "cm_system_mode",
                "cm_roaming_status",
                "cm_system_id_type",
            ],
            "serving_system",
        ),
    ]
    return params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        not_null_first_col=False,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )