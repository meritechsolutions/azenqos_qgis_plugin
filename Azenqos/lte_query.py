import pandas as pd

import params_disp_df


################################## df get functions


def get_lte_rrc_sib_states_df(dbcon, time_before):
    parameter_to_columns_list = [
        (
            [
                "Time",
                "SIB1 MCC",
                "SIB1 MNC",
                "SIB1 TAC",
                "SIB1 ECI (Cell ID)",
                "SIB1 eNodeB ID",
                "SIB1 LCI",
            ],
            [
                "time",
                "lte_sib1_mcc",
                "lte_sib1_mnc",
                "lte_sib1_tac",
                "lte_sib1_eci",
                "lte_sib1_enb_id",
                "lte_sib1_local_cell_id",
            ],
            "lte_sib1_info",
        ),
        (
            ["Time", "Transmission Mode (RRC-tm)"],
            ["time", "lte_transmission_mode_l3",],
            "lte_rrc_transmode_info",
        ),
        (["Time", "RRC State"], ["time", "lte_rrc_state",], "lte_rrc_state",),
    ]
    return params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        not_null_first_col=True,
        custom_lookback_dur_millis=24 * 3600 * 1000,
    )


def get_lte_radio_params_disp_df(dbcon, time_before):
    n_param_args = 4
    parameter_to_columns_list = [
        ("Time", ["time"], "lte_cell_meas"),
        (  # these params below come together so query them all in one query
            ["Band", "EARFCN", "PCI", "RSRP", "RSRQ", "SINR", "RSSI"],
            list(map(lambda x: "lte_band_{}".format(x + 1), range(n_param_args)))
            + list(map(lambda x: "lte_earfcn_{}".format(x + 1), range(n_param_args)))
            + list(
                map(
                    lambda x: "lte_physical_cell_id_{}".format(x + 1),
                    range(n_param_args),
                )
            )
            + list(map(lambda x: "lte_inst_rsrp_{}".format(x + 1), range(n_param_args)))
            + list(map(lambda x: "lte_inst_rsrq_{}".format(x + 1), range(n_param_args)))
            + list(map(lambda x: "lte_sinr_{}".format(x + 1), range(n_param_args)))
            + list(
                map(lambda x: "lte_inst_rssi_{}".format(x + 1), range(n_param_args))
            ),
            "lte_cell_meas",
        ),
        (["TxPower",], ["lte_tx_power",], "lte_tx_power",),
        (["PUSCH TxPower"], ["lte_pusch_tx_power",], "lte_pusch_tx_info",),
        (["PUCCH TxPower"], ["lte_pucch_tx_power",], "lte_pucch_tx_info",),
        (["TA"], ["lte_ta",], "lte_frame_timing",),
    ]
    return params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        not_null_first_col=True,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )


def get_lte_serv_and_neigh_disp_df(dbcon, time_before):
    df_list = []

    pcell_scell_col_prefix_sr = pd.Series(
        [
            "lte_earfcn_",
            "lte_physical_cell_id_",
            "lte_inst_rsrp_",
            "lte_inst_rsrq_",
            "lte_sinr_",
        ]
    )
    pcell_scell_col_prefix_renamed = ["EARFCN", "PCI", "RSRP", "RSRQ", "SINR"]
    parameter_to_columns_list = [
        ("Time", ["time"]),
        (
            ["PCell", "SCell1", "SCell2", "SCell3"],
            list(pcell_scell_col_prefix_sr + "1")
            + list(pcell_scell_col_prefix_sr + "2")
            + list(pcell_scell_col_prefix_sr + "3")
            + list(pcell_scell_col_prefix_sr + "4"),
            "lte_cell_meas",
        ),
    ]
    df = params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        default_table="lte_cell_meas",
        not_null_first_col=True,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )
    # print("df.head():\n%s" % df.head())
    df.columns = ["CellGroup"] + pcell_scell_col_prefix_renamed
    # print("df.head():\n%s" % df.head())
    df_list.append(df)

    # neigh
    pcell_scell_col_prefix_sr = pd.Series(
        [
            "lte_neigh_earfcn_",
            "lte_neigh_physical_cell_id_",
            "lte_neigh_rsrp_",
            "lte_neigh_rsrq_",
        ]
    )
    pcell_scell_col_prefix_renamed = ["ARFCN", "PCI", "RSRP", "RSRQ"]
    parameter_to_columns_list = [
        (
            [
                "Neigh1",
                "Neigh2",
                "Neigh3",
                "Neigh4",
                "Neigh5",
                "Neigh6",
                "Neigh7",
                "Neigh8",
            ],
            list(pcell_scell_col_prefix_sr + "1")
            + list(pcell_scell_col_prefix_sr + "2")
            + list(pcell_scell_col_prefix_sr + "3")
            + list(pcell_scell_col_prefix_sr + "4")
            + list(pcell_scell_col_prefix_sr + "5")
            + list(pcell_scell_col_prefix_sr + "6")
            + list(pcell_scell_col_prefix_sr + "7")
            + list(pcell_scell_col_prefix_sr + "8"),
            "lte_neigh_meas",
        )
    ]
    df = params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        not_null_first_col=True,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )
    # print("df.head():\n%s" % df.head())
    df.columns = ["CellGroup"] + pcell_scell_col_prefix_renamed
    # print("df.head():\n%s" % df.head())
    df_list.append(df)

    final_df = pd.concat(df_list, sort=False)
    return final_df


