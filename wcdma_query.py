from PyQt5.QtSql import QSqlQuery, QSqlDatabase

class WcdmaDataQuery:
    def __init__(self, database, currentDateTimeString):
        self.timeFilter = ''
        self.azenqosDatabase = database
        if currentDateTimeString:
            self.timeFilter = currentDateTimeString

    def getActiveMonitoredSets(self):
        self.openConnection()
        dataList = []
        condition = ''
        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)
        selectedColumns = """time,wcdma_cellfile_matched_cellname_1,
                             wcdma_celltype_1,wcdma_sc_1,wcdma_ecio_1,wcdma_rscp_1,
	                           wcdma_cellfreq_1"""
        #ขาด Column Event
        queryString = """SELECT %s FROM wcdma_cells_combined %s ORDER BY time""" % (
            selectedColumns, condition)
        query = QSqlQuery()
        query.exec_(queryString)

        # Real Query Code (รันไม่ได้เพราะ no data in DB)
        #-----------------------------------------------
        # while query.next():
        #     timeValue = query.value(0)
        #     nameValue = query.value(1)
        #     typeValue = query.value(2)
        #     scValue = query.value(3)
        #     ecioValue = query.value(4)
        #     rscpValue = query.value(5)
        #     freqValue = query.value(6)
        #     #eventValue = query.value(eventField)
        #     dataList.append([timeValue, nameValue, typeValue, scValue, ecioValue, rscpValue,''])

        #Table Ui Test
        dataList.append([self.timeFilter, '', '', '', '', '', '', ''])
        self.closeConnection()
        return dataList

    def getRadioParameters(self):
        self.openConnection()
        dataList = []
        fieldsList = [
            'Time', 'Tx Power', 'Max Tx Power', 'RSSI', 'SIR', 'RRC State',
            'Cell ID', 'RNC ID'
        ]
        selectedColumns = """wtp.time,wtp.wcdma_txagc,wtp.wcdma_maxtxpwr,wrp.wcdma_rssi,sir.wcdma_sir,
                            rrc.wcdma_rrc_state,cel.wcdma_cellid,cel.wcdma_rnc_id"""
        condition = ''
        if self.timeFilter:
            condition = "WHERE wtp.time <= '%s'" % (self.timeFilter)
        queryString = """SELECT %s
                        FROM wcdma_tx_power wtp
                        LEFT JOIN wcdma_rx_power wrp ON wtp.time = wrp.time
                        LEFT JOIN wcdma_sir sir ON wtp.time = sir.time
                        LEFT JOIN wcdma_rrc_state rrc ON wtp.time = rrc.time
                        LEFT JOIN wcdma_idle_cell_info cel ON wtp.time = cel.time
                        %s
                        ORDER BY wtp.time DESC LIMIT 1""" % (selectedColumns,
                                                             condition)

        # Real Query Code (รันไม่ได้เพราะ no data in DB)
        #-----------------------------------------------
        # query = QSqlQuery()
        # query.exec_(queryString)
        # while query.next():
        #     for field in range(len(fieldsList)):
        #         if query.value(fieldsList):
        #             dataList.append([fieldsList[field],query.value(field)])
        #         else:
        #             dataList.append([fieldsList[field],''])

        #Table Ui Test
        dataList.append(['Time', self.timeFilter])
        for field in range(1, len(fieldsList)):
            dataList.append([fieldsList[field], ''])
        self.closeConnection()
        return dataList

    def getMonitoredSetList(self):
        self.openConnection()
        dataList = []
        condition = ''
        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)

        selectedColumns = """time,wcdma_mset_cellfreq_1,wcdma_mset_sc_1"""
        #ขาด Column Cell Position และ Diversity
        queryString = """SELECT %s FROM wcdma_cell_meas %s ORDER BY time""" % (
            selectedColumns, condition)

        # Real Query Code (รันไม่ได้เพราะ no data in DB)
        #-----------------------------------------------
        # query = QSqlQuery()
        # query.exec_(queryString)
        # while query.next():
        #     timeValue = query.value(0)
        #     freqValue = query.value(1)
        #     pscValue = query.value(2)
        #     # celposValue = query.value(3)
        #     # diverValue = query.value(4)
        #     dataList.append([timeValue,freqValue,pscValue,'',''])

        #Table Ui Test
        dataList.append([self.timeFilter, '', '', '', '', ''])

        self.closeConnection()
        return dataList

    def getActiveSetList(self):
        self.openConnection()
        dataList = []
        condition = ''
        if self.timeFilter:
            condition = "WHERE wcm.time <= '%s'" % (self.timeFilter)

        selectedColumns = """wcm.time,wcm.wcdma_aset_cellfreq_1,wafl.wcdma_activeset_psc_1,
                            wafl.wcdma_activeset_cellposition_1,wafl.wcdma_activeset_celltpc_1,
                            wafl.wcdma_activeset_diversity_1"""
        queryString = """SELECT %s
                        FROM wcdma_cell_meas wcm
                        LEFT JOIN wcdma_aset_full_list wafl ON wcm.time = wafl.time
                        %s
                        ORDER BY wcm.time DESC""" % (selectedColumns,
                                                     condition)

        # Real Query Code (รันไม่ได้เพราะ no data in DB)
        #-----------------------------------------------
        # query = QSqlQuery()
        # query.exec_(queryString)
        # while query.next():
        #     timeValue = query.value(0)
        #     freqValue = query.value(1)
        #     pscValue = query.value(2)
        #     celposValue = query.value(3)
        #     tpcValue = query.value(4)
        #     diverValue = query.value(5)
        #     dataList.append([timeValue,freqValue,pscValue,celposValue,tpcValue,diverValue])

        #Table Ui Test
        dataList.append([self.timeFilter, '', '', '', '', ''])

        self.closeConnection()
        return dataList

    def getBlerSummary(self):
        self.openConnection()
        dataList = []
        fieldsList = [
            'Time', 'BLER Average Percent', 'BLER Calculation Window Size',
            'BLER N Transport Channels'
        ]
        condition = ''
        if self.timeFilter:
            condition = "WHERE wcm.time <= '%s'" % (self.timeFilter)

        queryString = """Select time,wcdma_bler_average_percent_all_channels,wcdma_bler_calculation_window_size,
                        wcdma_bler_n_transport_channels
                        FROM wcdma_bler
                        %s
                        ORDER BY time DESC LIMIT 1""" % (condition)

        # Real Query Code (รันไม่ได้เพราะ no data in DB)
        #-----------------------------------------------
        # query = QSqlQuery()
        # query.exec_(queryString)
        # while query.next():
        #     for field in range(len(fieldsList)):
        #         if query.value(fieldsList):
        #             dataList.append([fieldsList[field],query.value(field)])
        #         else:
        #             dataList.append([fieldsList[field],''])

        #Table Ui Test
        dataList.append(['Time', self.timeFilter])
        for field in range(1, len(fieldsList)):
            dataList.append([fieldsList[field], ''])
        self.closeConnection()
        return dataList

    def getBLER_TransportChannel(self):
        self.openConnection()
        dataList = []
        condition = ''
        maxChannel = 16

        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)
        for channel in range(1, maxChannel):
            queryString = """SELECT wcdma_bler_channel_%d,wcdma_bler_percent_%d,
                            wcdma_bler_err_%d,wcdma_bler_rcvd_%d
                            FROM wcdma_bler
                            %s
                            ORDER BY time DESC LIMIT 1""" % (
                channel, channel, channel, channel, condition)
            query = QSqlQuery()
            query.exec_(queryString)
            rowCount = query.record().count()
            if rowCount > 0:
                while query.next():
                    if query.value(0):
                        dataList.append([
                            query.value(0),
                            query.value(1),
                            query.value(2),
                            query.value(3)
                        ])
        self.closeConnection()
        return dataList

    def getBearers(self):
        self.openConnection()
        dataList = []
        condition = ''
        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)
        row = ['', '', '', '']
        maxBearers = 10
        for bearers in range(1, maxBearers):
            queryString = """SELECT data_wcdma_n_bearers,data_wcdma_bearer_id_%d,data_wcdma_bearer_rate_dl_%d,
                             data_wcdma_bearer_rate_ul_%d
                             FROM wcdma_bearers %s
                             ORDER BY time DESC LIMIT 1""" % (
                bearers, bearers, bearers, condition)

            query = QSqlQuery()
            query.exec_(queryString)
            rowCount = query.record().count()
            if rowCount > 0:
                while query.next():
                    if query.value(0):
                        row[0] = query.value(0)
                        for index in range(1, len(row)):
                            row[index] = query.value(index)
                        dataList.append(row)
        self.closeConnection()
        return dataList

    def getPilotPolutingCells(self):
        self.openConnection()
        dataList = []
        condition = ''
        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)
        row = ['', '', '', '', '']
        maxPollution = 32
        for pollution in range(1, maxPollution):
            queryString = """SELECT time,wcdma_n_pilot_polluting_cells,wcdma_pilot_polluting_cell_sc_%d,
                             wcdma_pilot_polluting_cell_rscp_%d,wcdma_pilot_polluting_cell_ecio_%d
                             FROM wcdma_pilot_pollution
                             %s
                             ORDER BY time DESC LIMIT 1""" % (
                pollution, pollution, pollution, condition)

            query = QSqlQuery()
            query.exec_(queryString)
            rowCount = query.record().count()
            if rowCount > 0:
                while query.next():
                    if query.value(0):
                        #row[0] = query.value(0)
                        row[0] = self.timeFilter
                        row[1] = query.value(1)
                        for index in range(2, len(row)):
                            row[index] = query.value(index)
                        dataList.append(row)

        self.closeConnection()
        return dataList

    def getActiveMonitoredBar(self):
        self.openConnection()
        dataList = []
        condition = ''
        maxItem = 27

        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)

        for item in range(1, maxItem):
            queryString = """SELECT wcdma_celltype_%d,wcdma_ecio_%d,wcdma_rscp_%d
                            FROM wcdma_cells_combined
                            %s
                            ORDER BY time DESC""" % (item, item, item,
                                                     condition)
            query = QSqlQuery()
            query.exec_(queryString)
            rowCount = query.record().count()
            if rowCount > 0:
                while query.next():
                    if query.value(0):
                        dataList.append(
                            [query.value(0),
                             query.value(1),
                             query.value(2)])

        self.closeConnection()
        return dataList

    def getCmGsmCells(self):
        self.openConnection()
        dataList = []
        condition = ''

        queryString = """Select time,wcdma_cm_gsm_meas_arfcn,wcdma_cm_gsm_meas_rxlev,
                        wcdma_cm_gsm_meas_bsic,wcdma_cm_gsm_meas_cell_measure_state
                        FROM wcdma_cm_gsm_meas
                        %s
                        ORDER BY time DESC""" % (condition)

        # Real Query Code (รันไม่ได้เพราะ no data in DB)
        # -----------------------------------------------
        # query = QSqlQuery()
        # query.exec_(queryString)
        # while query.next():
        #     if query.value(0):
        #         dataList.append([query.value(0),
        #                           query.value(1),
        #                           query.value(2),
        #                           query.value(3),
        #                           query.value(4)])
        #     else:
        #         dataList.append([self.timeFilter,'','','',''])

        #Table Ui Test
        dataList.append([self.timeFilter, '', '', '', ''])
        self.closeConnection()
        return dataList

    def openConnection(self):
      if self.azenqosDatabase is not None:
            self.azenqosDatabase.open()

    def closeConnection(self):
      self.azenqosDatabase.close()