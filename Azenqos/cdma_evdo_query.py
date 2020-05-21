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
        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)
            dataList.append(["Time", self.timeFilter, ""])

        elementDictList = [
            {
                "name": "cdma",
                "element": "Active PN (Best), Ec/Io,RX Power,TX Power,FER,Channel,Band class,N Active Set Cells",
                "table": "cdma",
                "column": "cdma_cell_pn_1, cdma_ecio_1, cdma_rx_power, cdma_tx_power, cdma_fer, cdma_channel, cdma_band_class, cdma_n_aset_cells",
            }
        ]
        for dic in elementDictList:
            temp = []
            name = dic["name"]
            element = dic["element"]
            mainElement = dic["element"]
            mainColumn = dic["column"]
            subColumn = dic["column"]
            table = dic["table"]
            join = None
            joinString = ""
            onString = ""

            if element and mainColumn and table:
                queryString = """SELECT %s
                                FROM ( SELECT %s,1 as row_num
                                        FROM %s 
                                        %s 
                                        ORDER BY time DESC 
                                        LIMIT 1 
                                    ) %s
                                %s 
                                """ % (
                    mainColumn,
                    subColumn,
                    table,
                    condition,
                    name,
                    joinString,
                )
                query = QSqlQuery()
                query.exec_(queryString)
                elements = mainElement.split(",")
                if query.first():
                    for i in range(0, len(elements)):
                        temp.append(
                            [
                                elements[i],
                                "" if str(query.value(i)) == "NULL" else query.value(i),
                                "",
                            ]
                        )
                else:
                    for elem in elements:
                        temp.append([elem, "", ""])
            dataList.extend(temp)
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
            row = []
            queryString = """SELECT cdma_cell_pn_%d, cdma_ecio_%d, cdma_cell_type_%d
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
            if query.first():
                for i in range(3):
                    row.append("" if str(query.value(i)) == "NULL" else query.value(i))
            else:
                row = ["", "", ""]

            if not all(v == "" for v in row):
                row.insert(0, "")
                dataList.append(row)
        if len(dataList) == 0:
            dataList.append([self.timeFilter, "", "", ""])
        self.closeConnection()
        return dataList

    def getEvdoParameters(self):
        self.openConnection()
        MAX_EVDO = 6
        dataList = []
        evdoFields = ["DRC", "PER", "", "SINR Per PN:"]
        evdoExtend = ["PN", "SINR"]

        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)

        query = QSqlQuery()
        evdoQueryString = ""
        for i in range(MAX_EVDO):
            evdoQueryString += ",cdma_evdo_pn_%d, cdma_evdo_sinr_%d" % (i + 1, i + 1)

        queryString = """SELECT cdma_evdo_drc, cdma_evdo_per, '' as empty1, '' as empty2 %s
                        FROM cdma
                        %s
                        ORDER BY time DESC
                        LIMIT 1""" % (
            evdoQueryString,
            condition,
        )
        query.exec_(queryString)
        dataList.append(["Time", self.timeFilter])
        if query.first():
            extraHeaderRow = []
            extraRow = []
            for field in range(len(evdoFields)):
                if not str(query.value(field)) == "NULL":
                    dataList.append([evdoFields[field], query.value(field)])
                else:
                    dataList.append([evdoFields[field], ""])
            for field in range(len(evdoExtend)):
                extraHeaderRow.append(evdoExtend[field])
            dataList.append(extraHeaderRow)
            for extendField in range(MAX_EVDO * 2):
                fieldIndex = (len(evdoFields) - 1) + extendField
                if not str(query.value(fieldIndex)) == "NULL":
                    extraRow.append(query.value(fieldIndex))
                else:
                    extraRow.append("")
                if len(extraRow) >= 2:
                    if not all(v == "" for v in extraRow):
                        dataList.append(extraRow)
                    extraRow = []
        else:
            extraHeaderRow = []
            for field in evdoFields:
                dataList.append([field, ""])
            for field in range(len(evdoExtend)):
                extraHeaderRow.append(evdoExtend[field])
            dataList.append(extraHeaderRow)
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