def get_lte_rlc_disp_df(dbcon, time_before):
    n_param_args = 4
    parameter_to_columns_list = [
        (
            ["Time", "DL TP(Mbps)", "DL TP(Kbps)", "N Bearers"],
            ["time", "lte_rlc_dl_tp_mbps", "lte_rlc_dl_tp", "lte_rlc_n_bearers"],
            "lte_rlc_stats",
        ),
        (  # these params below come together so query them all in one query
            ["Mode", "Type", "RB-ID", "Index", "TP Mbps",],
            list(
                map(
                    lambda x: "lte_rlc_per_rb_dl_rb_mode_{}".format(x + 1),
                    range(n_param_args),
                )
            )
            + list(
                map(
                    lambda x: "lte_rlc_per_rb_dl_rb_type_{}".format(x + 1),
                    range(n_param_args),
                )
            )
            + list(
                map(
                    lambda x: "lte_rlc_per_rb_dl_rb_id_{}".format(x + 1),
                    range(n_param_args),
                )
            )
            + list(
                map(
                    lambda x: "lte_rlc_per_rb_cfg_index_{}".format(x + 1),
                    range(n_param_args),
                )
            )
            + list(
                map(
                    lambda x: "lte_rlc_per_rb_dl_tp_{}".format(x + 1),
                    range(n_param_args),
                )
            ),
            "lte_rlc_stats",
        ),
    ]
    return params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        not_null_first_col=True,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )


def get_lte_pucch_pdsch_disp_df(dbcon, time_before):
    n_param_args = 4
    parameter_to_columns_list = [
        (
            [
                "---- PUCCH ----",
                "CQI CW 0",
                "CQI CW 1",
                "CQI N Sub-bands",
                "Rank Indicator",
            ],
            list(map(lambda x: '"" as unused_{}'.format(x + 1), range(n_param_args)))
            + list(map(lambda x: "lte_cqi_cw0_{}".format(x + 1), range(n_param_args)))
            + list(map(lambda x: "lte_cqi_cw1_{}".format(x + 1), range(n_param_args)))
            + list(
                map(
                    lambda x: "lte_cqi_n_subbands_{}".format(x + 1), range(n_param_args)
                )
            )
            + list(
                map(
                    lambda x: "lte_rank_indication_{}".format(x + 1),
                    range(n_param_args),
                )
            ),
            "lte_cqi",
        ),
        (
            [
                "---- PDSCH ----",
                "PDSCH Serving Cell ID",
                "PDSCH RNTI ID",
                "PDSCH RNTI Type",
                "PDSCH Serving N Tx Antennas",
                "PDSCH Serving N Rx Antennas",
                "PDSCH Transmission Mode Current",
                "PDSCH Spatial Rank",
                "PDSCH Rb Allocation Slot 0",
                "PDSCH Rb Allocation Slot 1",
                "PDSCH PMI Type",
                "PDSCH PMI Index",
                "PDSCH Stream[0] Block Size",
                "PDSCH Stream[0] Modulation",
                "PDSCH Traffic To Pilot Ratio",
                "PDSCH Stream[1] Block Size",
                "PDSCH Stream[1] Modulation",
            ],
            list(map(lambda x: '"" as unused_{}'.format(x + 1), range(n_param_args)))
            + list(
                map(
                    lambda x: "lte_pdsch_serving_cell_id_{}".format(x + 1),
                    range(n_param_args),
                )
            )
            + list(
                map(lambda x: "lte_pdsch_rnti_id_{}".format(x + 1), range(n_param_args))
            )
            + list(
                map(
                    lambda x: "lte_pdsch_rnti_type_{}".format(x + 1),
                    range(n_param_args),
                )
            )
            + list(
                map(
                    lambda x: "lte_pdsch_serving_n_tx_antennas_{}".format(x + 1),
                    range(n_param_args),
                )
            )
            + list(
                map(
                    lambda x: "lte_pdsch_serving_n_rx_antennas_{}".format(x + 1),
                    range(n_param_args),
                )
            )
            + list(
                map(
                    lambda x: "lte_pdsch_transmission_mode_current_{}".format(x + 1),
                    range(n_param_args),
                )
            )
            + list(
                map(
                    lambda x: "lte_pdsch_spatial_rank_{}".format(x + 1),
                    range(n_param_args),
                )
            )
            + list(
                map(
                    lambda x: "lte_pdsch_rb_allocation_slot0_{}".format(x + 1),
                    range(n_param_args),
                )
            )
            + list(
                map(
                    lambda x: "lte_pdsch_rb_allocation_slot1_{}".format(x + 1),
                    range(n_param_args),
                )
            )
            + list(
                map(
                    lambda x: "lte_pdsch_pmi_type_{}".format(x + 1), range(n_param_args)
                )
            )
            + list(
                map(
                    lambda x: "lte_pdsch_pmi_index_{}".format(x + 1),
                    range(n_param_args),
                )
            )
            + list(
                map(
                    lambda x: "lte_pdsch_stream0_transport_block_size_bits_{}".format(
                        x + 1
                    ),
                    range(n_param_args),
                )
            )
            + list(
                map(
                    lambda x: "lte_pdsch_stream0_modulation_{}".format(x + 1),
                    range(n_param_args),
                )
            )
            + list(
                map(
                    lambda x: "lte_pdsch_traffic_to_pilot_ratio_{}".format(x + 1),
                    range(n_param_args),
                )
            )
            + list(
                map(
                    lambda x: "lte_pdsch_stream1_transport_block_size_bits_{}".format(
                        x + 1
                    ),
                    range(n_param_args),
                )
            )
            + list(
                map(
                    lambda x: "lte_pdsch_stream1_modulation_{}".format(x + 1),
                    range(n_param_args),
                )
            ),
            "lte_pdsch_meas",
        ),
    ]
    return params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        not_null_first_col=False,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )


