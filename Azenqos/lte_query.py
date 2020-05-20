from PyQt5.QtSql import QSqlQuery, QSqlDatabase


class LteDataQuery:
    def __init__(self, database, currentDateTimeString):
        self.timeFilter = ""
        self.azenqosDatabase = database
        if currentDateTimeString:
            self.timeFilter = currentDateTimeString

    def getRadioParameters(self):
        self.openConnection()
        dataList = []
        condition = ""
        # add Time for first row
        if self.timeFilter:
            dataList.append(["Time", self.timeFilter, "", ""])
            condition = "WHERE time <= '%s'" % (self.timeFilter)
        elementDictList = [
            {
                "name": "Band",
                "column": "lte_band_1,lte_band_2,lte_band_3",
                "table": "lte_cell_meas",
            },
            {
                "name": "E-ARFCN",
                "column": "lte_earfcn_1,lte_earfcn_2,lte_earfcn_3",
                "table": "lte_cell_meas",
            },
            {
                "name": "Serving PCI",
                "column": "lte_physical_cell_id_1,lte_physical_cell_id_2,lte_physical_cell_id_3",
                "table": "lte_cell_meas",
            },
            {
                "name": "Serving RSRP[0]",
                "column": "lte_inst_rsrp_rx0_1,lte_inst_rsrp_rx0_2,lte_inst_rsrp_rx0_3",
                "table": "lte_cell_meas",
            },
            {
                "name": "Serving RSRP[1]",
                "column": "lte_inst_rsrp_rx1_1,lte_inst_rsrp_rx1_2,lte_inst_rsrp_rx1_3",
                "table": "lte_cell_meas",
            },
            {
                "name": "Serving RSRP",
                "column": "lte_inst_rsrp_1,lte_inst_rsrp_2,lte_inst_rsrp_3",
                "table": "lte_cell_meas",
            },
            {
                "name": "Serving RSRQ[0]",
                "column": "lte_inst_rsrq_rx0_1,lte_inst_rsrq_rx0_2,lte_inst_rsrq_rx0_3",
                "table": "lte_cell_meas",
            },
            {
                "name": "Serving RSRQ[1]",
                "column": "lte_inst_rsrq_rx1_1,lte_inst_rsrq_rx1_2,lte_inst_rsrq_rx1_3",
                "table": "lte_cell_meas",
            },
            {
                "name": "Serving RSRQ",
                "column": "lte_inst_rsrq_1,lte_inst_rsrq_2,lte_inst_rsrq_3",
                "table": "lte_cell_meas",
            },
            {
                "name": "SINR Rx[0]",
                "column": "lte_sinr_rx0_1,lte_sinr_rx0_2,lte_sinr_rx0_3",
                "table": "lte_cell_meas",
            },
            {
                "name": "SINR Rx[1]",
                "column": "lte_sinr_rx1_1,lte_sinr_rx1_2,lte_sinr_rx1_3",
                "table": "lte_cell_meas",
            },
            {
                "name": "SINR",
                "column": "lte_sinr_1,lte_sinr_2,lte_sinr_3",
                "table": "lte_cell_meas",
            },
            {
                "name": "RSSI Rx[0]",
                "column": "lte_inst_rssi_rx0_1,lte_inst_rssi_rx0_2,lte_inst_rssi_rx0_3",
                "table": "lte_cell_meas",
            },
            {
                "name": "RSSI Rx[1]",
                "column": "lte_inst_rssi_rx1_1,lte_inst_rssi_rx1_2,lte_inst_rssi_rx1_3",
                "table": "lte_cell_meas",
            },
            {
                "name": "RSSI",
                "column": "lte_inst_rssi_1,lte_inst_rssi_2,lte_inst_rssi_3",
                "table": "lte_cell_meas",
            },
            {
                "name": "BLER",
                "column": "lte_bler_1,lte_bler_2,lte_bler_3",
                "table": "lte_l1_dl_tp",
            },
            {
                "name": "CQI CW[0]",
                "column": "lte_cqi_cw0_1,lte_cqi_cw0_2,lte_cqi_cw0_3",
                "table": "lte_cqi",
            },
            {
                "name": "CQI CW[1]",
                "column": "lte_cqi_cw1_1,lte_cqi_cw1_2,lte_cqi_cw1_3",
                "table": "lte_cqi",
            },
        ]
        for dic in elementDictList:
            name = dic["name"]
            column = dic["column"]
            table = dic["table"]
            query = QSqlQuery()
            if column != "" and table != "":
                queryString = """SELECT %s
                            FROM %s
                            %s
                            ORDER BY time DESC
                            LIMIT 1""" % (
                    column,
                    table,
                    condition,
                )
                query.exec_(queryString)
                while query.next():
                    dataList.append(
                        [
                            name,
                            query.value(0) or "",
                            query.value(1) or "",
                            query.value(2) or "",
                        ]
                    )

        fieldsList = [
            "Tx Power",
            "PUCCH TxPower (dBm)",
            "PUSCH TxPower (dBm)",
            "TimingAdvance",
            "Transmission Mode (RRC-tm)",
            "LTE RRC State",
            "LTE EMM State",
            "LTE RRC Substate",
            "Modern ServCellInfo",
            "Allowed Access",
            "MCC",
            "MNC",
            "TAC",
            "Cell ID (ECI)",
            "eNodeB ID",
            "LCI",
            "PCI",
            "Derived SCC ECI",
            "Derived SCC eNodeB ID",
            "Derived SCC LCI",
            "DL EARFCN",
            "UL EARFCN",
            "DL Bandwidth (Mhz)",
            "UL Bandwidth (Mhz)",
            "SCC DL Bandwidth (Mhz)",
            "SIB1 info:",
            "sib1 MCC",
            "sib1 MNC",
            "sib1 TAC",
            "sib1 ECI",
            "sib1 eNBid",
            "sib1 LCI",
            "TDD Config:",
            "SubframeAssignment",
            "SpclSubframePattern",
            "DedBearer QCI",
        ]

        queryString = """SELECT ltp.lte_tx_power AS 'Tx Power', lpcti.lte_pucch_tx_power AS 'PUCCH TxPower (dBm)', lpsti.lte_pusch_tx_power AS 'PUSCH TxPower (dBm)',
                                lft.lte_ta AS 'TimingAdvance', lrti.lte_transmission_mode_l3 AS 'Transmission Mode (RRC-tm)', lrs.lte_rrc_state AS 'LTE RRC State',
                                les.lte_emm_state AS 'LTE EMM State', les.lte_emm_substate AS 'LTE EMM Substate', '____' AS 'Modem ServCellInfo',
                                lsci.lte_serv_cell_info_allowed_access AS 'Allowed Access', lsci.lte_serv_cell_info_mcc AS 'MCC', lsci.lte_serv_cell_info_mnc AS 'MNC',
                                lsci.lte_serv_cell_info_tac AS 'TAC', lsci.lte_serv_cell_info_eci AS 'Cell ID (ECI)', lsci.lte_serv_cell_info_enb_id AS 'eNodeB ID', lsci.lte_scc_derived_lci AS 'LCI',
                                lsci.lte_serv_cell_info_pci AS 'PCI', lsci.lte_scc_derived_eci AS 'Derviced SCC ECI', lsci.lte_scc_derived_enb_id AS 'Derived SCC eNodeB ID',
                                lsci.lte_scc_derived_lci AS 'Derived SCC LCI', lsci.lte_serv_cell_info_dl_freq AS 'DL EARFCN', lsci.lte_serv_cell_info_ul_freq AS 'UL EARFCN',
                                lsci.lte_serv_cell_info_dl_bandwidth_mhz AS 'DL Bandwidth (Mhz)', lsci.lte_serv_cell_info_ul_bandwidth_mhz AS 'UL Bandwidth (Mhz)', lsci.lte_scc_dl_bandwidth_1 AS 'SCC DL Bandwidth (Mhz)',
                                '____' AS 'SIB1 info:', lsoi.lte_sib1_mcc AS 'sib1 MCC', lsoi.lte_sib1_mnc AS 'sib1 MNC', lsoi.lte_sib1_tac AS 'sib1 TAC', lsoi.lte_sib1_eci AS 'sib ECI',
                                lsoi.lte_sib1_enb_id AS 'sib1 eNBid', lsoi.lte_sib1_local_cell_id AS 'sib1 LCI', '____' AS 'TDD Config:', ltc.lte_tdd_config_subframe_assignment AS 'SubframeAssignment',
                                ltc.lte_tdd_config_special_subframe_pattern AS 'SpclSubframePattern', ad.lte_ded_eps_bearer_qci AS 'DedBearer QCI'
                        FROM (SELECT lte_tx_power FROM lte_tx_power WHERE time <= '%s'  ORDER BY time DESC LIMIT 1) AS ltp,
                        (SELECT * FROM lte_serv_cell_info WHERE time <= '%s'  ORDER BY time DESC LIMIT 1) AS lsci,
                        (SELECT lte_pucch_tx_power FROM lte_pucch_tx_info WHERE time <= '%s'  ORDER BY time DESC LIMIT 1) AS lpcti,
                        (SELECT lte_pusch_tx_power FROM lte_pusch_tx_info WHERE time <= '%s'  ORDER BY time DESC LIMIT 1) AS lpsti,
                        (SELECT lte_ta FROM lte_frame_timing WHERE time <= '%s'  ORDER BY time DESC LIMIT 1) AS lft,
                        (SELECT lte_transmission_mode_l3 FROM lte_rrc_transmode_info WHERE time <= '%s'  ORDER BY time DESC LIMIT 1) AS lrti,
                        (SELECT lte_rrc_state FROM lte_rrc_state WHERE time <= '%s'  ORDER BY time DESC LIMIT 1) AS lrs,
                        (SELECT lte_emm_state, lte_emm_substate FROM lte_emm_state WHERE time <= '%s'  ORDER BY time DESC LIMIT 1) AS les,
                        (SELECT * FROM lte_sib1_info WHERE time <= '%s'  ORDER BY time DESC LIMIT 1) AS lsoi,
                        (SELECT lte_tdd_config_subframe_assignment, lte_tdd_config_special_subframe_pattern FROM lte_tdd_config WHERE time <= '%s'  ORDER BY time DESC LIMIT 1) AS ltc,
                        (SELECT lte_ded_eps_bearer_qci FROM activate_dedicated_eps_bearer_context_request_params WHERE time <= '%s'  ORDER BY time DESC LIMIT 1) AS ad""" % (
            self.timeFilter,
            self.timeFilter,
            self.timeFilter,
            self.timeFilter,
            self.timeFilter,
            self.timeFilter,
            self.timeFilter,
            self.timeFilter,
            self.timeFilter,
            self.timeFilter,
            self.timeFilter,
        )
        query = QSqlQuery()
        query.exec_(queryString)
        if query.first():
            for index in range(fieldsList):
                columnName = fieldsList[index]
                value = ""
                if query.value(index) != "":
                    value = query.value(index)
                dataList.append([columnName, value, "", ""])
        else:
            for index in range(fieldsList):
                columnName = fieldsList[index]
                value = ""
                dataList.append([columnName, value, "", ""])
        self.closeConnection()
        return dataList

    def getServingAndNeighbors(self):
        self.openConnection()
        MAX_NEIGHBORS = 16
        dataList = []
        typeHeader = {
            "serving": ["dateString", "Serving cell:", "", "", "", ""],
            "neigh": ["", "Neighbor cells:", "", "", "", ""],
        }
        emptyRow = ["", "", "", "", "", ""]
        condition = ""

        # Set query condition for serving cell
        if self.timeFilter:
            condition = "WHERE lcm.time <= '%s'" % (self.timeFilter)

        typeHeader["serving"][0] = self.timeFilter
        dataList.append(typeHeader["serving"])

        # queryString = """SELECT lcm.lte_earfcn_1, lsci.lte_serv_cell_info_band, lsci.lte_serv_cell_info_pci, lcm.lte_inst_rsrp_1,
        #                 lcm.lte_inst_rsrq_1
        #                 FROM lte_cell_meas AS lcm
        #                 LEFT JOIN lte_serv_cell_info lsci ON lcm.time = lsci.time
        #                 %s
        #                 ORDER BY lcm.time DESC
        #                 LIMIT 1""" % (
        #     condition
        # )
        queryString = """SELECT lcm.lte_earfcn_1, lsci.lte_serv_cell_info_band, lsci.lte_serv_cell_info_pci, lcm.lte_inst_rsrp_1,lcm.lte_inst_rsrq_1
                        FROM (SELECT lte_earfcn_1, lte_inst_rsrp_1, lte_inst_rsrq_1 FROM lte_cell_meas WHERE time <= '%s' ORDER BY time DESC LIMIT 1) lcm,
                        (SELECT lte_serv_cell_info_band,lte_serv_cell_info_pci FROM lte_serv_cell_info WHERE time <= '%s' ORDER BY time DESC LIMIT 1) lsci""" % (
            self.timeFilter,
            self.timeFilter,
        )
        query = QSqlQuery()
        query.exec_(queryString)
        if query.first():
            servingCell = [
                "",
                query.value(0) or "",
                query.value(1) or "",
                query.value(2) or "",
                query.value(3) or "",
                query.value(4) or "",
            ]
            dataList.append(servingCell)

        # Set query condition for neigh cell
        if self.timeFilter:
            condition = "WHERE lnm.time <= '%s'" % (self.timeFilter)

        for neighbor in range(1, MAX_NEIGHBORS):
            neighborNo = neighbor + 1
            queryString = """SELECT lnm.lte_neigh_earfcn_%d, lnm.lte_neigh_band_%d, lnm.lte_neigh_physical_cell_id_%d, lnm.lte_neigh_rsrp_%d,
                            lnm.lte_neigh_rsrq_%d
                            FROM lte_neigh_meas AS lnm
                            %s
                            ORDER BY lnm.time DESC
                            LIMIT 1""" % (
                neighborNo,
                neighborNo,
                neighborNo,
                neighborNo,
                neighborNo,
                condition,
            )
            query = QSqlQuery()
            query.exec_(queryString)
            if query.first():
                if query.value(0):
                    if neighborNo == 1:
                        dataList.append(typeHeader["neigh"])
                    neighCell = [
                        "",
                        query.value(0),
                        query.value(1),
                        query.value(2),
                        query.value(3),
                        query.value(4),
                    ]
                    dataList.append(neighCell)
                else:
                    break
        self.closeConnection()
        return dataList

    def getPucchPdschParameters(self):
        self.openConnection()

        dataList = []
        condition = ""
        maxBearers = 8
        pucchFields = [
            "---- PUCCH ----",
            "CQI CW 0",
            "CQI CW 1",
            "CQI N Sub-bands",
            "Rank Indicator",
        ]
        pdschFields = [
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
        ]

        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)
            dateString = "%s" % (self.timeFilter)

        dataList.append(["Time", self.timeFilter])

        queryString = """SELECT '' AS header, lte_cqi_cw0_1, lte_cqi_cw1_1, lte_cqi_n_subbands_1, lte_rank_indication_1
                        FROM lte_cqi
                        %s
                        ORDER BY time DESC
                        LIMIT 1""" % (
            condition
        )
        query = QSqlQuery()
        query.exec_(queryString)
        if query.first():
            for field in range(len(pucchFields)):
                dataList.append([pucchFields[field], query.value(field) or ""])

        queryString = """SELECT '' AS pdsch, lte_pdsch_serving_cell_id_1, lte_pdsch_rnti_id_1, lte_pdsch_rnti_type_1,
                        lte_pdsch_serving_n_tx_antennas_1, lte_pdsch_serving_n_rx_antennas_1,
                        lte_pdsch_transmission_mode_current_1, lte_pdsch_spatial_rank_1,
                        lte_pdsch_rb_allocation_slot0_1, lte_pdsch_rb_allocation_slot1_1,
                        lte_pdsch_pmi_type_1, lte_pdsch_pmi_index_1,lte_pdsch_stream0_transport_block_size_bits_1,
                        lte_pdsch_stream0_modulation_1, lte_pdsch_traffic_to_pilot_ratio_1,lte_pdsch_stream1_transport_block_size_bits_1,
                        lte_pdsch_stream1_modulation_1
                        FROM lte_pdsch_meas
                        %s
                        ORDER BY time DESC
                        LIMIT 1""" % (
            condition
        )
        query = QSqlQuery()
        query.exec_(queryString)
        if query.first():
            for field in range(len(pdschFields)):
                dataList.append([pdschFields[field], query.value(field) or ""])
        self.closeConnection()
        return dataList

    def getRlc(self):
        self.openConnection()

        dataList = []
        condition = ""
        maxBearers = 8

        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)
        dataList.append(["Time", self.timeFilter, "", "", ""])
        queryString = """SELECT time, lte_rlc_dl_tp_mbps, lte_rlc_dl_tp, lte_rlc_n_bearers
                        FROM lte_rlc_stats
                        %s
                        ORDER BY time DESC
                        LIMIT 1""" % (
            condition
        )
        query = QSqlQuery()
        query.exec_(queryString)
        if query.first():
            dataList.append(
                ["DL TP(Mbps)", query.value("lte_rlc_dl_tp_mbps") or "", "", "", ""]
            )
            dataList.append(["DL TP(Kbps)", query.value("lte_rlc_dl_tp") or "", "", "", ""])
            dataList.append(["Bearers:", "", "", "", ""])
            dataList.append(["N Bearers", query.value("lte_rlc_n_bearers") or "", "", "", ""])
        for bearer in range(1, maxBearers):
            bearerNo = bearer + 1
            queryString = """SELECT lte_rlc_per_rb_dl_rb_mode_%d, lte_rlc_per_rb_dl_rb_type_%d, lte_rlc_per_rb_dl_rb_id_%d, lte_rlc_per_rb_cfg_index_%d,
                            lte_rlc_per_rb_dl_tp_%d
                            FROM lte_rlc_stats
                            %s
                            ORDER BY time DESC
                            LIMIT 1""" % (
                bearerNo,
                bearerNo,
                bearerNo,
                bearerNo,
                bearerNo,
                condition,
            )
            query = QSqlQuery()
            query.exec_(queryString)
            while query.next():
                if bearerNo == 1:
                    dataList.append(["Mode", "Type", "RB-ID", "Index", "TP Mbps"])
                dataList.append(
                    [
                        query.value(0) or "",
                        query.value(1) or "",
                        query.value(2) or "",
                        query.value(3) or "",
                        query.value(4) or "",
                    ]
                )
        self.closeConnection()
        return dataList

    def getVolte(self):
        self.openConnection()
        dataList = []
        condition = ""
        volteFields = [
            "Time",
            "Codec:",
            "AMR SpeechCodec-RX",
            "AMR SpeechCodec-TX",
            "Delay interval avg:",
            "Audio Packet delay (ms.)",
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
        ]

        if self.timeFilter:
            condition = "WHERE lvs.time <= '%s'" % (self.timeFilter)

        queryString = """SELECT lvs.time, '' AS codec, vi.gsm_speechcodecrx, vi.gsm_speechcodectx, '' AS delay_interval,
                        vi.vocoder_amr_audio_packet_delay_avg, lvs.lte_volte_rtp_pkt_delay_avg, '' AS rtcp_sr_params,
                        lvs.lte_volte_rtp_round_trip_time, '' AS rtcp_jitter_dl, lvs.lte_volte_rtp_jitter_dl,
                        lvs.lte_volte_rtp_jitter_dl_millis, '' AS rtcp_jitter_ul, lte_volte_rtp_jitter_ul, lte_volte_rtp_jitter_ul_millis,
                        '' AS rtcp_sr_packet_loss, lte_volte_rtp_packet_loss_rate_dl, lte_volte_rtp_packet_loss_rate_ul
                        FROM lte_volte_stats AS lvs
                        LEFT JOIN vocoder_info vi ON lvs.time = vi.time
                        %s
                        ORDER BY lvs.time DESC
                        LIMIT 1""" % (
            condition
        )
        query = QSqlQuery()
        query.exec_(queryString)
        while query.next():
            for field in range(len(volteFields)):
                if field == 0:
                    dataList.append([volteFields[field], self.timeFilter])
                else:
                    if query.value(field):
                        dataList.append([volteFields[field], query.value(field)])
                    else:
                        dataList.append([volteFields[field], ""])
        if len(dataList) == 0:
            for field in range(len(volteFields)):
                if field == 0:
                    dataList.append([volteFields[field], self.timeFilter])
                else:
                    dataList.append([volteFields[field], ""])
        self.closeConnection()
        return dataList

    def defaultData(self, fieldsList, dataList):
        fieldCount = len(fieldsList)
        if fieldCount > 0:
            for index in range(fieldCount):
                columnName = fieldsList[index]
                dataList.append([columnName, "", "", ""])
            return dataList

    def openConnection(self):
        if self.azenqosDatabase is not None:
            self.azenqosDatabase.open()

    def closeConnection(self):
        self.azenqosDatabase.close()
