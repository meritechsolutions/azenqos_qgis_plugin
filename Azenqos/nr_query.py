import pandas as pd

import params_disp_df


################################## df get functions

def get_nr_radio_params_disp_df(dbcon, time_before):
    #n_param_args = 4
    parameter_to_columns_list = [
        (
            [
                "---- PCell ----",
                "NR DL FREQ",
                "NR ARFCN",
                "NR Band",
                "NR PCI",
                "NR SSB Index",
                "NR SS RSRP",
                "NR SS RSRQ",
                "NR SS SINR",
                "NR N Rx Ant",
                "NR N Tx Ant",
                "NR SubCarrier Size",
                "NR DL RB",
                "NR DL Bandwidth",
                "NR UL RB",
                "NR UL Bandwidth",
                "NR Num Layers",
                "   ",
                "NR DL TxMode",
                "NR UL TxMode",
            ],
            [
                '"" as unused1',
                "nr_dl_frequency_1",
                "nr_dl_arfcn_1",
                "nr_band_1",
                "nr_servingbeam_pci_1",
                "nr_servingbeam_ssb_index_1",
                "nr_servingbeam_ss_rsrp_1",
                "nr_servingbeam_ss_rsrq_1",
                "nr_servingbeam_ss_sinr_1",
                "nr_num_rx_ant_1",
                "nr_num_tx_ant_1",
                "nr_numerology_scs_1",
                "nr_dl_rb_1",
                "nr_bw_1",
                "nr_ul_rb_1",
                "nr_ul_bw_1",
                "nr_numlayers_1",
                '"" as unused2',
                "nr_pdsch_tx_mode_1",
                "nr_ul_tx_mode_1",
            ],
            "nr_cell_meas",
        ),
        (
            [
                "NR ENDC Total Tx Power"
            ],
            [
                "nr_endc_total_tx_power"
            ],
            "nr_deb_stat"
        ),
        (
            [
                "---- PUSCH ----",
                "NR PUSCH Tx Power",
                "NR PUSCH MTPL",
                "NR PUSCH DL Ploss",
                "NR PUSCH f(i)",
            ],
            [
                '"" as unused3',
                "nr_pusch_tx_power_1",
                "nr_pusch_mtpl_1",
                "nr_pusch_dl_pathloss_1",
                "nr_pusch_f_i_1",
            ],
            "nr_cell_meas"
        ),
        (
            [
                "---- PUSCH ----",
                "NR PUCCH Tx Power",
                "NR PUCCH MTPL",
                "NR PUCCH DL PLoss",
                "NR PUCCH g(i)",
            ],
            [
                '"" as unused4',
                "nr_pucch_tx_power_1",
                "nr_pucch_mtp_1",
                "nr_pucch_dl_pathlos_1",
                "nr_pucch_g_i_1",
            ],
            "nr_cell_meas"
        ),
        (
            [
                "---- SRS ----",
                "NR SRX Tx Power",
                "NR SRX MTPL",
                "NR SRX DL PLoss",
                "NR SRX PC Adj State",
            ],
            [
                '"" as unused5',
                "nr_srs_tx_power_1",
                "nr_srs_mtpl_1",
                "nr_srs_dl_pathloss_1",
                "nr_srs_pc_adj_state_1",
            ],
            "nr_cell_meas"
        ),
        (
            [
                "---- RACH ----",
                "NR PRACH Tx Power",
            ],
            [
                '"" as unused6',
                "nr_prach_tx_power",
            ],
            "nr_deb_stat"
        ),
        (
            [
                "RACH PLoss",
                "RACH Reason",
                "RACH CRNTI",
                "RACH CNType",
                "RACH AttNum",
                "RACH Result",
                "RACH N Success",
                "RACH N Fail",
                "RACH N Abort",
                "RACH N OthRslt",
                "RACH N 1stAttScss",
                "RACH N MltAttScss",
                "RACH N FailMsg2",
                "RACH N FailMsg4",
            ],
            [
                "nr_p_plus_scell_nr_rach_pathloss",
                "nr_p_plus_scell_nr_rach_reason",
                "nr_p_plus_scell_nr_rach_crnti",
                "nr_p_plus_scell_nr_rach_contention_type",
                "nr_p_plus_scell_nr_rach_attempt_number",
                "nr_p_plus_scell_nr_rach_result",
                "nr_p_plus_scell_nr_rach_num_success",
                "nr_p_plus_scell_nr_rach_num_fail",
                "nr_p_plus_scell_nr_rach_num_abort",
                "nr_p_plus_scell_nr_rach_num_other_result",
                "nr_p_plus_scell_nr_rach_num_first_attempt_success",
                "nr_p_plus_scell_nr_rach_num_multiple_attempt_success",
                "nr_p_plus_scell_nr_rach_num_fail_msg2",
                "nr_p_plus_scell_nr_rach_num_fail_msg4",
            ],
            "nr_cell_meas"
        ),
        (
            [
                "---- ReconfigWithSync params ----",
                "target_arfcn",
                "offset_to_carrier",
                "carrier_bandwidth_rbs",
                "carrier_bandwidth_mhz",
            ],
            [
                '"" as unused6',
                "nr_reconfigwithsync_target_arfcn",
                "nr_reconfigwithsync_carrier_offset_to_carrier_1",
                "nr_reconfigwithsync_carrier_bandwidth_rbs_1",
                "nr_reconfigwithsync_carrier_bandwidth_mhz_1",
            ],
            "nr_reconfigwithsync_params"
        ),
    ]
    return params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        not_null_first_col=False,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )


