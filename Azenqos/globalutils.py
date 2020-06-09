from PyQt5.QtSql import QSql, QSqlDatabase, QSqlQuery
import csv, inspect, os, sys, datetime, json, io
from zipfile import ZipFile

# Adding folder path
sys.path.insert(1, os.path.dirname(os.path.realpath(__file__)))
import global_config as gc

db = None
elementData = []


def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno


# todo: ใช้ข้อมูลจาก csv อ้างอิงชื่อแต่ละ element
class ElementInfo:
    data = []

    def __init__(self):
        global elementData
        reader = csv.DictReader(open("element_info_list.csv"))
        for row in reader:
            if row["name"]:
                rowdict = {
                    "name": row["name"],
                    "column_name": row["var_name"],
                    "db_table": row["db_table"],
                }
                elementData.append(rowdict)

    def getTableAttr(self, name: str):
        for obj in elementData:
            if obj["name"] == name:
                source = [obj["column_name"], obj["db_table"]]
                query = Query(source[0], source[1], "").query()
                table = Table()
                table.row.setSource(source)
                table.row.setDatarow(query)
                table.printdata()

    def checkCsv(self):
        print(elementData)

    def searchName(self, name: str, obj_list: list):
        for obj in obj_list:
            if name in obj["name"]:
                return obj

    def addDatabase(self):
        databasePath = "/Users/Maxorz/Desktop/DB_Test/ARGazqdata.db"
        global db
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName(databasePath)


class Row:
    source = []
    datarow = []

    def setSource(self, source):
        self.source = source

    def setDatarow(self, datarow):
        self.datarow = datarow


class Table:
    row = Row()

    def setTableModel(self):
        return False

    def printdata(self):
        print([self.row.source, self.row.datarow])


class Query(object):
    def __init__(self, column_name: str, table_name: str, condition: str):
        self.column_name = column_name
        self.table_name = table_name

    def query(self):
        condition = ""
        result = []
        # inputdata = ['table','value','row',column']
        # if self.globalTime:
        #     condition = 'WHERE time <= \'%s\'' % (self.globalTime)
        if not db.isOpen():
            db.open()
        query = QSqlQuery()
        queryString = "SELECT %s FROM %s WHERE %s IS NOT NULL LIMIT 1" % (
            self.column_name,
            self.table_name,
            self.column_name,
        )
        query.exec_(queryString)
        while query.next():
            result.append(query.value(0))
        db.close()
        return result


class Utils:
    def __init__(self):
        super().__init__()

    def unzipToFile(self, currentPath, filePath):
        file_folder_path = currentPath + "/file"
        if not os.path.exists(file_folder_path):
            os.makedirs(file_folder_path)
        file_list = os.listdir(file_folder_path)
        if len(file_list) > 0:
            for f in file_list:
                os.remove(file_folder_path + "/" + f)
        if len(os.listdir(file_folder_path)) == 0:
            with ZipFile(filePath, "r") as zip_obj:
                zip_obj.extractall(file_folder_path)
            db_file_path = file_folder_path + "/azqdata.db"
            return db_file_path

    def cleanupFile(self, currentPath):
        file_folder_path = currentPath + "/file"
        file_list = os.listdir(file_folder_path)
        try:
            if len(file_list) > 0:
                for f in file_list:
                    os.remove(file_folder_path + "/" + f)
        except:
            return False

        return True

    def saveState(self, currentPath):
        file_path = currentPath + "/save.azs"
        with open(file_path, "w") as f:
            saveEntities = {}
            winList = []
            for window in gc.openedWindows:
                winList.append(str(window.title))

            saveEntities["windows"] = winList
            saveEntities["timestamp"] = gc.currentTimestamp
            jsonString = json.dumps(saveEntities)
            binString = " ".join(format(x, "b") for x in bytearray(jsonString, "utf-8"))
            f.write(binString)
        return True

    def loadState(self, currentPath, dialog):
        textString = ""
        loadedEntities = None
        file_path = currentPath + "/save.azs"
        if not os.path.exists(file_path):
            return False

        f = io.open(file_path, mode="r")
        text = f.read()

        if text:
            text = text.split(" ")
            textString = bytearray([int(x, 2) for x in text]).decode()
        try:
            loadedEntities = json.loads(textString)
        except:
            pass

        if loadedEntities:
            for window in loadedEntities["windows"]:
                name = window.split("_")
                dialog.classifySelectedItems(name[0], name[1])

            loadedTimestamp = float(loadedEntities["timestamp"])
            if loadedTimestamp >= gc.minTimeValue and loadedTimestamp <= gc.maxTimeValue:
                gc.timeSlider.setValue(loadedTimestamp - gc.minTimeValue)

        f.close()
        return False

    def openConnection(self, db: QSqlDatabase):
        if db:
            if not db.isOpen():
                db.open()

    def closeConnection(self, db: QSqlDatabase):
        if db:
            if db.isOpen():
                db.close()

    def datetimeStringtoTimestamp(datetimeString: str):
        try:
            element = datetime.datetime.strptime(datetimeString, "%Y-%m-%d %H:%M:%S.%f")
            timestamp = datetime.datetime.timestamp(element)
            return timestamp
        except Exception as ex:
            print(ex)
            return False


# todo: dynamic data query object
# class DataQuery:
#     def __inti__(self, fieldArr, tableName, conditionStr):
#         self.fieldArr = fieldArr
#         self.tableName = tableName
#         self.condition = conditionStr

#     def countField(self):
#         fieldCount = 0
#         if self.fieldArr is not None:
#             fieldCount = len(self.fieldArr)
#         return fieldCount

#     def selectFieldToQuery(self):
#         selectField = '*'
#         if self.fieldArr is not None:
#             selectField = ",".join(self.fieldArr)
#         return selectField

#     def getData(self):
#         result = dict()
#         selectField = self.selectFieldToQuery()
#         azenqosDatabase.open()
#         query = QSqlQuery()
#         queryString = 'select %s from %s' % (selectField, self.tableName)
#         query.exec_(queryString)
#         while query.next():
#             for field in range(len(self.fieldArr)):
#                 fieldName = fieldArr[field]
#                 validatedValue = self.valueValidation(query.value(field))
#                 if fieldName in result:
#                     if isinstance(result[fieldName], list):
#                         result[fieldName].append(validatedValue)
#                     else:
#                         result[fieldName] = [validatedValue]
#                 else:
#                     result[fieldName] = [validatedValue]
#         azenqosDatabase.close()
#         return result

# def valueValidation(self, value):
#     validatedValue = 0
#     if value is not None:
#         validatedValue = value
#     return validatedValue


# if __name__ == '__main__':
#     addDatabase()
#     element = ElementInfo()
#     element.checkCsv()
#     print(element.searchName('SINR\tRx[0]', elementData))
#     element.getTableAttr('SINR\tRx[0]')
# element.getTableAttr()