def get_volte_disp_df(dbcon, time_before):
    parameter_to_columns_list = [
        (
            [
                "Time",
                "Codec:",
            ],
            [
                "time",
                '"" as unused0',
            ],
            "lte_volte_stats",
        ),
        (
            [
                "AMR SpeechCodec-RX",
                "AMR SpeechCodec-TX",
                "Delay interval avg:",
                "Audio Packet delay (ms.)",
            ],
            [
                "gsm_speechcodecrx",
                "gsm_speechcodectx",
                '"" as unused1',
                "vocoder_amr_audio_packet_delay_avg",
            ],
            "vocoder_info",
        ),
        (
            [
                "RTP Packet delay (ms.)",
                "RTCP SR Params:",
                "RTCP Round trip time (ms.)",
                "RTCP SR Params - Jitter DL:",
                "RTCP SR Jitter DL (ts unit)",
                "RTCP SR Jitter DL (ms.)",
                "RTCP SR Params - Jitter UL:",
                "RTCP SR Jitter UL (ts unit)",
                "RTCP SR Jitter UL (ms.)",
                "RTCP SR Params - Packet loss rate:",
                "RTCP SR Packet loss DL (%)",
                "RTCP SR Packet loss UL (%)",
            ],
            [
                "lte_volte_rtp_pkt_delay_avg",
                '"" as unused2',
                "lte_volte_rtp_round_trip_time",
                '"" as unused3',
                "lte_volte_rtp_jitter_dl",
                "lte_volte_rtp_jitter_dl_millis",
                '"" as unused4',
                "lte_volte_rtp_jitter_ul",
                "lte_volte_rtp_jitter_ul_millis",
                '"" as unused5',
                "lte_volte_rtp_packet_loss_rate_dl",
                "lte_volte_rtp_packet_loss_rate_ul",
            ],
            "lte_volte_stats",
        ),
    ]
    return params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        not_null_first_col=True,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )


