from PyQt5.QtSql import QSql,QSqlDatabase,QSqlQuery

def addDatabase():
  databasePath = '/Users/Maxorz/Desktop/DB_Test/ARGazqdata.db'
  db = QSqlDatabase.addDatabase("QSQLITE")
  db.setDatabaseName(databasePath)
  return db

