from PyQt5.QtSql import QSql,QSqlDatabase,QSqlQuery
import csv
import inspect

db = None
elementData = []

def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno

class ElementInfo:
    data = []
    def __init__(self):
        global elementData
        reader = csv.DictReader(open('element_info_list.csv'))
        for row in reader:
            if row['name']:
                rowdict = {'name': row['name'], 'column_name': row['var_name'], 'db_table': row['db_table']}
                elementData.append(rowdict)

    def getTableAttr(self, name: str):
        for obj in elementData:
            if obj['name'] == name:
                source = [obj['column_name'], obj['db_table']]
                query = Query(source[0], source[1]).query()
                table = Table()
                table.row.setSource(source)
                table.row.setDatarow(query)
                table.printdata()
                break

    def checkCsv(self):
        print(len(elementData))
        print(elementData.__sizeof__())
        print(elementData[0])


def addDatabase():
    databasePath = '/Users/Maxorz/Desktop/DB_Test/ARGazqdata.db'
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
        print([self.row.source,self.row.datarow])

class Query:
    def __init__(self, column_name: str, table_name: str):
        self.column_name = column_name
        self.table_name = table_name

    def query(self):
        condition = ''
        result = []
        #inputdata = ['table','value','row',column']
        # if self.globalTime:
        #     condition = 'WHERE time <= \'%s\'' % (self.globalTime)
        if not db.isOpen():
            db.open()
        query = QSqlQuery()
        queryString = 'SELECT %s FROM %s WHERE %s IS NOT NULL LIMIT 1' % (self.column_name, self.table_name, self.column_name)
        query.exec_(queryString)
        while query.next():
            result.append(query.value(0))
        db.close()
        return result



if __name__ == '__main__':
    addDatabase()
    element = ElementInfo()
    element.checkCsv()