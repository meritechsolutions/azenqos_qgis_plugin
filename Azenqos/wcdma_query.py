from PyQt5.QtSql import QSqlQuery, QSqlDatabase


class WcdmaDataQuery:
    def __init__(self, database, currentDateTimeString):
        self.timeFilter = ""
        self.azenqosDatabase = database
        if currentDateTimeString:
            self.timeFilter = currentDateTimeString

    def getActiveMonitoredSets(self):
        self.openConnection()
        dataList = []
        maxUnits = 27
        condition = ""
        if self.timeFilter:
            condition = "WHERE wcc.time <= '%s'" % (self.timeFilter)
        for unit in range(maxUnits):
            unitNo = unit + 1
            selectedColumns = (
                "wcc.wcdma_cellfile_matched_cellname_%d, wcc.wcdma_celltype_%d, wcc.wcdma_sc_%d, wcc.wcdma_ecio_%d, wcc.wcdma_rscp_%d, wcc.wcdma_cellfreq_%d, wcc.wcdma_cellfreq_%d, wrme.wcdma_prevmeasevent"
                % (unitNo, unitNo, unitNo, unitNo, unitNo, unitNo, unitNo)
            )
            queryString = """SELECT %s FROM wcdma_cells_combined wcc
                            INNER JOIN wcdma_rrc_meas_events wrme ON wcc.time = wrme.time
                            %s ORDER BY wcc.time DESC
                            LIMIT 1""" % (
                selectedColumns,
                condition,
            )
            query = QSqlQuery()
            query.exec_(queryString)
            while query.next():
                nameValue = query.value(0)
                typeValue = query.value(1)
                scValue = query.value(2)
                ecioValue = query.value(3)
                rscpValue = query.value(4)
                freqValue = query.value(5)
                eventValue = query.value(6)
                if unitNo == 1:
                    dataList.append(
                        [
                            self.timeFilter,
                            nameValue,
                            typeValue,
                            scValue,
                            ecioValue,
                            rscpValue,
                            freqValue,
                            eventValue,
                        ]
                    )
                else:
                    dataList.append(
                        [
                            "",
                            nameValue,
                            typeValue,
                            scValue,
                            ecioValue,
                            rscpValue,
                            freqValue,
                            eventValue,
                        ]
                    )
            else:
                if unitNo == 1 and len(dataList) == 0:
                    dataList.append([self.timeFilter, "", "", "", "", "", "", ""])
        self.closeConnection()
        return dataList

    def getRadioParameters(self):
        self.openConnection()
        dataList = []
        fieldsList = [
            "Time",
            "Tx Power",
            "Max Tx Power",
            "RSSI",
            "SIR",
            "RRC State",
            "Speech Codec TX" "Speech Codec RX" "Cell ID",
            "RNC ID",
        ]
        selectedColumns = """wtp.time,wtp.wcdma_txagc,wtp.wcdma_maxtxpwr,wrp.wcdma_rssi,sir.wcdma_sir,
                            rrc.wcdma_rrc_state,vi.gsm_speechcodectx,vi.gsm_speechcodecrx,ai.android_cellid,ai.android_rnc_id"""
        condition = ""
        if self.timeFilter:
            condition = "WHERE wtp.time <= '%s'" % (self.timeFilter)

        queryString = """SELECT %s
                        FROM wcdma_tx_power wtp
                        LEFT JOIN wcdma_rx_power wrp ON wtp.time = wrp.time
                        LEFT JOIN wcdma_sir sir ON wtp.time = sir.time
                        LEFT JOIN wcdma_rrc_state rrc ON wtp.time = rrc.time
                        LEFT JOIN android_info_1sec ai ON wtp.time = ai.time
                        LEFT JOIN vocoder_info vi ON wtp.time = vi.time
                        %s
                        ORDER BY wtp.time DESC LIMIT 1""" % (
            selectedColumns,
            condition,
        )

        query = QSqlQuery()
        query.exec_(queryString)
        while query.next():
            for field in range(len(fieldsList)):
                if field == 0:
                    dataList.append([fieldsList[field], self.timeFilter])
                else:
                    if query.value(field):
                        dataList.append([fieldsList[field], query.value(field)])
                    else:
                        dataList.append([fieldsList[field], ""])
        else:
            if len(dataList) == 0:
                for field in range(len(fieldsList)):
                    if field == 0:
                        dataList.append([fieldsList[field], self.timeFilter])
                    else:
                        dataList.append([fieldsList[field], ""])
        self.closeConnection()
        return dataList

    def getActiveSetList(self):
        self.openConnection()
        dataList = []
        condition = ""
        maxUnits = 3
        if self.timeFilter:
            condition = "WHERE wcm.time <= '%s'" % (self.timeFilter)
        for unit in range(maxUnits):
            unitNo = unit + 1
            selectedColumns = """wcm.time,wcm.wcdma_aset_cellfreq_%d,wafl.wcdma_activeset_psc_%d,
                                wafl.wcdma_activeset_cellposition_%d,wafl.wcdma_activeset_celltpc_%d,
                                wafl.wcdma_activeset_diversity_%d""" % (
                unitNo,
                unitNo,
                unitNo,
                unitNo,
                unitNo,
            )
            queryString = """SELECT %s
                            FROM wcdma_cell_meas wcm
                            LEFT JOIN wcdma_aset_full_list wafl ON wcm.time = wafl.time
                            %s
                            ORDER BY wcm.time DESC LIMIT 1""" % (
                selectedColumns,
                condition,
            )
            query = QSqlQuery()
            query.exec_(queryString)
            while query.next():
                freqValue = query.value(0)
                pscValue = query.value(1)
                celposValue = query.value(2)
                tpcValue = query.value(3)
                diverValue = query.value(4)
                if unitNo == 1:
                    dataList.append(
                        [
                            self.timeFilter,
                            freqValue,
                            pscValue,
                            celposValue,
                            tpcValue,
                            diverValue,
                        ]
                    )
                else:
                    dataList.append(
                        ["", freqValue, pscValue, celposValue, tpcValue, diverValue]
                    )
            else:
                if len(dataList) == 0:
                    if unitNo == 1:
                        dataList.append([self.timeFilter, "", "", "", "", ""])
        self.closeConnection()
        return dataList

    def getMonitoredSetList(self):
        self.openConnection()
        dataList = []
        condition = ""
        maxUnits = 32
        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)

        for unit in range(maxUnits):
            unitNo = unit + 1
            selectedColumns = (
                """time,wcdma_neighborset_downlinkfreq_%d,wcdma_neighborset_psc_%d,wcdma_neighborset_cellposition_%d,wcdma_neighborset_diversity_%d"""
                % (unitNo, unitNo, unitNo, unitNo)
            )
            queryString = (
                """SELECT %s FROM wcdma_nset_full_list %s ORDER BY time DESC LIMIT 1"""
                % (selectedColumns, condition,)
            )
            query = QSqlQuery()
            query.exec_(queryString)
            while query.next():
                freqValue = query.value(1)
                pscValue = query.value(2)
                celposValue = query.value(3)
                diverValue = query.value(4)
                if unitNo == 1:
                    dataList.append(
                        [self.timeFilter, freqValue, pscValue, celposValue, diverValue]
                    )
                else:
                    dataList.append(["", freqValue, pscValue, celposValue, diverValue])
            else:
                if len(dataList) == 0:
                    dataList.append([self.timeFilter, "", "", "", "", ""])

        self.closeConnection()
        return dataList

    def getBlerSummary(self):
        self.openConnection()
        dataList = []
        fieldsList = [
            "Time",
            "BLER Average Percent",
            "BLER Calculation Window Size",
            "BLER N Transport Channels",
        ]
        condition = ""
        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)

        queryString = """Select time,wcdma_bler_average_percent_all_channels,wcdma_bler_calculation_window_size,
                        wcdma_bler_n_transport_channels
                        FROM wcdma_bler
                        %s
                        ORDER BY time DESC LIMIT 1""" % (
            condition
        )
        query = QSqlQuery()
        query.exec_(queryString)
        while query.next():
            dataList.append(["Time", self.timeFilter])
            blerAvg = query.value(1)
            blerCalWindowSize = query.value(2)
            blerNTransportChannels = query.value(3)
            for field in range(1, len(fieldsList)):
                dataList.append([fieldsList[field], query.value(field)])
        else:
            if len(dataList) == 0:
                dataList.append(["Time", self.timeFilter])
                for field in range(1, len(fieldsList)):
                    dataList.append([fieldsList[field], ""])
        self.closeConnection()
        return dataList

    def getBLER_TransportChannel(self):
        self.openConnection()
        dataList = []
        condition = ""
        maxChannel = 16

        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)
        for channel in range(maxChannel):
            channelNo = channel + 1
            queryString = """SELECT wcdma_bler_channel_%d,wcdma_bler_percent_%d,
                            wcdma_bler_err_%d,wcdma_bler_rcvd_%d
                            FROM wcdma_bler
                            %s
                            ORDER BY time DESC LIMIT 1""" % (
                channelNo,
                channelNo,
                channelNo,
                channelNo,
                condition,
            )
            query = QSqlQuery()
            query.exec_(queryString)
            while query.next():
                dataList.append(
                    [query.value(0), query.value(1), query.value(2), query.value(3)]
                )
            else:
                if len(dataList) == 0:
                    dataList.append(["", "", "", ""])

        self.closeConnection()
        return dataList

    def getBearers(self):
        self.openConnection()
        dataList = []
        condition = ""
        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)

        maxBearers = 10
        for bearers in range(1, maxBearers):
            bearerNo = bearers + 1
            queryString = """SELECT data_wcdma_n_bearers,data_wcdma_bearer_id_%d,data_wcdma_bearer_rate_dl_%d,
                             data_wcdma_bearer_rate_ul_%d
                             FROM wcdma_bearers %s
                             ORDER BY time DESC LIMIT 1""" % (
                bearerNo,
                bearerNo,
                bearerNo,
                condition,
            )

            query = QSqlQuery()
            query.exec_(queryString)
            while query.next():
                row = ["", "", "", ""]
                if bearerNo == 1:
                    row[0] = query.value(0)
                for index in range(1, len(row)):
                    row[index] = query.value(index)
                dataList.append(row)
            else:
                if len(dataList) == 0:
                    dataList.append(["", "", "", ""])
        self.closeConnection()
        return dataList

    def getPilotPolutingCells(self):
        self.openConnection()
        dataList = []
        condition = ""
        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)
        maxPollution = 32
        for pollution in range(maxPollution):
            pollutionNo = pollution + 1
            queryString = """SELECT time,wcdma_n_pilot_polluting_cells,wcdma_pilot_polluting_cell_sc_%d,
                             wcdma_pilot_polluting_cell_rscp_%d,wcdma_pilot_polluting_cell_ecio_%d
                             FROM wcdma_pilot_pollution
                             %s
                             ORDER BY time DESC LIMIT 1""" % (
                pollution,
                pollution,
                pollution,
                condition,
            )

            query = QSqlQuery()
            query.exec_(queryString)
            while query.next():
                row = ["", "", "", "", ""]
                if pollutionNo == 1:
                    row[0] = query.value(0)
                    row[1] = query.value(1)
                for index in range(2, len(row)):
                    row[index] = query.value(index)
                dataList.append(row)

        self.closeConnection()
        return dataList

    def getActiveMonitoredBar(self):
        self.openConnection()
        dataList = []
        condition = ""
        maxItem = 27

        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)

        for item in range(maxItem):
            itemNo = item + 1
            queryString = """SELECT wcdma_celltype_%d,wcdma_ecio_%d,wcdma_rscp_%d
                            FROM wcdma_cells_combined
                            %s
                            ORDER BY time DESC""" % (
                itemNo,
                itemNo,
                itemNo,
                condition,
            )
            query = QSqlQuery()
            query.exec_(queryString)
            while query.next():
                dataList.append([query.value(0), query.value(1), query.value(2)])
            else:
                if len(dataList) == 0:
                    dataList.append(["", "", ""])

        self.closeConnection()
        return dataList

    def getCmGsmCells(self):
        self.openConnection()
        dataList = []
        condition = ""

        queryString = """Select time,wcdma_cm_gsm_meas_arfcn,wcdma_cm_gsm_meas_rxlev,
                        wcdma_cm_gsm_meas_bsic,wcdma_cm_gsm_meas_cell_measure_state
                        FROM wcdma_cm_gsm_meas
                        %s
                        ORDER BY time DESC LIMIT 1""" % (
            condition
        )

        query = QSqlQuery()
        query.exec_(queryString)
        while query.next():
            dataList.append(
                [
                    query.value(0),
                    query.value(1),
                    query.value(2),
                    query.value(3),
                    query.value(4),
                ]
            )
        else:
            dataList.append([self.timeFilter, "", "", "", ""])
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
