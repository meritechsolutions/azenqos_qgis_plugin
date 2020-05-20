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
        gcmQueryString = """SELECT gsm_rxlev_full_dbm || ' ' || gsm_rxlev_sub_dbm as "RxLev",  gsm_rxqual_full || ' ' || gsm_rxqual_sub as "RxQual"
                        FROM gsm_cell_meas
                        %s
                        ORDER BY time DESC LIMIT 1""" % (
            condition
        )
        gcmQuery = QSqlQuery()
        gcmQuery.exec_(gcmQueryString)
        while gcmQuery.next():
            for field in gcmFieldList:
                fullValue = ""
                subValue = ""
                if field in ["RxLev", "RxQual"]:
                    splitValue = str(gcmQuery.value(field)).split(" ")
                    fullValue = splitValue[0] or ""
                    subValue = splitValue[1] or ""
                else:
                    fullValue = gcmQuery.value(field) or ""
                dataList.append([field, fullValue, subValue])
        if gcmQuery.size() == -1:
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
                query.exec_(queryString)
                while query.next():
                    dataList.append([element, query.value(element), ""])
                if query.size() == -1:
                    dataList.append([element, "", ""])

        # fieldsList = [
        #     "TA",
        #     "RLT (Max)",
        #     "RLT (Current)",
        #     "DTX Used",
        #     "TxPower",
        #     "FER",
        # ]

        # selectedColumns = """gtm.gsm_ta, grtc.gsm_radiolinktimeout_max,
        #                     grc.gsm_radiolinktimeout_current, grmp.gsm_dtxused, gtm.gsm_txpower, vi.gsm_fer"""
        # queryString = """SELECT %s
        #                 FROM gsm_cell_meas gcm
        #                 LEFT JOIN gsm_rlt_counter grc ON gcm.time = grc.time
        #                 LEFT JOIN gsm_rl_timeout_counter grtc ON gcm.time = grtc.time
        #                 LEFT JOIN gsm_tx_meas gtm ON gcm.time = gtm.time
        #                 LEFT JOIN gsm_rr_measrep_params grmp ON gcm.time = grmp.time
        #                 LEFT JOIN vocoder_info vi ON gcm.time = vi.time
        #                 %s
        #                 ORDER BY gcm.time DESC LIMIT 1""" % (
        #     selectedColumns,
        #     condition,
        # )
        # query = QSqlQuery()
        # query.exec_(queryString)
        # fieldCount = len(selectedColumns.split(","))
        # while query.next():
        #     for index in range(fieldCount):
        #         columnName = fieldsList[index]
        #         fullValue = query.value(index) or ""
        #         subValue = ""
        #         if columnName in ["RxLev", "RxQual"]:
        #             if query.value(index):
        #                 splitValue = query.value(index).split(" ")
        #                 fullValue = splitValue[0] or ""
        #                 subValue = splitValue[1] or ""
        #         dataList.append([columnName, fullValue, subValue])
        # else:
        #     if len(dataList) == 0:
        #         for index in range(fieldCount):
        #             columnName = fieldsList[index]
        #             fullValue = ""
        #             subValue = ""
        #             dataList.append([columnName, fullValue, subValue])
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
        query.exec_(queryString)
        while query.next():
            for x in range(len(fieldsList)):
                if query.value(x):
                    dataList.append(query.value(x))
                else:
                    dataList.append("")
        self.closeConnection()
        return dataList

    def getCurrentChannel(self):
        self.openConnection()

        dataList = []
        condition = ""
        gsmFields = [
            "Cellname",
            "CGI",
            "Channel type",
            "Sub channel number",
            "Mobile Allocation Index Offset (MAIO)",
            "Hopping Sequence Number (HSN)",
            "Cipering Algorithm",
            "MS Power Control Level",
            "Channel Mode",
            "Speech Codec TX",
            "Speech Codec RX",
            "Hopping Channel",
            "Hopping Frequencies",
            "ARFCN BCCH",
            "ARFCN TCH",
            "Time slot",
        ]

        if self.timeFilter:
            condition = "WHERE gcm.time <= '%s'" % (self.timeFilter)
            dateString = "%s" % (self.timeFilter)

        dataList.append(["Time", self.timeFilter])

        queryString = """SELECT gcm.gsm_cellfile_matched_cellname, gcm.gsm_cgi, grcd.gsm_channeltype, grs.gsm_subchannelnumber,
                        grcd.gsm_maio, grcd.gsm_hsn, grca.gsm_cipheringalgorithm, grpc.gsm_ms_powercontrollevel, gchm.gsm_channelmode,
                        vi.gsm_speechcodectx, vi.gsm_speechcodecrx, grcd.gsm_hoppingchannel, ghl.gsm_hoppingfrequencies, gcm.gsm_arfcn_bcch,
                        grcd.gsm_arfcn_tch
                        FROM gsm_cell_meas gcm
                        INNER JOIN gsm_rr_chan_desc grcd ON gcm.time = grcd.time
                        INNER JOIN gsm_rr_subchan grs ON grs.time = gcm.time
                        INNER JOIN gsm_rr_cipher_alg grca ON grca.time = gcm.time
                        INNER JOIN gsm_rr_power_ctrl grpc ON grpc.time = gcm.time
                        INNER JOIN gsm_chan_mode gchm ON gchm.time = gcm.time
                        INNER JOIN vocoder_info vi ON vi.time = gcm.time
                        INNER JOIN gsm_hopping_list ghl ON ghl.time = gcm.time
                        %s
                        ORDER BY time DESC
                        LIMIT 1""" % (
            condition
        )
        query = QSqlQuery()
        query.exec_(queryString)
        while query.next():
            for field in range(len(gsmFields)):
                if query.value(field):
                    dataList.append([gsmFields[field], query.value(field)])
                else:
                    dataList.append([gsmFields[field], ""])
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
            queryString = """SELECT gsm_coi_arfcn_%d, gsm_coi_%d
                            FROM gsm_coi_per_chan
                            %s
                            ORDER BY time DESC
                            LIMIT 1""" % (
                unit,
                unit,
                condition,
            )
            query = QSqlQuery()
            query.exec_(queryString)
            rowCount = query.record().count()
            if rowCount > 0:
                while query.next():
                    if query.value(0):
                        dataList.append(
                            [
                                "",
                                query.value("gsm_coi_arfcn_" + str(unit)),
                                query.value("gsm_coi_" + str(unit)),
                            ]
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
