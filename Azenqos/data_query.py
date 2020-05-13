from PyQt5.QtSql import QSqlQuery, QSqlDatabase


class DataQuery:
    def __init__(self, database, currentDateTimeString):
        self.timeFilter = ""
        self.azenqosDatabase = database
        if currentDateTimeString:
            self.timeFilter = currentDateTimeString

    def getGprsEdgeInformation(self):
        self.openConnection()
        dataList = []
        elementList = [
            "Time",
            "GPRS Attach Duration",
            "PDP Context Activation Duration",
            "RLC DL Throughput (kbit/s)",
            "RLC UL Throughput (kbit/s)",
            "DL Coding Scheme",
            "UL Coding Scheme",
            "DL Timeslot Used",
            "Ul Timeslot Used",
            "GPRS C/I",
        ]

        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)

        query = QSqlQuery()
        queryString = """SELECT udas.time, udas.data_gprs_attach_duration, udas.data_pdp_context_activation_duration,
                        des.data_gsm_rlc_ul_throughput, des.data_gsm_rlc_dl_throughput,
                        des.data_egprs_dl_coding_scheme_index, des.data_egprs_ul_coding_scheme_index,
                        des.data_gprs_timeslot_used_dl, des.data_gprs_timeslot_used_ul,
                        des.data_gprs_ci
                        FROM umts_data_activation_stats udas
                        LEFT JOIN data_egprs_stats des ON udas.time = des.time
                        %s
                        ORDER BY time DESC
                        LIMIT 1""" % (
            condition
        )
        query.exec_(queryString)
        while query.next():
            for field in range(len(elementList)):
                if query.value(field):
                    dataList.append([elementList[field], query.value(field)])
                else:
                    dataList.append([elementList[field], ""])
        self.closeConnection()
        return dataList

    def getHsdpaHspaStatistics(self):
        self.openConnection()
        dataList = []
        elementList = [
            "Time",
            "HSDPA Scheduled Rate",
            "HSDPA Served Rate",
            "HS-DSCH Throughput",
            "HSDPA SBLER on 1st transmission",
            "HSDPA SBLER",
            "HSDPA CQI number avg.",
            "Data HSPAP CQI B",
            "Data HSPAP CQI A",
            "Data HSPAP CQI DC Primary Carrier",
            "Data HSPAP CQI DC Secondary Carrier",
            "HSDPA Num Codes Used Avg.",
            "HSDPA MOD QPSK Percent",
            "HSDPA MOD 16QAM Percent",
            "HSDPA MOD 64QAM Percent",
            "HSDPA Meas from num 2MS slots",
            "HSDPA Num SCCH DEMOD Attempts",
            "HSDPA Num DEMOD Valid",
            "Data HSPAP Dual Carrier Enabled",
            "Data HSPAP 64QAM Configured",
            "Data_HSPAP_DUAL_CARRIER_ENABLED_PERCENT",
            "Data_HSPAP_MIMO_ENABLED",
            "Data_HSPAP_UE_CATEGORY",
            "Data_HSPAP_2TB_REQUESTED_PERCENT",
            "Data_HSPAP_1TB_REQUESTED_PERCENT",
            "HSDPA HS-SCCH Usage Percent",
            "WCDMA RLC DL Throughput",
        ]

        if self.timeFilter:
            condition = "WHERE whs.time <= '%s'" % (self.timeFilter)

        query = QSqlQuery()
        queryString = """SELECT whs.time, whs.data_hsdpa_scheduled_rate, whs.data_hsdpa_served_rate,
                        whs.data_hsdpa_thoughput, whs.data_hsdpa_sbler_on_1st_transmission,whs.data_hsdpa_sbler,
                        whc.data_hsdpa_cqi_number_avg, whc.data_hspap_cqi_b, whc.data_hspap_cqi_a,
                        whc.data_hspap_cqi_dc_primary_carrier, whc.data_hspap_cqi_dc_secondary_carrier,
                        whs.data_hsdpa_num_codes_used_avg, whs.data_hsdpa_mod_qpsk_percent, whs.data_hsdpa_mod_16qam_percent,
                        whs.data_hspap_mod_64qam_percent, whs.data_hsdpa_meas_from_num_2ms_slots,
                        whs.data_hsdpa_num_scch_demod_attempts, whs.data_hsdpa_num_demod_valid,
                        whs.data_hspap_dual_carrier_enabled, whs.data_hspap_64qam_configured,
                        whs.data_hspap_dual_carrier_enabled_percent, whs.data_hspap_mimo_enabled,
                        whs.data_hspap_ue_category, whs.data_hspap_2tb_requested_percent,
                        whs.data_hspap_1tb_requested_percent, whs.data_hsdpa_hs_scch_usage_percent,
                        dwrs.data_wcdma_rlc_dl_throughput
                        FROM wcdma_hsdpa_stats whs
                        LEFT JOIN wcdma_hsdpa_cqi whc ON whs.time = whc.time
                        LEFT JOIN data_wcdma_rlc_stats dwrs ON whs.time = dwrs.time
                        %s
                        ORDER BY whs.time DESC
                        LIMIT 1""" % (
            condition
        )
        query.exec_(queryString)
        while query.next():
            for field in range(len(elementList)):
                if query.value(field):
                    dataList.append([elementList[field], query.value(field)])
                else:
                    dataList.append([elementList[field], ""])
        self.closeConnection()
        return dataList

    def getHsupaStatistics(self):
        self.openConnection()
        dataList = []
        elementList = [
            "Time",
            "HSUPA Sample duration",
            "HSUPA TTI",
            "HSUPA Sample frames",
            "HSUPA Happy bit TTIs (%)",
            "HSUPA Serving RGCH Up (%)",
            "HSUPA Serving RGCH Down (%)",
            "HSUPA Serving RGCH Hold (%)",
            "HSUPA NonServing RGCH Down (%)",
            "HSUPA NonServing RGCH Hold (%)",
            "HSUPA N AGCH Receive success",
            "HSUPA Average AGCH",
            "HSUPA Average SGI",
            "HSUPA new transmission (%)",
            "HSUPA retransmission (%)",
            "HSUPA DTX (%)",
            "HSUPA N NACK after max retrans",
            "HSUPA N MAC e Resets",
            "HSUPA Power Limited TTIs (%)",
            "HSUPA Serving Grant Limited TTIs (%)",
            "HSUPA SBLER (%)",
            "HSUPA Avg Raw Throughput",
            "HSUPA Avg Scheduled Throughput",
            "HSUPA Total E DPDCH Throughput",
            "WCDMA RLC UL Throughput",
        ]

        if self.timeFilter:
            condition = "WHERE whs.time <= '%s'" % (self.timeFilter)

        query = QSqlQuery()
        queryString = """SELECT whs.time, whs.data_hsupa_sample_duration, whs.data_hsupa_tti,
                        whs.data_hsupa_sample_frames, whs.data_hsupa_p_happy_bit_ttis,whs.data_hsupa_p_serving_rgch_up,
                        whs.data_hsupa_p_serving_rgch_down, whs.data_hsupa_p_serving_rgch_hold, whc.data_hsupa_p_nonserving_rgch_down,
                        whs.data_hsupa_p_nonserving_rgch_hold, whs.data_hsupa_n_agch_receive_success,
                        whs.data_hsupa_average_agch, whs.data_hsupa_average_sgi, whs.data_hsupa_p_new_transmission,
                        whs.data_hsupa_p_retransmission, whs.data_hsupa_p_dtx,
                        whs.data_hsupa_n_nack_after_max_retrans, whs.data_hsupa_n_mac_e_resets,
                        whs.data_hsupa_n_power_limited_ttis, whs.data_hsupa_n_serving_grant_limited_ttis,
                        whs.data_hsupa_p_sbler, whs.data_hsupa_avg_raw_throughput,
                        whs.data_hsupa_avg_scheduled_throughput, whs.data_hsupa_total_e_dpdch_throughput,
                        dwrs.data_wcdma_rlc_ul_throughput
                        FROM wcdma_hsupa_stats whs
                        LEFT JOIN data_wcdma_rlc_stats dwrs ON whs.time = dwrs.time
                        %s
                        ORDER BY whs.time DESC
                        LIMIT 1""" % (
            condition
        )
        query.exec_(queryString)
        while query.next():
            for field in range(len(elementList)):
                if query.value(field):
                    dataList.append([elementList[field], query.value(field)])
                else:
                    dataList.append([elementList[field], ""])
        self.closeConnection()
        return dataList

    def getLteDataStatistics(self):
        self.openConnection()
        dataList = []
        elementList = [
            "Time",
            "RRC State",
            "L1 DL TP Combined (Mbps)",
            "L1 UL TP Combined (Mbps)",
            "RLC Throughput (Mbps)",
        ]

        if self.timeFilter:
            condition = "WHERE lrrs.time <= '%s'" % (self.timeFilter)

        query = QSqlQuery()
        queryString = """SELECT "", lrrs.lte_rrc_state, lldt.lte_l1_dl_throughput_all_carriers_mbps,
                        llut.lte_l1_ul_throughput_all_carriers_mbps, lrs.lte_rlc_dl_tp_mbps
                        FROM lte_rrc_state lrrs
                        LEFT JOIN lte_l1_dl_tp lldt ON lrrs.time = lldt.time
                        LEFT JOIN lte_l1_ul_tp llut ON lrrs.time = llut.time
                        LEFT JOIN lte_rlc_stats lrs ON lrrs.time = lrs.time
                        %s
                        ORDER BY lrrs.time DESC
                        LIMIT 1""" % (
            condition
        )
        query.exec_(queryString)
        while query.next():
            for field in range(len(elementList)):
                if query.value(field):
                    dataList.append([elementList[field], query.value(field), "", ""])
                else:
                    dataList.append([elementList[field], "", "", ""])

        # add PCC SCC0 SSC1
        dataList.append(["", "PCC", "SCC0", "SCC1"])

        elementDictList = [
            {
                "name": "L1 DL TP (Mbps)",
                "column": "lte_l1_dl_throughput_mbps_1, lte_l1_dl_throughput_mbps_2, lte_l1_dl_throughput_mbps_3",
                "table": "lte_l1_dl_tp",
            },
            {
                "name": "L1 UL TP (Mbps)",
                "column": "lte_l1_ul_throughput_mbps_1, lte_l1_ul_throughput_mbps_2, lte_l1_ul_throughput_mbps_3",
                "table": "lte_l1_ul_tp",
            },
            {
                "name": "TransMode Current",
                "column": "lte_pdsch_transmission_mode_current_1, lte_pdsch_transmission_mode_current_2, lte_pdsch_transmission_mode_current_3",
                "table": "lte_pdsch_meas",
            },
            {
                "name": "PCI",
                "column": "lte_pdsch_serving_cell_id_1, lte_pdsch_serving_cell_id_2, lte_pdsch_serving_cell_id_3",
                "table": "lte_l1_dl_tp",
            },
            {"name": "PDSCH Stats:", "column": "", "table": ""},
            {
                "name": "BLER",
                "column": "lte_bler_1, lte_bler_2, lte_bler_3",
                "table": "lte_l1_dl_tp",
            },
            {
                "name": "Serv N Tx Ant",
                "column": "lte_pdsch_serving_n_tx_antennas_1, lte_pdsch_serving_n_tx_antennas_2, lte_pdsch_serving_n_tx_antennas_3",
                "table": "lte_pdsch_meas",
            },
            {
                "name": "Serv N Rx Ant",
                "column": "lte_pdsch_serving_n_rx_antennas_1, lte_pdsch_serving_n_rx_antennas_2, lte_pdsch_serving_n_rx_antennas_3",
                "table": "lte_pdsch_meas",
            },
            {
                "name": "Spatial Rank",
                "column": "lte_pdsch_spatial_rank_1, lte_pdsch_spatial_rank_2, lte_pdsch_spatial_rank_3",
                "table": "lte_pdsch_meas",
            },
            {
                "name": "Rank Indicator",
                "column": "lte_rank_indicator_1, lte_rank_indicator_2, lte_rank_indicator_3",
                "table": "lte_cqi",
            },
            {
                "name": "CQI CW0",
                "column": "lte_cqi_cw0_1, lte_cqi_cw0_2, lte_cqi_cw0_3",
                "table": "lte_cqi",
            },
            {
                "name": "CQI CW1",
                "column": "lte_cqi_cw1_1, lte_cqi_cw1_2, lte_cqi_cw1_3",
                "table": "lte_cqi",
            },
            {
                "name": "PRB Alloc",
                "column": "lte_pdsch_n_rb_allocated_latest_1, lte_pdsch_n_rb_allocated_latest_2, lte_pdsch_n_rb_allocated_latest_3",
                "table": "lte_pdsch_meas",
            },
            {
                "name": "PRB Max",
                "column": "lte_mib_max_n_rb_1, lte_mib_max_n_rb_2, lte_mib_max_n_rb_3",
                "table": "lte_mib_info",
            },
            {
                "name": "PRB Util %",
                "column": "lte_prb_alloc_in_bandwidth_percent_latest_1, lte_prb_alloc_in_bandwidth_percent_latest_2, lte_prb_alloc_in_bandwidth_percent_latest_3",
                "table": "lte_pdsch_meas",
            },
            {
                "name": "DL Bandwidth (MHz)",
                "column": "lte_mib_dl_bandwidth_mhz_1, lte_mib_dl_bandwidth_mhz_2, lte_mib_dl_bandwidth_mhz_3",
                "table": "lte_mib_info",
            },
            {
                "name": "PCC UL Bw (Mhz)",
                "column": "lte_sib2_ul_bandwidth_mhz",
                "table": "lte_sib2_info",
            },
            {
                "name": "Time Scheduled %",
                "column": "lte_pdsch_sched_percent_1, lte_pdsch_sched_percent_2, lte_pdsch_sched_percent_3",
                "table": "lte_l1_dl_tp",
            },
            {
                "name": "MCS Index",
                "column": "lte_mcs_index_1, lte_mcs_index_2, lte_mcs_index_3",
                "table": "lte_l1_dl_tp",
            },
            {
                "name": "BlockSizeBits[0]",
                "column": "lte_pdsch_stream0_transport_block_size_bits_1, lte_pdsch_stream0_transport_block_size_bits_2, lte_pdsch_stream0_transport_block_size_bits_3",
                "table": "lte_pdsch_meas",
            },
            {
                "name": "Modulation[0]",
                "column": "lte_pdsch_stream0_modulation_1, lte_pdsch_stream0_modulation_2, lte_pdsch_stream0_modulation_3",
                "table": "lte_pdsch_meas",
            },
            {
                "name": "BlockSizeBits[1]",
                "column": "lte_pdsch_stream1_transport_block_size_bits_1, lte_pdsch_stream1_transport_block_size_bits_2, lte_pdsch_stream1_transport_block_size_bits_3",
                "table": "lte_pdsch_meas",
            },
            {
                "name": "Modulation[1]",
                "column": "lte_pdsch_stream1_modulation_1, lte_pdsch_stream1_modulation_2, lte_pdsch_stream1_modulation_3",
                "table": "lte_pdsch_meas",
            },
            {
                "name": "TrafficToPilot Ratio",
                "column": "lte_pdsch_traffic_to_pilot_ratio_1, lte_pdsch_traffic_to_pilot_ratio_2, lte_pdsch_traffic_to_pilot_ratio_3",
                "table": "lte_pdsch_meas",
            },
            {
                "name": "RNTI Type",
                "column": "lte_pdsch_rnti_type_1, lte_pdsch_rnti_type_2, lte_pdsch_rnti_type_3",
                "table": "lte_pdsch_meas",
            },
            {
                "name": "RNTI ID",
                "column": "lte_pdsch_rnti_id_1, lte_pdsch_rnti_id_2, lte_pdsch_rnti_id_3",
                "table": "lte_pdsch_meas",
            },
            {
                "name": "PMI Type",
                "column": "lte_pdsch_pmi_type_1, lte_pdsch_pmi_type_2, lte_pdsch_pmi_type_3",
                "table": "lte_pdsch_meas",
            },
            {
                "name": "PMI Index",
                "column": "lte_pdsch_pmi_index_1, lte_pdsch_pmi_index_2, lte_pdsch_pmi_index_3",
                "table": "lte_pdsch_meas",
            },
        ]
        # "name": "","column": "","table": ""
        for dic in elementDictList:
            name = dic["name"]
            column = dic["column"]
            table = dic["table"]
            query = QSqlQuery()
            if column != "" and table != "":
                queryString = """SELECT %s
                            FROM %s
                            %s
                            ORDER BY lrrs.time DESC
                            LIMIT 1""" % (
                    column,
                    table,
                    condition,
                )
                query.exec_(queryString)
                while query.next():
                    dataList.append(
                        [name, query.value(0), query.value(1), query.value(2)]
                    )
                else:
                    dataList.append([name, "", "", ""])
            else:
                dataList.append([name, "", "", ""])

        self.closeConnection()
        return dataList

    def getGprsEdgeInformation(self):
        self.openConnection()
        dataList = []
        elementList = [
            "Time",
            "GPRS Attach Duration",
            "PDP Context Activation Duration",
            "RLC DL Throughput (kbit/s)",
            "RLC UL Throughput (kbit/s)",
            "DL Coding Scheme",
            "UL Coding Scheme",
            "DL Timeslot Used",
            "Ul Timeslot Used",
            "GPRS C/I",
        ]

        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)

        query = QSqlQuery()
        queryString = """SELECT udas.time, udas.data_gprs_attach_duration, udas.data_pdp_context_activation_duration,
                        des.data_gsm_rlc_ul_throughput, des.data_gsm_rlc_dl_throughput,
                        des.data_egprs_dl_coding_scheme_index, des.data_egprs_ul_coding_scheme_index,
                        des.data_gprs_timeslot_used_dl, des.data_gprs_timeslot_used_ul,
                        des.data_gprs_ci
                        FROM umts_data_activation_stats udas
                        LEFT JOIN data_egprs_stats des ON udas.time = des.time
                        %s
                        ORDER BY time DESC
                        LIMIT 1""" % (
            condition
        )
        query.exec_(queryString)
        while query.next():
            for field in range(len(elementList)):
                if query.value(field):
                    dataList.append([elementList[field], query.value(field)])
                else:
                    dataList.append([elementList[field], ""])
        self.closeConnection()
        return dataList

    def getWifiActive(self):
        self.openConnection()
        dataList = []
        elementList = [
            "Time",
            "BSSID",
            "SSID",
            "RSSI",
            "IP Addr",
            "Link Speed (Mbps.)",
            "MAC Addr",
            "Encryption",
            "Ch.",
            "Freq",
            "ISP",
        ]

        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)

        query = QSqlQuery()
        queryString = """SELECT wifi_active_bssid, wifi_active_ssid, wifi_active_rssi, wifi_active_ipaddr, wifi_active_linkspeed,
                        wifi_active_macaddr, wifi_active_encryption, wifi_active_channel, wifi_active_freq, wifi_active_isp
                        FROM wifi_active
                        %s
                        ORDER BY time DESC
                        LIMIT 1""" % (
            condition
        )
        query.exec_(queryString)
        while query.next():
            for field in range(len(elementList)):
                if field == 0:
                    dataList.append([elementList[field], self.timeFilter])
                else:
                    dataList.append([elementList[field], query.value(field)])
        self.closeConnection()
        return dataList

    def getWifiScanned(self):
        self.openConnection()
        dataList = []
        maxUnits = 50

        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)

        for unit in range(maxUnits):
            unitNo = unit + 1
            column = (
                "time, wifi_scanned_bssid_%d, wifi_scanned_ssid_%d, wifi_scanned_freq_%d, wifi_scanned_channel_%d, wifi_scanned_level_%d, wifi_scanned_encryption_%d"
                % (unitNo, unitNo, unitNo, unitNo, unitNo, unitNo)
            )
            query = QSqlQuery()
            queryString = """SELECT %s
                            FROM wifi_scanned
                            %s
                            ORDER BY time DESC
                            LIMIT 1""" % (
                column,
                condition,
            )
            query.exec_(queryString)
            while query.next():
                # data = []
                # columnCount = query.record().count()
                # for column in columnCount:
                #     data.append(query.value(column))
                dataList.append(
                    [
                        query.value(0),
                        query.value(1),
                        query.value(2),
                        query.value(3),
                        query.value(4),
                        query.value(5),
                        query.value(6),
                    ]
                )
            else:
                dataList.append(["", "", "", "", "", "", ""])
        self.closeConnection()
        return dataList

    def openConnection(self):
        if self.azenqosDatabase is not None:
            self.azenqosDatabase.open()

    def closeConnection(self):
        self.azenqosDatabase.close()

    def defaultData(self, fieldsList):
        fieldCount = len(fieldsList)
        if fieldCount > 0:
            dataList = []
            for index in range(fieldCount):
                columnName = fieldsList[index]
                value = ""
                dataList.append([columnName, value, "", ""])
            return dataList
