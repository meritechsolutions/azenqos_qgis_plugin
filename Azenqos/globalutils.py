from PyQt5.QtSql import QSql, QSqlDatabase, QSqlQuery
import csv, inspect, os, sys, datetime, json, io
from zipfile import ZipFile
import shutil

# Adding folder path
sys.path.insert(1, os.path.dirname(os.path.realpath(__file__)))

TMP_FOLDER_NAME = "tmp_gen"

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
    gc = None
    def __init__(self, gc):
        self.gc = gc

    def tmp_gen_path(self):
        return os.path.join(self.gc.CURRENT_PATH, TMP_FOLDER_NAME)

    def unzipToFile(self, currentPath, filePath):
        self.gc.logPath = os.path.join(self.tmp_gen_path(), str(os.getpid()))
        if not os.path.exists(self.gc.logPath):
            os.makedirs(self.gc.logPath)
        else:
            shutil.rmtree(self.gc.logPath)
            os.makedirs(self.gc.logPath)
            
        if len(os.listdir(self.gc.logPath)) == 0:
            with ZipFile(filePath, "r") as zip_obj:
                filesContain = zip_obj.namelist()
                for fileName in filesContain:
                    zip_obj.extract(fileName, self.gc.logPath)
            db_file_path = self.gc.logPath + "/azqdata.db"
            return db_file_path
        else:
            raise Exception("target tmp folder not empty: {}".format(self.gc.logPath))        


    def openConnection(self, db: QSqlDatabase):
        print("%s: openConnection" % os.path.basename(__file__))
        if db:
            if not db.isOpen():
                db.open()

    def closeConnection(self, db: QSqlDatabase):
        print("%s: closeConnection" % os.path.basename(__file__))
        if db:
            if db.isOpen():
                db.close()

    def datetimeStringtoTimestamp(self, datetimeString: str):
        # print("%s: datetimestringtotimestamp" % os.path.basename(__file__))
        try:
            element = datetime.datetime.strptime(datetimeString, "%Y-%m-%d %H:%M:%S.%f")
            timestamp = datetime.datetime.timestamp(element)
            return timestamp
        except Exception as ex:
            print(ex)
            return False
