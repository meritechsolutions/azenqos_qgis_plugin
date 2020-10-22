from PyQt5.QtSql import QSqlQuery


class PolqaQuery:
    def __init__(self, database, currentDateTimeString, polqa_mos=None):
        self.timeFilter = ""
        self.azenqosDatabase = database
        if currentDateTimeString:
            self.timeFilter = currentDateTimeString
        self.polqa_mos = polqa_mos

    def getPolqa(self):
        self.openConnection()
        queryString = "SELECT polqa_output_text, wav_filename from polqa_mos pm WHERE polqa_mos = '{}' AND time <= '{}' LIMIT 1".format(
            self.polqa_mos, self.timeFilter
        )
        query = QSqlQuery()
        query.exec_(queryString)
        outputText = query.record().indexOf("polqa_output_text")
        outputFile = query.record().indexOf("wav_filename")
        dataDict = {"output_text": None, "wave_file": None}
        while query.next():
            dataDict["output_text"] = query.value(outputText)
            dataDict["wave_file"] = query.value(outputFile)
        self.closeConnection()
        return dataDict

    def openConnection(self):
        if self.azenqosDatabase is not None:
            self.azenqosDatabase.open()

    def closeConnection(self):
        self.azenqosDatabase.close()

