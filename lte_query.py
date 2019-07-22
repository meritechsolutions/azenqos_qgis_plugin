from PyQt5.QtSql import QSqlQuery, QSqlDatabase

class LteDataQuery:
    def __init__(self, database, currentDateTimeString):
        self.timeFilter = ''
        self.azenqosDatabase = database
        if currentDateTimeString:
            self.timeFilter = currentDateTimeString

    def getRadioParameters(self):
        self.openConnection()
        dataList = []
        condition = ''
        fieldsList = [
            'Time', 'Band', 'E-ARFCN', 'Serving PCI', 'Serving RSRP[0]',
            'Serving RSRP[1]', 'Serving RSRP', 'Serving RSRQ[0]',
            'Serving RSRQ[1]', 'Serving RSRQ', 'SINR Rx[0]', 'SINR Rx[1]',
            'SINR', 'RSSI Rx[0]', 'RSSI Rx[1]', 'RSSI', 'BLER', 'CQI CW[0]',
            'CQI CW[1]', 'Tx Power', 'PUCCH TxPower (dBm)',
            'PUSCH TxPower (dBm)', 'TimingAdvance',
            'Transmission Mode (RRC-tm)', 'LTE RRC State', 'LTE EMM State',
            'LTE RRC Substate', 'Modern ServCellInfo', 'Allowed Access', 'MCC',
            'MNC', 'TAC', 'Cell ID (ECI)', 'eNodeB ID', 'LCI', 'PCI',
            'Derived SCC ECI', 'Derived SCC eNodeB ID', 'Derived SCC LCI',
            'DL EARFCN', 'UL EARFCN', 'DL Bandwidth (Mhz)',
            'UL Bandwidth (Mhz)', 'SCC DL Bandwidth (Mhz)', 'SIB1 info:',
            'sib1 MCC', 'sib1 MNC', 'sib1 TAC', 'sib1 ECI', 'sib1 eNBid',
            'sib1 LCI', 'TDD Config:', 'SubframeAssignment',
            'SpclSubframePattern', 'DedBearer QCI'
        ]
        selectedColumns = """lcm.time as Time, lcm.lte_band_1 as Band, lcm.lte_earfcn_1 as 'E-ARFCN', lsci.lte_serv_cell_info_pci as 'Serving PCI',
                                lcm.lte_inst_rsrp_rx0_1 as 'Serving RSRP[0]', lcm.lte_inst_rsrp_rx1_1 as 'Serving RSRP[1]', lcm.lte_inst_rsrp_1 as 'Serving RSRP', lcm.lte_inst_rsrq_rx0_1 as 'Serving RSRQ[0]', lcm.lte_inst_rsrq_rx1_1 as 'Serving RSRP[1]', lcm.lte_inst_rsrq_1 as 'Serving RSRQ', lcm.lte_sinr_rx0_1 as 'SINR Rx[0]', lcm.lte_sinr_rx1_1 as 'SINR Rx[1]', lcm.lte_sinr_1 as 'SINR', lcm.lte_inst_rssi_rx0_1 as 'RSSI Rx[0]', lcm.lte_inst_rssi_rx1_1 as 'RSSI Rx[1]', lcm.lte_inst_rssi_1 as 'RSSI', lldt.lte_bler_1 as 'BLER', lc.lte_cqi_cw0_1 as 'CQI CW[0]', lc.lte_cqi_cw1_1 as 'CQI CW[1]', ltp.lte_tx_power as 'Tx Power', lpcti.lte_pucch_tx_power as 'PUCCH TxPower (dBm)', lpsti.lte_pusch_tx_power as 'PUSCH TxPower (dBm)', lft.lte_ta as 'TimingAdvance', lrti.lte_transmission_mode_l3 as 'Transmission Mode (RRC-tm)', lrs.lte_rrc_state as 'LTE RRC State', les.lte_emm_state as 'LTE EMM State', les.lte_emm_substate as 'LTE EMM Substate', '____' as 'Modem ServCellInfo', lsci.lte_serv_cell_info_allowed_access as 'Allowed Access', lsci.lte_serv_cell_info_mcc as 'MCC', lsci.lte_serv_cell_info_mnc as 'MNC',
                                lsci.lte_serv_cell_info_tac as 'TAC', lsci.lte_serv_cell_info_eci as 'Cell ID (ECI)', lsci.lte_serv_cell_info_enb_id as 'eNodeB ID', lsci.lte_scc_derived_lci as 'LCI', lsci.lte_serv_cell_info_pci as 'PCI', lsci.lte_scc_derived_eci as 'Derviced SCC ECI', lsci.lte_scc_derived_enb_id as 'Derived SCC eNodeB ID', lsci.lte_scc_derived_lci as 'Derived SCC LCI', lsci.lte_serv_cell_info_dl_freq as 'DL EARFCN', lsci.lte_serv_cell_info_ul_freq as 'UL EARFCN',
                                lsci.lte_serv_cell_info_dl_bandwidth_mhz as 'DL Bandwidth (Mhz)', lsci.lte_serv_cell_info_ul_bandwidth_mhz as 'UL Bandwidth (Mhz)', '' as 'SCC DL Bandwidth (Mhz)', '____' as 'SIB1 info:', lsoi.lte_sib1_mcc as 'sib1 MCC', lsoi.lte_sib1_mnc as 'sib1 MNC', lsoi.lte_sib1_tac as 'sib1 TAC', lsoi.lte_sib1_eci as 'sib ECI', lsoi.lte_sib1_enb_id as 'sib1 eNBid', lsoi.lte_sib1_local_cell_id as 'sib1 LCI', '____' as 'TDD Config:', ltc.lte_tdd_config_subframe_assignment as 'SubframeAssignment', ltc.lte_tdd_config_special_subframe_pattern as 'SpclSubframePattern', '' as 'DedBearer QCI'"""

        if self.timeFilter:
            condition = "WHERE lcm.time <= '%s'" % (self.timeFilter)

        queryString = """SELECT %s
                        FROM lte_cell_meas lcm
                        LEFT JOIN lte_serv_cell_info lsci ON lcm.time = lsci.time
                        LEFT JOIN lte_l1_dl_tp lldt ON lcm.time = lldt.time
                        LEFT JOIN lte_cqi lc ON lcm.time = lc.time
                        LEFT JOIN lte_tx_power ltp ON lcm.time = ltp.time
                        LEFT JOIN lte_pucch_tx_info lpcti ON lcm.time = lpcti.time
                        LEFT JOIN lte_pusch_tx_info lpsti ON lcm.time = lpsti.time
                        LEFT JOIN lte_frame_timing lft ON lcm.time = lft.time
                        LEFT JOIN lte_rrc_transmode_info lrti ON lcm.time = lrti.time
                        LEFT JOIN lte_rrc_state lrs ON lcm.time = lrs.time
                        LEFT JOIN lte_emm_state les ON lcm.time = les.time
                        LEFT JOIN lte_sib1_info lsoi ON lcm.time = lsoi.time
                        LEFT JOIN lte_tdd_config ltc ON lcm.time = ltc.time
                        %s
                        ORDER BY lcm.time DESC LIMIT 1""" % (selectedColumns,
                                                             condition)
        query = QSqlQuery()
        query.exec_(queryString)
        fieldCount = len(selectedColumns.split(","))
        queryRowCount = query.record().count()
        if queryRowCount > 0:
            while query.next():
                for index in range(fieldCount):
                    columnName = fieldsList[index]
                    value = ''
                    if query.value(index) != '':
                        value = query.value(index)
                    dataList.append([columnName, value, '', ''])
        else:
            for index in range(fieldCount):
                columnName = fieldsList[index]
                value = ''
                dataList.append([columnName, value, '', ''])
        self.closeConnection()
        return dataList

    def getServingAndNeighbors(self):
        self.openConnection()
        MAX_NEIGHBORS = 16
        dataList = []
        typeHeader = {
            'serving': ['dateString', 'Serving cell:', '', '', '', ''],
            'neigh': ['', 'Neighbor cells:', '', '', '', '']
        }
        emptyRow = ['', '', '', '', '', '']
        condition = ''

        # Set query condition for serving cell
        if self.timeFilter:
            condition = "WHERE lcm.time <= '%s'" % (self.timeFilter)

        typeHeader['serving'][0] = self.timeFilter
        dataList.append(typeHeader['serving'])

        queryString = """SELECT lcm.lte_earfcn_1, lsci.lte_serv_cell_info_band, lsci.lte_serv_cell_info_pci, lcm.lte_inst_rsrp_1,
                        lcm.lte_inst_rsrq_1
                        FROM lte_cell_meas as lcm
                        LEFT JOIN lte_serv_cell_info lsci ON lcm.time = lsci.time
                        %s
                        ORDER BY lcm.time DESC
                        LIMIT 1""" % (condition)
        query = QSqlQuery()
        query.exec_(queryString)
        while query.next():
            servingCell = [
                '',
                query.value(0),
                query.value(1),
                query.value(2),
                query.value(3),
                query.value(4)
            ]
            dataList.append(servingCell)

        # Set query condition for neigh cell
        if self.timeFilter:
            condition = "WHERE lnm.time <= '%s'" % (self.timeFilter)

        for neighbor in range(1, MAX_NEIGHBORS):
            queryString = """SELECT lnm.lte_neigh_earfcn_%d, lnm.lte_neigh_band_%d, lnm.lte_neigh_physical_cell_id_%d, lnm.lte_neigh_rsrp_%d,
                            lnm.lte_neigh_rsrq_%d
                            FROM lte_neigh_meas as lnm
                            %s
                            ORDER BY lnm.time DESC
                            LIMIT 1""" % (neighbor, neighbor, neighbor,
                                          neighbor, neighbor, condition)
            query = QSqlQuery()
            query.exec_(queryString)
            rowCount = query.record().count()
            if rowCount > 0:
                while query.next():
                    if query.value(0):
                        if neighbor == 1:
                            dataList.append(typeHeader['neigh'])
                        neighCell = [
                            '',
                            query.value(0),
                            query.value(1),
                            query.value(2),
                            query.value(3),
                            query.value(4)
                        ]
                        dataList.append(neighCell)
                    else:
                        break
            else:
                dataList.append(emptyRow)
        self.closeConnection()
        return dataList

    def getPucchPdschParameters(self):
        self.openConnection()

        dataList = []
        condition = ""
        maxBearers = 8
        pucchFields = [
            '---- PUCCH ----', 'CQI CW 0', 'CQI CW 1', 'CQI N Sub-bands',
            'Rank Indicator'
        ]
        pdschFields = [
            '---- PDSCH ----', 'PDSCH Serving Cell ID', 'PDSCH RNTI ID',
            'PDSCH RNTI Type', 'PDSCH Serving N Tx Antennas',
            'PDSCH Serving N Rx Antennas', 'PDSCH Transmission Mode Current',
            'PDSCH Spatial Rank', 'PDSCH Rb Allocation Slot 0',
            'PDSCH Rb Allocation Slot 1', 'PDSCH PMI Type', 'PDSCH PMI Index',
            'PDSCH Stream[0] Block Size', 'PDSCH Stream[0] Modulation',
            'PDSCH Traffic To Pilot Ratio', 'PDSCH Stream[1] Block Size',
            'PDSCH Stream[1] Modulation'
        ]

        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)
            dateString = '%s' % (self.timeFilter)

        dataList.append(['Time', self.timeFilter])

        queryString = """SELECT '' as header, lte_cqi_cw0_1, lte_cqi_cw1_1, lte_cqi_n_subbands_1, lte_rank_indication_1
                        FROM lte_cqi
                        %s
                        ORDER BY time DESC
                        LIMIT 1""" % (condition)
        query = QSqlQuery()
        query.exec_(queryString)
        while query.next():
            for field in range(len(pucchFields)):
                if query.value(field):
                    dataList.append([pucchFields[field], query.value(field)])
                else:
                    dataList.append([pucchFields[field], ''])

        queryString = """SELECT '' as pdsch, lte_pdsch_serving_cell_id_1, lte_pdsch_rnti_id_1, lte_pdsch_rnti_type_1,
                        lte_pdsch_serving_n_tx_antennas_1, lte_pdsch_serving_n_rx_antennas_1,
                        lte_pdsch_transmission_mode_current_1, lte_pdsch_spatial_rank_1,
                        lte_pdsch_rb_allocation_slot0_1, lte_pdsch_rb_allocation_slot1_1,
                        lte_pdsch_pmi_type_1, lte_pdsch_pmi_index_1,lte_pdsch_stream0_transport_block_size_bits_1,
                        lte_pdsch_stream0_modulation_1, lte_pdsch_traffic_to_pilot_ratio_1,lte_pdsch_stream1_transport_block_size_bits_1,
                        lte_pdsch_stream1_modulation_1
                        FROM lte_pdsch_meas
                        %s
                        ORDER BY time DESC
                        LIMIT 1""" % (condition)
        query = QSqlQuery()
        query.exec_(queryString)
        rowCount = query.record().count()
        if rowCount > 0:

            while query.next():
                for field in range(len(pdschFields)):
                    if query.value(field):
                        dataList.append(
                            [pdschFields[field],
                             query.value(field)])
                    else:
                        dataList.append([pdschFields[field], ''])
        self.closeConnection()
        return dataList

    def getRlc(self):
        if azenqosDatabase is not None:
            azenqosDatabase.open()

        dataList = []
        condition = ""
        maxBearers = 8

        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)

        queryString = """SELECT time, lte_rlc_dl_tp_mbps, lte_rlc_dl_tp, lte_rlc_n_bearers
                        FROM lte_rlc_stats
                        %s
                        ORDER BY time DESC
                        LIMIT 1""" % (condition)
        query = QSqlQuery()
        query.exec_(queryString)
        while query.next():
            dataList.append(['Time', self.timeFilter, '', '', ''])
            dataList.append(
                ['DL TP(Mbps)',
                 query.value('lte_rlc_dl_tp_mbps'), '', '', ''])
            dataList.append(
                ['DL TP(Kbps)',
                 query.value('lte_rlc_dl_tp'), '', '', ''])
            dataList.append(['Bearers:', '', '', '', ''])
            dataList.append(
                ['N Bearers',
                 query.value('lte_rlc_n_bearers'), '', '', ''])
        for bearer in range(1, maxBearers):
            queryString = """SELECT lte_rlc_per_rb_dl_rb_mode_%d, lte_rlc_per_rb_dl_rb_type_%d, lte_rlc_per_rb_dl_rb_id_%d, lte_rlc_per_rb_cfg_index_%d,
                            lte_rlc_per_rb_dl_tp_%d
                            FROM lte_rlc_stats
                            %s
                            ORDER BY time DESC
                            LIMIT 1""" % (bearer, bearer, bearer, bearer,
                                          bearer, condition)
            query = QSqlQuery()
            query.exec_(queryString)
            rowCount = query.record().count()
            if rowCount > 0:
                while query.next():
                    if query.value(0):
                        if bearer == 1:
                            dataList.append(
                                ['Mode', 'Type', 'RB-ID', 'Index', 'TP Mbps'])
                        dataList.append([
                            query.value(0),
                            query.value(1),
                            query.value(2),
                            query.value(3),
                            query.value(4)
                        ])
        azenqosDatabase.close()
        return dataList

    def getVolte(self):
        self.openConnection()
        dataList = []
        condition = ""
        volteFields = [
            'Time', 'Codec:', 'AMR SpeechCodec-RX', 'AMR SpeechCodec-TX',
            'Delay interval avg:', 'Audio Packet delay (ms.)',
            'RTP Packet delay (ms.)', 'RTCP SR Params:',
            'RTCP Round trip time (ms.)', 'RTCP SR Params - Jitter DL:',
            'RTCP SR Jitter DL (ts unit)', 'RTCP SR Jitter DL (ms.)',
            'RTCP SR Params - Jitter UL:', 'RTCP SR Jitter UL (ts unit)',
            'RTCP SR Jitter UL (ms.)', 'RTCP SR Params - Packet loss rate:',
            'RTCP SR Packet loss DL (%)', 'RTCP SR Packet loss UL (%)'
        ]

        if self.timeFilter:
            condition = "WHERE lvs.time <= '%s'" % (self.timeFilter)

        queryString = """SELECT lvs.time, '' as codec, vi.gsm_speechcodecrx, vi.gsm_speechcodectx, '' as delay_interval,
                        vi.vocoder_amr_audio_packet_delay_avg, lvs.lte_volte_rtp_pkt_delay_avg, '' as rtcp_sr_params,
                        lvs.lte_volte_rtp_round_trip_time, '' as rtcp_jitter_dl, lvs.lte_volte_rtp_jitter_dl,
                        lvs.lte_volte_rtp_jitter_dl_millis, '' as rtcp_jitter_ul, lte_volte_rtp_jitter_ul, lte_volte_rtp_jitter_ul_millis,
                        '' as rtcp_sr_packet_loss, lte_volte_rtp_packet_loss_rate_dl, lte_volte_rtp_packet_loss_rate_ul
                        FROM lte_volte_stats as lvs
                        LEFT JOIN vocoder_info vi ON lvs.time = vi.time
                        %s
                        ORDER BY lvs.time DESC
                        LIMIT 1""" % (condition)
        query = QSqlQuery()
        query.exec_(queryString)
        rowCount = query.record().count()
        if rowCount > 0:
            while query.next():
                for field in range(len(volteFields)):
                    if field == 0:
                        dataList.append([volteFields[field], self.timeFilter])
                    else:
                        if query.value(field):
                            dataList.append(
                                [volteFields[field],
                                 query.value(field)])
                        else:
                            dataList.append([volteFields[field], ''])
            if len(dataList) == 0:
                for field in range(len(volteFields)):
                    if field == 0:
                        dataList.append([volteFields[field], self.timeFilter])
                    else:
                        dataList.append([volteFields[field], ''])
        self.closeConnection()
        return dataList

    def openConnection(self):
      if self.azenqosDatabase is not None:
            self.azenqosDatabase.open()

    def closeConnection(self):
      self.azenqosDatabase.close()