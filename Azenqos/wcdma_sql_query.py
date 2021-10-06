
WCDMA_ACTIVE_MONITORED_SQL_LIST_DICT = {
    "UARFCN":[
        '''
        select log_hash, time as Time,
        wcdma_aset_cellfreq_1 as Aset1,
        wcdma_aset_cellfreq_2 as Aset2,
        wcdma_aset_cellfreq_3 as Aset3,
        wcdma_mset_cellfreq_1 as Mset1,
        wcdma_mset_cellfreq_2 as Mset2,
        wcdma_mset_cellfreq_3 as Mset3,
        wcdma_mset_cellfreq_4 as Mset4,
        wcdma_mset_cellfreq_5 as Mset5,
        wcdma_mset_cellfreq_6 as Mset6,
        wcdma_dset_cellfreq_1 as Dset1,
        wcdma_dset_cellfreq_2 as Dset2,
        wcdma_dset_cellfreq_3 as Dset3,
        wcdma_dset_cellfreq_4 as Dset4
        from wcdma_cell_meas
        ''',
    ],
    "PSC":[
        '''
        select '' as log_hash, '' as Time,
        wcdma_aset_sc_1 as Aset1,
        wcdma_aset_sc_2 as Aset2,
        wcdma_aset_sc_3 as Aset3,
        wcdma_mset_sc_1 as Mset1,
        wcdma_mset_sc_2 as Mset2,
        wcdma_mset_sc_3 as Mset3,
        wcdma_mset_sc_4 as Mset4,
        wcdma_mset_sc_5 as Mset5,
        wcdma_mset_sc_6 as Mset6,
        wcdma_dset_sc_1 as Dset1,
        wcdma_dset_sc_2 as Dset2,
        wcdma_dset_sc_3 as Dset3,
        wcdma_dset_sc_4 as Dset4
        from wcdma_cell_meas
        ''',
    ],
    "Ec/Io":[
        '''
        select '' as log_hash, '' as Time,
        wcdma_aset_ecio_1 as Aset1,
        wcdma_aset_ecio_2 as Aset2,
        wcdma_aset_ecio_3 as Aset3,
        wcdma_mset_ecio_1 as Mset1,
        wcdma_mset_ecio_2 as Mset2,
        wcdma_mset_ecio_3 as Mset3,
        wcdma_mset_ecio_4 as Mset4,
        wcdma_mset_ecio_5 as Mset5,
        wcdma_mset_ecio_6 as Mset6,
        wcdma_dset_ecio_1 as Dset1,
        wcdma_dset_ecio_2 as Dset2,
        wcdma_dset_ecio_3 as Dset3,
        wcdma_dset_ecio_4 as Dset4
        from wcdma_cell_meas
        ''',
    ],
    "RSCP":[
        '''
        select '' as log_hash, '' as Time,
        wcdma_aset_rscp_1 as Aset1,
        wcdma_aset_rscp_2 as Aset2,
        wcdma_aset_rscp_3 as Aset3,
        wcdma_mset_rscp_1 as Mset1,
        wcdma_mset_rscp_2 as Mset2,
        wcdma_mset_rscp_3 as Mset3,
        wcdma_mset_rscp_4 as Mset4,
        wcdma_mset_rscp_5 as Mset5,
        wcdma_mset_rscp_6 as Mset6,
        wcdma_dset_rscp_1 as Dset1,
        wcdma_dset_rscp_2 as Dset2,
        wcdma_dset_rscp_3 as Dset3,
        wcdma_dset_rscp_4 as Dset4
        from wcdma_cell_meas
        ''',
    ],
}

WCDMA_RADIO_PARAMS_SQL_LIST = [
    '''select time as 'Time',wcdma_txagc as 'Tx Power',wcdma_maxtxpwr as 'Max Tx Power' from wcdma_tx_power''',
    '''select wcdma_rssi as 'RSSI' from wcdma_rx_power''',
    '''select wcdma_sir as 'SIR' from wcdma_sir''',
    '''select wcdma_rrc_state as 'RRC State' from wcdma_rrc_state''',
    '''select gsm_speechcodectx as 'Speech Codec TX',gsm_speechcodecrx as 'Speech Codec RX' from vocoder_info''',
    '''select android_cellid as 'Cell ID',android_rnc_id as 'RNC ID' from android_info_1sec'''
]

WCDMA_BLER_SQL_LIST = [
    '''select time as 'Time',wcdma_bler_average_percent_all_channels as 'BLER Average Percent',wcdma_bler_calculation_window_size as 'BLER Calculation Window Size',wcdma_bler_n_transport_channels as 'BLER N Transport Channels' from wcdma_bler'''
]

WCDMA_BLER_SQL_LIST_DICT = {}

for i in range(10):
    index_str = str(i+1)
    WCDMA_BLER_SQL_LIST_DICT[index_str] = ['''
        select 
        data_wcdma_bearer_id_{arg} as 'Bearers ID',
        data_wcdma_bearer_rate_dl_{arg} as 'Bearers Rate DL',
        data_wcdma_bearer_rate_ul_{arg} as 'Bearers Rate UL'
        from wcdma_bearers
        '''.format(arg=index_str)]