# def get_nr_radio_params_disp_df(dbcon, time_before):
#     n_param_args = 8
#     parameter_to_columns_list = [
#         ("Time", ["time"]),
#         (  # these params below come together so query them all in one query
#             [
#                 "Beam ID",
#                 "Band",
#                 "Band Type",
#                 "ARFCN",
#                 "Frequency",
#                 "PCI",
#                 "RSRP",
#                 "RSRQ",
#                 "SINR",
#                 "Bandwidth",
#                 "SSB SCS",
#                 "Numerology SCS",
#             ],
#             list(
#                 map(
#                     lambda x: "nr_servingbeam_ssb_index_{}".format(x + 1),
#                     range(n_param_args),
#                 )
#             )
#             + list(map(lambda x: "nr_band_{}".format(x + 1), range(n_param_args)))
#             + list(map(lambda x: "nr_band_type_{}".format(x + 1), range(n_param_args)))
#             + list(map(lambda x: "nr_dl_arfcn_{}".format(x + 1), range(n_param_args)))
#             + list(
#                 map(lambda x: "nr_dl_frequency_{}".format(x + 1), range(n_param_args))
#             )
#             + list(
#                 map(
#                     lambda x: "nr_servingbeam_pci_{}".format(x + 1), range(n_param_args)
#                 )
#             )
#             + list(
#                 map(
#                     lambda x: "nr_servingbeam_ss_rsrp_{}".format(x + 1),
#                     range(n_param_args),
#                 )
#             )
#             + list(
#                 map(
#                     lambda x: "nr_servingbeam_ss_rsrq_{}".format(x + 1),
#                     range(n_param_args),
#                 )
#             )
#             + list(
#                 map(
#                     lambda x: "nr_servingbeam_ss_sinr_{}".format(x + 1),
#                     range(n_param_args),
#                 )
#             )
#             + list(map(lambda x: "nr_bw_{}".format(x + 1), range(n_param_args)))
#             + list(map(lambda x: "nr_ssb_scs_{}".format(x + 1), range(n_param_args)))
#             + list(
#                 map(lambda x: "nr_numerology_scs_{}".format(x + 1), range(n_param_args))
#             ),
#         ),
#         (  # these params below come together but not same row with rsrp etc above so query them all in their own set below
#             ["PUSCH TxPower", "PUCCH TxPower", "SRS TxPower"],
#             list(
#                 map(lambda x: "nr_pusch_tx_power_{}".format(x + 1), range(n_param_args))
#             )
#             + list(
#                 map(lambda x: "nr_pucch_tx_power_{}".format(x + 1), range(n_param_args))
#             )
#             + list(
#                 map(lambda x: "nr_srs_tx_power_{}".format(x + 1), range(n_param_args))
#             ),
#         ),
#     ]
#     return params_disp_df.get(
#         dbcon,
#         parameter_to_columns_list,
#         time_before,
#         default_table="nr_cell_meas",
#         custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
#     )


def get_nr_serv_and_neigh_disp_df(dbcon, time_before):
    df_list = []

    pcell_scell_col_prefix_sr = pd.Series(
        [
            "nr_dl_arfcn_",
            "nr_servingbeam_pci_",
            "nr_servingbeam_ss_rsrp_",
            "nr_servingbeam_ss_rsrq_",
            "nr_servingbeam_ss_sinr_",
        ]
    )
    pcell_scell_col_prefix_renamed = ["ARFCN", "PCI", "RSRP", "RSRQ", "SINR"]
    parameter_to_columns_list = [
        ("Time", ["time"]),
        (
            [
                "PCell",
                "SCell1",
                "SCell2",
                "SCell3",
                "SCell4",
                "SCell5",
                "SCell6",
                "SCell7",
            ],
            list(pcell_scell_col_prefix_sr + "1")
            + list(pcell_scell_col_prefix_sr + "2")
            + list(pcell_scell_col_prefix_sr + "3")
            + list(pcell_scell_col_prefix_sr + "4")
            + list(pcell_scell_col_prefix_sr + "5")
            + list(pcell_scell_col_prefix_sr + "6")
            + list(pcell_scell_col_prefix_sr + "7")
            + list(pcell_scell_col_prefix_sr + "8"),
        ),
    ]
    df = params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        default_table="nr_cell_meas",
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )
    # print("df.head():\n%s" % df.head())
    df.columns = ["CellGroup"] + pcell_scell_col_prefix_renamed
    # print("df.head():\n%s" % df.head())
    df_list.append(df)

    dcell_col_suffix_sr = pd.Series(
        ["_pci_1", "_ss_rsrp_1", "_ss_rsrq_1", "_ss_sinr_1"]
    )  # a mistake during elm sheets made this unnecessary _1 required
    dcell_col_renamed = ["PCI", "RSRP", "RSRQ", "SINR"]
    dparameter_to_columns_list = [
        (
            ["DCell1", "DCell2", "DCell3", "DCell4"],
            list("nr_detectedbeam1" + dcell_col_suffix_sr)
            + list("nr_detectedbeam2" + dcell_col_suffix_sr)
            + list("nr_detectedbeam3" + dcell_col_suffix_sr)
            + list("nr_detectedbeam4" + dcell_col_suffix_sr),
        )
    ]
    dcell_df = params_disp_df.get(
        dbcon,
        dparameter_to_columns_list,
        time_before,
        default_table="nr_cell_meas",
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )
    # print("0dcell_df.head():\n%s" % dcell_df.head())
    dcell_df.columns = ["CellGroup"] + dcell_col_renamed
    # print("dcell_df.head():\n%s" % dcell_df.head())
    df_list.append(dcell_df)

    final_df = pd.concat(df_list, sort=False)
    return final_df