def get_lte_data_disp_df(dbcon, time_before):
    n_param_args = 4
    df_list = []
    parameter_to_columns_list = [
        (["RRC State",], ["lte_rrc_state",], "lte_rrc_state",),
    ]
    df_rrc = params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        default_table="lte_rrc_state",
        not_null_first_col=False,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )
    df_list.append(df_rrc)

    parameter_to_columns_list = [
        (
            ["L1 Combined (Mbps)", "L1 Combined (Kbps)",],
            [
                "lte_l1_dl_throughput_all_carriers_mbps",
                "lte_l1_dl_throughput_all_carriers",
            ],
            "lte_l1_dl_tp",
        ),
        (
            ["L1 Combined (Mbps)", "L1 Combined (Kbps)",],
            [
                "lte_l1_ul_throughput_all_carriers_mbps_1",
                "lte_l1_ul_throughput_all_carriers_1",
            ],
            "lte_l1_ul_tp",
        ),
    ]
    df_tp = params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        not_null_first_col=False,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )

    df_t = pd.DataFrame(columns=["param", 1, 2])
    df_t.loc[0] = ["Throughput", "DL", "UL"]
    df_t.loc[1] = ["L1 Combined (Mbps)", df_tp.iloc[0, 1], df_tp.iloc[2, 1]]
    df_t.loc[2] = ["L1 Combined (kbps)", df_tp.iloc[1, 1], df_tp.iloc[3, 1]]
    df_list.append(df_t)

    parameter_to_columns_list = [
        (
            ["PDCP (Mbps)", "PDCP (kbps)",],
            [
                "lte_pdcp_dl_throughput_mbps",
                "lte_pdcp_ul_throughput_mbps",
                "lte_pdcp_dl_throughput",
                "lte_pdcp_ul_throughput",
            ],
            "lte_pdcp_stats",
        ),
        (
            ["RLC (Mbps)", "RLC (kbps)",],
            [
                "lte_rlc_dl_tp_mbps",
                "lte_rlc_ul_tp_mbps",
                "lte_rlc_dl_tp",
                "lte_rlc_ul_tp",
            ],
            "lte_rlc_stats",
        ),
        (["MAC (Kbps)",], ["lte_mac_dl_tp", "lte_mac_ul_tp",], "lte_mac_ul_tx_stat",),
    ]
    df_pdcp = params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        not_null_first_col=False,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )
    df_list.append(df_pdcp)

    parameter_to_columns_list = [
        (
            ["TransMode RRC tm",],
            ["lte_transmission_mode_l3",],
            "lte_rrc_transmode_info",
        ),
    ]
    df_tran = params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        not_null_first_col=False,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )
    df_list.append(df_tran)

    df_cell = pd.DataFrame(columns=["param", 1, 2, 3, 4])
    df_cell.loc[1] = ["", "PCC", "SCC0", "SCC1", "SCC2"]
    df_list.append(df_cell)

    parameter_to_columns_list = [
        (
            ["L1 DL TP (Mbps)",],
            list(
                map(
                    lambda x: "lte_l1_throughput_mbps_{}".format(x + 1),
                    range(n_param_args),
                )
            ),
            "lte_l1_dl_tp",
        ),
        (
            ["L1 UL TP (Mbps)",],
            list(
                map(
                    lambda x: "lte_l1_ul_throughput_mbps_{}".format(x + 1),
                    range(n_param_args),
                )
            ),
            "lte_l1_ul_tp",
        ),
        (
            ["TransMode Cur",],
            list(
                map(
                    lambda x: "lte_pdsch_transmission_mode_current_{}".format(x + 1),
                    range(n_param_args),
                )
            ),
            "lte_pdsch_meas",
        ),
        (
            ["EARFCN",],
            list(map(lambda x: "lte_earfcn_{}".format(x + 1), range(n_param_args))),
            "lte_cell_meas",
        ),
        (
            ["PCI",],
            list(
                map(
                    lambda x: "lte_pdsch_serving_cell_id_{}".format(x + 1),
                    range(n_param_args),
                )
            ),
            "lte_pdsch_meas",
        ),
        (
            [
                "PUSCH Stats:",
                "PRB Alloc UL",
                "MCS Index UL",
                "Modulation UL",
                "L1 UL Bler",
            ],
            list(map(lambda x: '"" as unused_{}'.format(x + 1), range(n_param_args)))
            + list(
                map(lambda x: "lte_l1_ul_n_rbs_{}".format(x + 1), range(n_param_args))
            )
            + list(
                map(lambda x: "lte_ul_mcs_index_{}".format(x + 1), range(n_param_args))
            )
            + list(
                map(
                    lambda x: "lte_pusch_modulation_{}".format(x + 1),
                    range(n_param_args),
                )
            )
            + list(
                map(lambda x: "lte_l1_ul_bler_{}".format(x + 1), range(n_param_args))
            ),
            "lte_l1_ul_tp",
        ),
        (
            ["DCI",],
            list(map(lambda x: "lte_pdcch_dci_{}".format(x + 1), range(n_param_args))),
            "lte_pdcch_dec_result",
        ),
        (
            ["PDSCH Stats:", "BLER",],
            list(map(lambda x: '"" as unused_{}'.format(x + 1), range(n_param_args)))
            + list(map(lambda x: "lte_bler_{}".format(x + 1), range(n_param_args))),
            "lte_l1_dl_tp",
        ),
        (
            ["Serv N Tx Ant", "Serv N Tx Ant", "Spatial Rank"],
            list(
                map(
                    lambda x: "lte_pdsch_serving_n_tx_antennas_{}".format(x + 1),
                    range(n_param_args),
                )
            )
            + list(
                map(
                    lambda x: "lte_pdsch_serving_n_rx_antennas_{}".format(x + 1),
                    range(n_param_args),
                )
            )
            + list(
                map(
                    lambda x: "lte_pdsch_spatial_rank_{}".format(x + 1),
                    range(n_param_args),
                )
            ),
            "lte_pdsch_meas",
        ),
        (
            ["Rank Ind", "CQI CW0", "CQI CW1"],
            list(
                map(
                    lambda x: "lte_rank_indication_{}".format(x + 1),
                    range(n_param_args),
                )
            )
            + list(map(lambda x: "lte_cqi_cw0_{}".format(x + 1), range(n_param_args)))
            + list(map(lambda x: "lte_cqi_cw1_{}".format(x + 1), range(n_param_args))),
            "lte_cqi",
        ),
        (
            ["PRB Alloc"],
            list(
                map(
                    lambda x: "lte_pdsch_n_rb_allocated_latest_{}".format(x + 1),
                    range(n_param_args),
                )
            ),
            "lte_pdsch_meas",
        ),
        (
            ["PRB Ma"],
            list(
                map(lambda x: "lte_mib_max_n_rb_{}".format(x + 1), range(n_param_args))
            ),
            "lte_mib_info",
        ),
        (
            ["PRB Util (alloc/bw) %"],
            list(
                map(
                    lambda x: "lte_prb_alloc_in_bandwidth_percent_latest_{}".format(
                        x + 1
                    ),
                    range(n_param_args),
                )
            ),
            "lte_pdsch_meas",
        ),
        (
            ["DL Bandwidth (MHz)"],
            list(
                map(
                    lambda x: "lte_mib_dl_bandwidth_mhz_{}".format(x + 1),
                    range(n_param_args),
                )
            ),
            "lte_mib_info",
        ),
        (["PCC UL Bw (Mhz)"], ["lte_sib2_ul_bandwidth_mhz"], "lte_sib2_info"),
        (
            ["Time Scheduled %", "MCS Index"],
            list(
                map(
                    lambda x: "lte_pdsch_sched_percent_{}".format(x + 1),
                    range(n_param_args),
                )
            )
            + list(
                map(lambda x: "lte_mcs_index_{}".format(x + 1), range(n_param_args))
            ),
            "lte_l1_dl_tp",
        ),
        (
            [
                "BlockSizeBits[0]",
                "Modulation[0]",
                "BlockSizeBits[1]",
                "Modulation[1]",
                "TrafficToPilot Ratio",
                "RNTI Type",
                "RNTI ID",
                "PMI Type",
                "PMI Index",
            ],
            list(
                map(
                    lambda x: "lte_pdsch_stream0_transport_block_size_bits_{}".format(
                        x + 1
                    ),
                    range(n_param_args),
                )
            )
            + list(
                map(
                    lambda x: "lte_pdsch_stream0_modulation_{}".format(x + 1),
                    range(n_param_args),
                )
            )
            + list(
                map(
                    lambda x: "lte_pdsch_stream1_transport_block_size_bits_{}".format(
                        x + 1
                    ),
                    range(n_param_args),
                )
            )
            + list(
                map(
                    lambda x: "lte_pdsch_stream1_modulation_{}".format(x + 1),
                    range(n_param_args),
                )
            )
            + list(
                map(
                    lambda x: "lte_pdsch_traffic_to_pilot_ratio_{}".format(x + 1),
                    range(n_param_args),
                )
            )
            + list(
                map(
                    lambda x: "lte_pdsch_rnti_type_{}".format(x + 1),
                    range(n_param_args),
                )
            )
            + list(
                map(lambda x: "lte_pdsch_rnti_id_{}".format(x + 1), range(n_param_args))
            )
            + list(
                map(
                    lambda x: "lte_pdsch_pmi_type_{}".format(x + 1), range(n_param_args)
                )
            )
            + list(
                map(
                    lambda x: "lte_pdsch_pmi_index_{}".format(x + 1),
                    range(n_param_args),
                )
            ),
            "lte_pdsch_meas",
        ),
    ]
    df_tran = params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        not_null_first_col=False,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )
    df_list.append(df_tran)

    final_df = pd.concat(df_list, sort=False)
    return final_df
