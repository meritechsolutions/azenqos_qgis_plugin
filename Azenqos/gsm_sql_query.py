GSM_RADIO_PARAMS_SQL_LIST = [
    '''select time as 'Time',gsm_rxlev_full_dbm as 'RxLev Full',gsm_rxlev_sub_dbm as 'RxLev Sub',gsm_rxqual_full as 'RxQual Full',gsm_rxqual_sub as 'RxQual Sub' from gsm_cell_meas''',
    '''select gsm_ta as 'TA' from gsm_tx_meas''',
    '''select gsm_radiolinktimeout_max as 'RLT (Max)' from gsm_rl_timeout_counter''',
    '''select gsm_radiolinktimeout_current as 'RLT (Current)' from gsm_rlt_counter''',
    '''select gsm_dtxused as 'DTX Used' from gsm_rr_measrep_params''',
    '''select gsm_txpower as 'TxPower' from gsm_tx_meas''',
    '''select gsm_fer as 'FER' from vocoder_info'''
]

SERV_COL_DICT = {
    "Cell Name":{"gsm_cellfile_matched_cellname":"gsm_cell_meas"},
    "BSIC":{"gsm_bsic":"gsm_cell_meas"},
    "LAC":{"gsm_lac":"gsm_serv_cell_info"},
    "ARFCN ":{"gsm_arfcn_bcch":"gsm_cell_meas"},
    "RxLev":{"gsm_rxlev_sub_dbm":"gsm_cell_meas"},
    "C1":{"gsm_c1":"gsm_cell_meas"},
    "C2":{"gsm_c2":"gsm_cell_meas"},
    "C31":{"gsm_c31":"gsm_cell_meas"},
    "C32":{"gsm_c32":"gsm_cell_meas"}
    }
NEIGH_COL_DICT = {
    "Cell Name":"gsm_cellfile_matched_neighbor_cellname",
    "BSIC":"gsm_cellfile_matched_neighbor_lac_",
    "LAC":"gsm_neighbor_bsic_",
    "ARFCN ":"gsm_neighbor_arfcn_",
    "RxLev":"gsm_neighbor_rxlev_dbm_",
    "C1":"gsm_neighbor_c1_",
    "C2":"gsm_neighbor_c2_",
    "C31":"gsm_neighbor_c31_",
    "C32":"gsm_neighbor_c32_"
    }

GSM_SERV_AND_NEIGH_SQL_LIST_DICT = {}
first_round = True
separator = ","
for key in SERV_COL_DICT:
    SQL_LIST = []
    SERV_SQL_LIST = []
    NEIGH_SQL_LIST = []
    for serv_key in SERV_COL_DICT[key]:
        serv_sql = "select {} as 'serv' from {}".format(serv_key, SERV_COL_DICT[key][serv_key])
        SERV_SQL_LIST.append(serv_sql)
    for i in range(32):
        if first_round:
            if key == "Cell Name":
                neigh_sql = "{} as 'neigh{}'".format(NEIGH_COL_DICT[key], i+1)
                NEIGH_SQL_LIST.append(neigh_sql)
            first_round = False
        else:
            if key == "Cell Name":
                neigh_sql = " '' as 'neigh{}'".format(i+1)
                NEIGH_SQL_LIST.append(neigh_sql)
        if key != "Cell Name":
            neigh_sql = "{}{} as 'neigh{}'".format(NEIGH_COL_DICT[key],i+1, i+1)
            NEIGH_SQL_LIST.append(neigh_sql)

    serv_sql = separator.join(SERV_SQL_LIST)
    SQL_LIST.append(serv_sql)
    neigh_sql = "select "+separator.join(NEIGH_SQL_LIST)+" from gsm_cell_meas"
    SQL_LIST.append(neigh_sql)
    GSM_SERV_AND_NEIGH_SQL_LIST_DICT[key] = SQL_LIST

GSM_CURRENT_CHANNEL_SQL_LIST = [
    '''select time as 'Time',gsm_cellfile_matched_cellname as 'Cellname',gsm_cgi as 'CGI' from gsm_cell_meas''','''select gsm_channeltype as 'Channel Type' from gsm_rr_chan_desc''','''select gsm_subchannelnumber as 'Sub Channel Number' from gsm_rr_subchan''','''select gsm_maio as 'Mobile Allocation Index Offset (MAIO)',gsm_hsn as 'Hopping Sequence Number (HSN)' from gsm_rr_chan_desc''','''select gsm_cipheringalgorithm as 'Cipering Algorithm' from gsm_rr_cipher_alg''','''select gsm_ms_powercontrollevel as 'MS Power Control Level' from gsm_rr_power_ctrl''','''select gsm_channelmode as 'Channel Mode' from gsm_chan_mode''',
    '''select gsm_speechcodectx as 'Speech Codec TX',gsm_speechcodecrx as 'Speech Codec RX' from vocoder_info''',
    '''select gsm_hoppingfrequencies as 'Hopping Frequencies' from gsm_hopping_list''',
    '''select gsm_arfcn_bcch as 'ARFCN BCCH' from gsm_cell_meas''',
    '''select gsm_arfcn_tch as 'ARFCN TCH' from gsm_rr_chan_desc''',
    '''select gsm_timeslot as 'Time Slot' from gsm_rr_chan_desc'''
]

WORST_COL_DICT = {
    "ARFCN":"gsm_coi_worst_arfcn_1",
    "VALUE":"gsm_coi_worst",
    }
AVG_COL_DICT = {
    "ARFCN":"gsm_coi_arfcn_",
    "VALUE":"gsm_coi_",
    }

GSM_COI_SQL_LIST_DICT = {}
separator = ","
for key in WORST_COL_DICT:
    SQL_LIST = []
    WORST_SQL_LIST = []
    AVG_SQL_LIST = []
    worst_sql = "select {} as 'Worst', '' as 'Avg' from gsm_coi_per_chan".format(WORST_COL_DICT[key])
    WORST_SQL_LIST.append(worst_sql)
    for i in range(32):
        avg_sql = "{}{} as '{}'".format(AVG_COL_DICT[key],i+1, i+1)
        AVG_SQL_LIST.append(avg_sql)

    worst_sql = separator.join(WORST_SQL_LIST)
    SQL_LIST.append(worst_sql)
    avg_sql = "select "+separator.join(AVG_SQL_LIST)+" from gsm_coi_per_chan"
    SQL_LIST.append(avg_sql)
    GSM_COI_SQL_LIST_DICT[key] = SQL_LIST
