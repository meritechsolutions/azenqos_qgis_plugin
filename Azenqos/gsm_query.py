from PyQt5.QtSql import QSqlQuery, QSqlDatabase

class GsmDataQuery:
    def __init__(self, database, currentDateTimeString):
        self.timeFilter = ''
        self.azenqosDatabase = database
        if currentDateTimeString:
            self.timeFilter = currentDateTimeString

    def getRadioParameters(self):
        self.openConnection()
        dataList = []
        fieldsList = [
            'Time', 'RxLev', 'RxQual', 'TA', 'RLT (Max)', 'RLT (Current)',
            'DTX Used', 'TxPower', 'FER'
        ]
        selectedColumns = "gcm.time, gcm.gsm_rxlev_full_dbm, gcm.gsm_rxlev_sub_dbm, gcm.gsm_rxqual_full, gcm.gsm_rxqual_sub, gtm.gsm_ta, grtc.gsm_radiolinktimeout_max, grc.gsm_radiolinktimeout_current, grmp.gsm_dtxused, gtm.gsm_txpower, gsm_fer"
        queryString = """SELECT %s
                        FROM gsm_cell_meas gcm
                        LEFT JOIN gsm_rlt_counter grc ON gcm.time = grc.time
                        LEFT JOIN gsm_rl_timeout_counter grtc ON gcm.time = grtc.time
                        LEFT JOIN gsm_tx_meas gtm ON gcm.time = gtm.time
                        LEFT JOIN gsm_rr_measrep_params grmp ON gcm.time = grmp.time
                        LEFT JOIN vocoder_info vi ON gcm.time = vi.time
                        ORDER BY time DESC LIMIT 1""" % (selectedColumns)
        query = QSqlQuery()
        query.exec_(queryString)
        fieldCount = len(selectedColumns.split(","))
        while query.next():
            for index in range(fieldCount):
                columnName = fieldsList[index]
                fullValue = query.value(index)
                subValue = ''
                if columnName in any(('RxLev', 'RxQual')):
                    index + 1
                    subValue = query.value(index)
                dataList.append([columnName, fullValue, subValue])
        azenqosDatabase.close()
        return dataList

    def getServingAndNeighbors(self):
        self.openConnection()
        dataList = []
        fieldsList = [
            'Time', 'Cellname', 'LAC', 'BSIC', 'ARFCN', 'RxLev', 'C1', 'C2', 'C31', 'C32'
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
                        """ % (selectedColumns, condition)
        query = QSqlQuery()
        query.exec_(queryString)
        while query.next():
            for x in range(len(fieldsList)):
                if query.value(x):
                    dataList.append(query.value(x))
                else:
                    dataList.append('')
        self.closeConnection()
        return dataList

    def getCurrentChannel(self):
        self.openConnection()
        query = QSqlQuery()
        query.exec_("SELECT * FROM events")
        dataList = []
        while query.next():
            dataList.append(None)
        self.closeConnection()
        return dataList

    def getCSlashI(self):
        self.openConnection()
        query = QSqlQuery()
        query.exec_("SELECT * FROM events")
        dataList = []
        while query.next():
            dataList.append(None)
        azenqosDatabase.close()
        return dataList

    def getGSMLineChart(self):
        self.openConnection()
        query = QSqlQuery()
        query.exec_("SELECT * FROM events")
        dataList = []
        while query.next():
            dataList.append(None)
        azenqosDatabase.close()
        return dataList

    def getGSMEventsCounter(self):
        self.openConnection()
        query = QSqlQuery()
        query.exec_("SELECT * FROM events")
        dataList = []
        while query.next():
            dataList.append(None)
        azenqosDatabase.close()
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
                    value = ''
                    dataList.append([columnName, value, '', ''])
            return dataList