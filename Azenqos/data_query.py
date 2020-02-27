from PyQt5.QtSql import QSqlQuery, QSqlDatabase

class DataQuery:
    def __init__(self, database, currentDateTimeString):
        self.timeFilter = ''
        self.azenqosDatabase = database
        if currentDateTimeString:
            self.timeFilter = currentDateTimeString

    def getGprsEdgeInformation(self):
        if azenqosDatabase is not None:
            azenqosDatabase.open()
        query = QSqlQuery()
        query.exec_("SELECT * FROM events")
        timeField = query.record().indexOf("time")
        nameField = query.record().indexOf("name")
        detailField = query.record().indexOf("info")
        dataList = []
        while query.next():
            timeValue = query.value(timeField)
            nameValue = query.value(nameField)
            detailStrValue = query.value(detailField)
            dataList.append([timeValue, '', nameValue, detailStrValue])
        azenqosDatabase.close()
        return dataList

    def getHsdpaHspaStatistics(self):
        if azenqosDatabase is not None:
            azenqosDatabase.open()
        query = QSqlQuery()
        query.exec_("SELECT * FROM events")
        timeField = query.record().indexOf("time")
        nameField = query.record().indexOf("name")
        detailField = query.record().indexOf("info")
        dataList = []
        while query.next():
            timeValue = query.value(timeField)
            nameValue = query.value(nameField)
            detailStrValue = query.value(detailField)
            dataList.append([timeValue, '', nameValue, detailStrValue])
        azenqosDatabase.close()
        return dataList

    def getHsupaStatistics(self):
        if azenqosDatabase is not None:
            azenqosDatabase.open()
        query = QSqlQuery()
        query.exec_("SELECT * FROM events")
        timeField = query.record().indexOf("time")
        nameField = query.record().indexOf("name")
        detailField = query.record().indexOf("info")
        dataList = []
        while query.next():
            timeValue = query.value(timeField)
            nameValue = query.value(nameField)
            detailStrValue = query.value(detailField)
            dataList.append([timeValue, '', nameValue, detailStrValue])
        azenqosDatabase.close()
        return dataList

    def getLteDataStatistics(self):
        if azenqosDatabase is not None:
            azenqosDatabase.open()
        query = QSqlQuery()
        query.exec_("SELECT * FROM events")
        timeField = query.record().indexOf("time")
        nameField = query.record().indexOf("name")
        detailField = query.record().indexOf("info")
        dataList = []
        while query.next():
            timeValue = query.value(timeField)
            nameValue = query.value(nameField)
            detailStrValue = query.value(detailField)
            dataList.append([timeValue, '', nameValue, detailStrValue])
        azenqosDatabase.close()
        return dataList

    def getWifiConnectedAp(self):
        if azenqosDatabase is not None:
            azenqosDatabase.open()
        query = QSqlQuery()
        query.exec_("SELECT * FROM events")
        timeField = query.record().indexOf("time")
        nameField = query.record().indexOf("name")
        detailField = query.record().indexOf("info")
        dataList = []
        while query.next():
            timeValue = query.value(timeField)
            nameValue = query.value(nameField)
            detailStrValue = query.value(detailField)
            dataList.append([timeValue, '', nameValue, detailStrValue])
        azenqosDatabase.close()
        return dataList

    def getWifiScannedAps(self):
        if azenqosDatabase is not None:
            azenqosDatabase.open()
        query = QSqlQuery()
        query.exec_("SELECT * FROM events")
        timeField = query.record().indexOf("time")
        nameField = query.record().indexOf("name")
        detailField = query.record().indexOf("info")
        dataList = []
        while query.next():
            timeValue = query.value(timeField)
            nameValue = query.value(nameField)
            detailStrValue = query.value(detailField)
            dataList.append([timeValue, '', nameValue, detailStrValue])
        azenqosDatabase.close()
        return dataList

    def getWifiGraph(self):
        if azenqosDatabase is not None:
            azenqosDatabase.open()
        query = QSqlQuery()
        query.exec_("SELECT * FROM events")
        timeField = query.record().indexOf("time")
        nameField = query.record().indexOf("name")
        detailField = query.record().indexOf("info")
        dataList = []
        while query.next():
            timeValue = query.value(timeField)
            nameValue = query.value(nameField)
            detailStrValue = query.value(detailField)
            dataList.append([timeValue, '', nameValue, detailStrValue])
        azenqosDatabase.close()
        return dataList