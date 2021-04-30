import pandas as pd

import params_disp_df


################################## df get functions


def get_wcdma_acive_monitored_df(dbcon, time_before):
    df_list = []

    cell_col_prefix_renamed = [
        #"Cell ID",
        #"Cell Name",
        "UARFCN",
        "PSC",
        "Ec/Io",
        "RSCP ",

    ]

    aset_col_prefix_sr = pd.Series(
        [
            #"wcdma_aset_cellfile_matched_cellid_",
            #"wcdma_aset_cellfile_matched_cellname_",
            "wcdma_aset_cellfreq_",
            "wcdma_aset_sc_",
            "wcdma_aset_ecio_",
            "wcdma_aset_rscp_",
        ]
    )
    aset_n_param = 3
    aset = sum(
        map(
            lambda y: list(map(lambda x: x + "{}".format(y + 1), aset_col_prefix_sr)),
            range(aset_n_param),
        ),
        [],
    )
    parameter_to_columns_list = [
        ("Time", ["time"]),
        (
            list(map(lambda x: "Aset{}".format(x + 1), range(aset_n_param))),
            aset,
            # list(map(lambda x: "wcdma_aset_cellfile_matched_cellid_{}".format(x+1), range(aset_n_param))) +
            # list(map(lambda x: "wcdma_aset_cellfile_matched_cellname_{}".format(x+1), range(aset_n_param))) +
            # list(map(lambda x: "wcdma_aset_sc_{}".format(x+1), range(aset_n_param))) +
            # list(map(lambda x: "wcdma_aset_ecio_{}".format(x+1), range(aset_n_param))) +
            # list(map(lambda x: "wcdma_aset_rscp_{}".format(x+1), range(aset_n_param))) +
            # list(map(lambda x: "wcdma_aset_cellfreq_{}".format(x+1), range(aset_n_param))),
            "wcdma_cell_meas",
        ),
    ]
    df = params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        default_table="wcdma_cell_meas",
        not_null_first_col=False,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )
    # print("df.head():\n%s" % df.head())
    df.columns = ["CellGroup"] + cell_col_prefix_renamed
    # print("df.head():\n%s" % df.head())
    df_list.append(df)

    mset_col_prefix_sr = pd.Series(
        [
            #"wcdma_mset_cellfile_matched_cellid_",
            #"wcdma_mset_cellfile_matched_cellname_",
            "wcdma_mset_cellfreq_",
            "wcdma_mset_sc_",
            "wcdma_mset_ecio_",
            "wcdma_mset_rscp_",

        ]
    )
    mset_n_param = 6
    mset = sum(
        map(
            lambda y: list(map(lambda x: x + "{}".format(y + 1), mset_col_prefix_sr)),
            range(mset_n_param),
        ),
        [],
    )
    parameter_to_columns_list = [
        (
            list(map(lambda x: "Mset{}".format(x + 1), range(mset_n_param))),
            mset,
            "wcdma_cell_meas",
        ),
    ]
    df = params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        default_table="wcdma_cell_meas",
        not_null_first_col=False,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )
    df.columns = ["CellGroup"] + cell_col_prefix_renamed
    df_list.append(df)

    dset_col_prefix_sr = pd.Series(
        [
            #"wcdma_dset_cellfile_matched_cellid_",
            #"wcdma_dset_cellfile_matched_cellname_",
            "wcdma_dset_cellfreq_",
            "wcdma_dset_sc_",
            "wcdma_dset_ecio_",
            "wcdma_dset_rscp_",
        ]
    )
    dset_n_param = 4
    dset = sum(
        map(
            lambda y: list(map(lambda x: x + "{}".format(y + 1), dset_col_prefix_sr)),
            range(dset_n_param),
        ),
        [],
    )
    parameter_to_columns_list = [
        (
            list(map(lambda x: "Dset{}".format(x + 1), range(dset_n_param))),
            dset,
            "wcdma_cell_meas",
        ),
    ]
    df = params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        default_table="wcdma_cell_meas",
        not_null_first_col=False,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )
    df.columns = ["CellGroup"] + cell_col_prefix_renamed
    df_list.append(df)

    final_df = pd.concat(df_list, sort=False)
    return final_df


