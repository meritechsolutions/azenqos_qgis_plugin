from PyQt5.QtSql import QSqlQuery, QSqlDatabase


class GsmDataQuery:
    def __init__(self, database, currentDateTimeString):
        self.timeFilter = ""
        self.azenqosDatabase = database
        if currentDateTimeString:
            self.timeFilter = currentDateTimeString

    def getRadioParameters(self):
        self.openConnection()
        dataList = []
        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)
            dataList.append(["Time", self.timeFilter, ""])
        gcmFieldList = ["RxLev", "RxQual"]
        gcmQueryString = (
            """SELECT gsm_rxlev_full_dbm || ' ' || gsm_rxlev_sub_dbm as "RxLev", gsm_rxqual_full || ' ' || gsm_rxqual_sub as "RxQual" FROM gsm_cell_meas %s ORDER BY time DESC LIMIT 1"""
            % (condition)
        )
        gcmQuery = QSqlQuery()
        queryStatus = gcmQuery.exec_(gcmQueryString)
        if queryStatus:
            hasData = gcmQuery.first()
            if hasData:
                for field in gcmFieldList:
                    fullValue = ""
                    subValue = ""
                    if field in ["RxLev", "RxQual"]:
                        if gcmQuery.value(field):
                            splitValue = gcmQuery.value(field).split(" ")
                            fullValue = splitValue[0] or ""
                            subValue = splitValue[1] or ""
                    dataList.append([field, fullValue, subValue])
            else:
                for field in gcmFieldList:
                    fullValue = ""
                    subValue = ""
                    dataList.append([field, fullValue, subValue])

        elementDictList = [
            {"element": "TA", "table": "gsm_tx_meas", "column": 'gsm_ta as "TA"'},
            {
                "element": "RLT (Max)",
                "table": "gsm_rl_timeout_counter",
                "column": 'gsm_radiolinktimeout_max as "RLT (Max)"',
            },
            {
                "element": "RLT (Current)",
                "table": "gsm_rlt_counter",
                "column": 'gsm_radiolinktimeout_current as "RLT (Current)"',
            },
            {
                "element": "DTX Used",
                "table": "gsm_rr_measrep_params",
                "column": 'gsm_dtxused as "DTX Used"',
            },
            {
                "element": "TxPower",
                "table": "gsm_tx_meas",
                "column": 'gsm_txpower as "TxPower"',
            },
            {"element": "FER", "table": "vocoder_info", "column": 'gsm_fer as "FER"'},
        ]
        for dic in elementDictList:
            element = dic["element"]
            column = dic["column"]
            table = dic["table"]
            if element and column and table:
                queryString = """SELECT %s
                                FROM %s
                                %s
                                ORDER BY time DESC
                                LIMIT 1""" % (
                    column,
                    table,
                    condition,
                )
                query = QSqlQuery()
                queryStatus = query.exec_(queryString)
                if queryStatus:
                    hasData = query.first()
                    value = ""
                    if query.value(element):
                        value = query.value(element)
                    dataList.append([element, value, ""])
        self.closeConnection()
        return dataList

    def getServingAndNeighbors(self):
        self.openConnection()
        dataList = []
        fieldsList = [
            "Time",
            "Cellname",
            "LAC",
            "BSIC",
            "ARFCN",
            "RxLev",
            "C1",
            "C2",
            "C31",
            "C32",
        ]
        selectedColumns = "gcm.time, gcm.gsm_cellfile_matched_cellname, gsci.gsm_lac, gcm.gsm_bsic, gcm.gsm_arfcn_bcch, gcm.gsm_rxlev_full_dbm, gcm.gsm_c1, gcm.gsm_c2, gcm.gsm_c31, gcm.gsm_c32"
        condition = ""
        if self.timeFilter:
            condition = "WHERE gcm.time <= '%s'" % (self.timeFilter)
        queryString = """ SELECT %s
                        FROM gsm_cell_meas gcm
                        LEFT JOIN gsm_serv_cell_info gsci ON gcm.time = gsci.time
                        %s
                        ORDER BY gcm.time DESC
                        LIMIT 1
                        """ % (
            selectedColumns,
            condition,
        )
        query = QSqlQuery()
        queryStatus = query.exec_(queryString)
        if queryStatus:
            query.first()
            rowData = []
            for x in range(len(fieldsList)):
                if query.value(x):
                    rowData.append(query.value(x))
                else:
                    rowData.append("")
            dataList.append(rowData)
        self.closeConnection()
        return dataList

    def getCurrentChannel(self):
        self.openConnection()

        dataList = []
        condition = ""
        gsmFields = [
            {
                "element": "Cellname",
                "column": 'gsm_cellfile_matched_cellname as "Cellname"',
                "table": "gsm_cell_meas",
            },
            {"element": "CGI", "column": 'gsm_cgi as "CGI"', "table": "gsm_cell_meas"},
            {
                "element": "Channel type",
                "column": 'gsm_channeltype as "Channel type"',
                "table": "gsm_rr_chan_desc",
            },
            {
                "element": "Sub channel number",
                "column": 'gsm_subchannelnumber as "Sub channel number"',
                "table": "gsm_rr_subchan",
            },
            {
                "element": "Mobile Allocation Index Offset (MAIO)",
                "column": 'gsm_maio as "Mobile Allocation Index Offset (MAIO)"',
                "table": "gsm_rr_chan_desc",
            },
            {
                "element": "Hopping Sequence Number (HSN)",
                "column": 'gsm_hsn as "Hopping Sequence Number (HSN)"',
                "table": "gsm_rr_chan_desc",
            },
            {
                "element": "Cipering Algorithm",
                "column": 'gsm_cipheringalgorithm as "Cipering Algorithm"',
                "table": "gsm_rr_cipher_alg",
            },
            {
                "element": "MS Power Control Level",
                "column": 'gsm_ms_powercontrollevel as "MS Power Control Level"',
                "table": "gsm_rr_power_ctrl",
            },
            {
                "element": "Channel Mode",
                "column": 'gsm_channelmode as "Channel Mode"',
                "table": "gsm_chan_mode",
            },
            {
                "element": "Speech Codec TX",
                "column": 'gsm_speechcodectx as "Speech Codec TX"',
                "table": "vocoder_info",
            },
            {
                "element": "Speech Codec RX",
                "column": 'gsm_speechcodecrx as "Speech Codec RX"',
                "table": "vocoder_info",
            },
            {
                "element": "Hopping Channel",
                "column": 'gsm_hoppingchannel as "Hopping Channel"',
                "table": "gsm_rr_chan_desc",
            },
            {
                "element": "Hopping Frequencies",
                "column": 'gsm_hoppingfrequencies as "Hopping Frequencies"',
                "table": "gsm_hopping_list",
            },
            {
                "element": "ARFCN BCCH",
                "column": 'gsm_arfcn_bcch as "ARFCN BCCH"',
                "table": "gsm_cell_meas",
            },
            {
                "element": "ARFCN TCH",
                "column": 'gsm_arfcn_tch as "ARFCN TCH"',
                "table": "gsm_rr_chan_desc",
            },
            {
                "element": "Time slot",
                "column": 'gsm_timeslot as "Time slot"',
                "table": "gsm_rr_chan_desc",
            },
        ]

        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)
            dateString = "%s" % (self.timeFilter)

        dataList.append(["Time", self.timeFilter])
        for dic in gsmFields:
            element = dic["element"]
            column = dic["column"]
            table = dic["table"]
            if element and column and table:
                queryString = """ SELECT %s
                                FROM %s
                                %s
                                ORDER BY time DESC
                                LIMIT 1 """ % (
                    column,
                    table,
                    condition,
                )
                query = QSqlQuery()
                queryStatus = query.exec_(queryString)
                if queryStatus:
                    firstRow = query.first()
                    value = query.value(element) or ""
                    dataList.append([element, value])

        self.closeConnection()
        return dataList

    def getCSlashI(self):
        self.openConnection()
        dataList = []
        condition = ""
        maxUnits = 10

        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)
        dataList.append([self.timeFilter, "", ""])
        queryString = """SELECT gsm_coi_avg, gsm_coi_worst
                        FROM gsm_coi_per_chan
                        %s
                        ORDER BY time DESC
                        LIMIT 1""" % (
            condition
        )
        query = QSqlQuery()
        query.exec_(queryString)
        while query.next():

            dataList.append(["Worst", query.value("gsm_coi_worst"), ""])
            dataList.append(["Avg", query.value("gsm_coi_avg"), ""])

        for unit in range(1, maxUnits):
            column = "gsm_coi_arfcn_%s, gsm_coi_%s" % (unit, unit)
            queryString = """SELECT %s
                            FROM gsm_coi_per_chan
                            %s
                            ORDER BY time DESC
                            LIMIT 1""" % (
                column,
                condition,
            )
            query = QSqlQuery()
            queryStatus = query.exec_(queryString)
            if queryStatus:
                firstRow = query.first()
                if query.value(0) or query.value(1):
                    dataList.append(
                        ["", query.value(0) or "", query.value(1) or "",]
                    )
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
