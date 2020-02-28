from PyQt5.QtSql import QSqlQuery, QSqlDatabase


class CdmaEvdoQuery:
    def __init__(self, database, currentDateTimeString):
        self.timeFilter = ""
        self.azenqosDatabase = database
        if currentDateTimeString:
            self.timeFilter = currentDateTimeString

    def getRadioParameters(self):
        self.openConnection()
        dataList = []
        cdmaFields = [
            "Time",
            "Active PN (Best)",
            "Ec/Io",
            "RX Power",
            "TX Power",
            "FER",
            "Channel",
            "Band class",
            "N Active Set Cells",
        ]

        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)

        query = QSqlQuery()
        queryString = """SELECT time, cdma_cell_pn, cdma_ecio, cdma_rx_power, cdma_tx_power, cdma_fer, cdma_channel, cdma_band_class, cdma_n_aset_cells                   FROM cdma
                        %s
                        ORDER BY time DESC
                        LIMIT 1""" % (
            condition
        )
        query.exec_(queryString)
        while query.next():
            for field in range(len(cdmaFields)):
                if query.value(field):
                    dataList.append([cdmaFields[field], query.value(field)])
                else:
                    dataList.append([cdmaFields[field], ""])
        self.closeConnection()
        return dataList

    def getServingAndNeighbors(self):
        self.openConnection()
        MAX_NEIGHBORS = 32
        dataList = []
        condition = ""

        # Set query condition for serving cell
        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)

        dataList.append([self.timeFilter, "", "", ""])

        for neighbor in range(1, MAX_NEIGHBORS):
            queryString = """SELECT cdma_cell_pn_%d, cdma_cell_ecio_%d, cdma_cell_type_%d
                            FROM cdma
                            %s
                            ORDER BY time DESC
                            LIMIT 1""" % (
                neighbor,
                neighbor,
                neighbor,
                condition,
            )
            query = QSqlQuery()
            query.exec_(queryString)
            rowCount = query.record().count()
            if rowCount > 0:
                while query.next():
                    if query.value(0):
                        neighCell = ["", query.value(0), query.value(1), query.value(2)]
                        dataList.append(neighCell)
                    else:
                        break
            else:
                dataList.append(["", "", "", ""])
        self.closeConnection()
        return dataList

    def getEvdoParameters(self):
        self.openConnection()
        dataList = []
        evdoFields = ["Time", "DRC", "PER", "", "SINR Per PN:", "PN", "SINR"]

        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)

        query = QSqlQuery()
        queryString = """SELECT time, cdma_evdo_drc, cdma_evdo_per, '' as empty1, '' as empty2, cdma_evdo_pn, cdma_evdo_sinr
                        FROM cdma
                        %s
                        ORDER BY time DESC
                        LIMIT 1""" % (
            condition
        )
        query.exec_(queryString)
        while query.next():
            for field in range(len(evdoFields)):
                if query.value(field):
                    dataList.append([evdoFields[field], query.value(field)])
                else:
                    dataList.append([evdoFields[field], ""])
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