def get_wcdma_radio_params_disp_df(dbcon, time_before):
    parameter_to_columns_list = [
        (
            ["Time", "Tx Power", "Max Tx Power"],
            ["time", "wcdma_txagc", "wcdma_maxtxpwr",],
            "wcdma_tx_power",
        ),
        ("RSSI", ["wcdma_rssi"], "wcdma_rx_power"),
        ("SIR", ["wcdma_sir"], "wcdma_sir"),
        ("RRC State", ["wcdma_rrc_state"], "wcdma_rrc_state"),
        (
            ["Speech Codec TX", "Speech Codec RX"],
            ["gsm_speechcodectx", "gsm_speechcodecrx"],
            "vocoder_info",
        ),
        (
            ["Cell ID", "RNC ID"],
            ["android_cellid", "android_rnc_id"],
            "android_info_1sec",
        ),
    ]
    return params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        not_null_first_col=True,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )


def get_bler_sum_disp_df(dbcon, time_before):
    parameter_to_columns_list = [
        (
            [
                "Time",
                "BLER Average Percent",
                "BLER Calculation Window Size",
                "BLER N Transport Channels",
            ],
            [
                "time," "wcdma_bler_average_percent_all_channels",
                "wcdma_bler_calculation_window_size",
                "wcdma_bler_n_transport_channels",
            ],
            "wcdma_bler",
        ),
    ]
    return params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        not_null_first_col=False,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )


def get_wcdma_bler_transport_channel_df(dbcon, time_before):
    df_list = []

    cell_col_prefix_renamed = ["Transport Channel", "Percent", "Err", "Rcvd"]

    cell_col_prefix_sr = pd.Series(
        [
            "wcdma_bler_channel_",
            "wcdma_bler_percent_",
            "wcdma_bler_err_",
            "wcdma_bler_rcvd_",
        ]
    )
    n_param = 16
    bler = sum(
        map(
            lambda y: list(map(lambda x: x + "{}".format(y + 1), cell_col_prefix_sr)),
            range(n_param),
        ),
        [],
    )
    parameter_to_columns_list = [
        (list(map(lambda x: "{}".format(x + 1), range(n_param))), bler, "wcdma_bler"),
    ]
    df = params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        default_table="wcdma_bler",
        not_null_first_col=False,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )
    # print("df.head():\n%s" % df.head())
    df.columns = ["Channel"] + cell_col_prefix_renamed
    # print("df.head():\n%s" % df.head())
    df_list.append(df)

    final_df = pd.concat(df_list, sort=False)
    return final_df


def get_wcdma_bearers_df(dbcon, time_before):
    df_list = []

    cell_col_prefix_renamed = ["Bearers ID", "Bearers Rate DL", "Bearers Rate UL"]

    cell_col_prefix_sr = pd.Series(
        [
            "data_wcdma_bearer_id_",
            "data_wcdma_bearer_rate_dl_",
            "data_wcdma_bearer_rate_ul_",
        ]
    )
    n_param = 10
    bearer = sum(
        map(
            lambda y: list(map(lambda x: x + "{}".format(y + 1), cell_col_prefix_sr)),
            range(n_param),
        ),
        [],
    )
    parameter_to_columns_list = [
        (
            list(map(lambda x: " {}".format(x + 1), range(n_param))),
            bearer,
            "wcdma_bearers",
        ),
    ]
    df = params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        default_table="wcdma_bearers",
        not_null_first_col=False,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )
    # print("df.head():\n%s" % df.head())
    df.columns = ["Bearer"] + cell_col_prefix_renamed
    # print("df.head():\n%s" % df.head())
    df_list.append(df)

    final_df = pd.concat(df_list, sort=False)
    return final_df
