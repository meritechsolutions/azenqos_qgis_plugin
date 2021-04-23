import pandas as pd
import params_disp_df


################################## df get functions


def get_gsm_radio_params_disp_df(dbcon, time_before):
    df_list = []
    parameter_to_columns_list = [
        (
            [
                "Time",
                "RxLev Full",
                "RxLev Sub",
                "RxQual Full",
                "RxQual Sub",
            ],
            [
                "time," "gsm_rxlev_full_dbm",
                "gsm_rxlev_sub_dbm",
                "gsm_rxqual_full",
                "gsm_rxqual_sub",
            ],
            "gsm_cell_meas",
        ),
        ("TA", ["gsm_ta"], "gsm_tx_meas"),
        ("RLT (Max)", ["gsm_radiolinktimeout_max"], "gsm_rl_timeout_counter"),
        ("RLT (Current)", ["gsm_radiolinktimeout_current"], "gsm_rlt_counter"),
        ("DTX Used", ["gsm_dtxused"], "gsm_rr_measrep_params"),
        ("TxPower", ["gsm_txpower"], "gsm_tx_meas"),
        ("FER", ["gsm_fer"], "vocoder_info"),
    ]
    df = params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        not_null_first_col=False,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )
    df.columns = ["Parameter", "Value"]
    df_list.append(df)

    final_df = pd.concat(df_list, sort=False)
    return final_df


def get_gsm_serv_and_neigh__df(dbcon, time_before):
    df_list = []

    cell_col_prefix_renamed = [
        "Cell Name",
        "BSIC",
        "ARFCN ",
        "RxLev",
        "C1",
        "C2",
        "C31",
        "C32",
    ]
    serv_col_prefix_sr = pd.Series(
        [
            "gsm_cellfile_matched_cellname",
            "gsm_bsic",
            "gsm_arfcn_bcch",
            "gsm_rxlev_sub_dbm",
            "gsm_c1",
            "gsm_c2",
            "gsm_c31",
            "gsm_c32",
        ]
    )
    parameter_to_columns_list = [
        (
            "serv",
            list(serv_col_prefix_sr),
        ),
    ]
    df = params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        default_table="gsm_cell_meas",
        not_null_first_col=False,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )
    df.columns = ["CellGroup"] + cell_col_prefix_renamed
    df_list.append(df)

    lac_col_prefix_sr = pd.Series(
        [
            "gsm_lac",
        ]
    )
    parameter_to_columns_list = [
        (
            "serv",
            list(lac_col_prefix_sr),
        ),
    ]
    df2 = params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        default_table="gsm_serv_cell_info",
        not_null_first_col=False,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )
    df2.columns = ["CellGroup", "LAC"]
    df.insert(2, "LAC", df2["LAC"])

    neigh_col_prefix_sr = pd.Series(
        [
            "gsm_cellfile_matched_neighbor_cellname",
            "gsm_cellfile_matched_neighbor_lac_",
            "gsm_neighbor_bsic_",
            "gsm_neighbor_arfcn_",
            "gsm_neighbor_rxlev_dbm_",
            "gsm_neighbor_c1_",
            "gsm_neighbor_c2_",
            "gsm_neighbor_c31_",
            "gsm_neighbor_c32_",
        ]
    )
    neigh_n_param = 32

    def name_map(x, y):
        if x == "gsm_cellfile_matched_neighbor_cellname":
            if y == 0:
                return "gsm_cellfile_matched_neighbor_cellname"
            else:
                return '"" as unsed_{}'.format(y + 1)
        return x + "{}".format(y + 1)

    neigh = sum(
        map(
            lambda y: list(map(lambda x: name_map(x, y), neigh_col_prefix_sr)),
            range(neigh_n_param),
        ),
        [],
    )
    parameter_to_columns_list = [
        (
            list(map(lambda x: "neigh{}".format(x + 1), range(neigh_n_param))),
            neigh,
        ),
    ]
    df = params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        default_table="gsm_cell_meas",
        not_null_first_col=False,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )
    df.columns = [
        "CellGroup",
        "Cell Name",
        "LAC",
        "BSIC",
        "ARFCN ",
        "RxLev",
        "C1",
        "C2",
        "C31",
        "C32",
    ]
    df_list.append(df)

    final_df = pd.concat(df_list, sort=False)
    return final_df


def get_gsm_current_channel_disp_df(dbcon, time_before):
    df_list = []
    parameter_to_columns_list = [
        (
            [
                "Time",
                "Cellname",
                "CGI",
            ],
            [
                "time," "gsm_cellfile_matched_cellname",
                "gsm_cgi",
            ],
            "gsm_cell_meas",
        ),
        ("Channel Type", ["gsm_channeltype"], "gsm_rr_chan_desc"),
        ("Sub Channel Number", ["gsm_subchannelnumber"], "gsm_rr_subchan"),
        (
            ["Mobile Allocation Index Offset (MAIO)", "Hopping Sequence Number (HSN)"],
            ["gsm_maio", "gsm_hsn"],
            "gsm_rr_chan_desc",
        ),
        ("Cipering Algorithm", ["gsm_cipheringalgorithm"], "gsm_rr_cipher_alg"),
        ("MS Power Control Level", ["gsm_ms_powercontrollevel"], "gsm_rr_power_ctrl"),
        ("Channel Mode", ["gsm_channelmode"], "gsm_chan_mode"),
        (
            ["Speech Codec TX", "Speech Codec RX"],
            ["gsm_speechcodectx", "gsm_speechcodecrx"],
            "vocoder_info",
        ),
        ("Hopping Frequencies", ["gsm_hoppingfrequencies"], "gsm_hopping_list"),
        ("ARFCN BCCH", ["gsm_arfcn_bcch"], "gsm_cell_meas"),
        ("ARFCN TCH", ["gsm_arfcn_tch"], "gsm_rr_chan_desc"),
        ("Time Slot", ["gsm_timeslot"], "gsm_rr_chan_desc"),
    ]
    df = params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        not_null_first_col=False,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )
    df.columns = ["Parameter", "Value"]
    df_list.append(df)

    final_df = pd.concat(df_list, sort=False)
    return final_df


def get_coi_df(dbcon, time_before):
    df_list = []

    cell_col_prefix_renamed = ["ARFCN", "VALUE"]
    worst_col_prefix_sr = pd.Series(["gsm_coi_worst_arfcn_1", "gsm_coi_worst"])
    parameter_to_columns_list = [
        ("Time", ["time"]),
        (
            "Worst",
            list(worst_col_prefix_sr),
        ),
    ]
    df = params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        default_table="gsm_coi_per_chan",
        not_null_first_col=True,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )
    df.columns = ["CellGroup"] + cell_col_prefix_renamed
    df_list.append(df)

    avg_col_prefix_sr = pd.Series(["gsm_coi_arfcn_", "gsm_coi_"])
    avg_n_param = 32

    avg = sum(
        map(
            lambda y: list(map(lambda x: x + "{}".format(y + 1), avg_col_prefix_sr)),
            range(avg_n_param),
        ),
        [],
    )
    parameter_to_columns_list = [
        ("Avg", ['""']),
        (
            list(map(lambda x: "", range(avg_n_param))),
            avg,
        ),
    ]
    df = params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        default_table="gsm_coi_per_chan",
        not_null_first_col=True,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )
    df.columns = ["CellGroup"] + cell_col_prefix_renamed
    df_list.append(df)

    final_df = pd.concat(df_list, sort=False)
    return final_df
