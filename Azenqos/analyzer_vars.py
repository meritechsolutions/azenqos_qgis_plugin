import os
from PyQt5.QtCore import *
from PyQt5 import QtCore
from PyQt5.QtSql import QSqlQuery, QSqlDatabase


class analyzer_vars:
    DEFAULT_LOOKBACK_DUR_MILLIS = 2000
    maxColumns = 50
    maxRows = 1000
    schemaList = []
    activeLayers = []
    mdi = None
    qgis_iface = None
    mostFeaturesLayer = None
    azenqosDatabase = None
    databasePath = None
    db_fp = None  # same as databasePath but in snake_case
    dbcon = None
    minTimeValue = 0
    maxTimeValue = 99
    fastForwardValue = 1
    slowDownValue = 1
    currentTimestamp = None
    currentDateTimeString = None
    recentDateTimeString = ""
    clickedLatLon = {"lat": 0, "lon": 0}
    sliderLength = 0
    openedWindows = []
    timeSlider = None
    isSliderPlay = False
    allLayers = []
    # tableList = []
    h_list = []
    linechartWindowname = [
        "GSM_GSM Line Chart",
        "WCDMA_Line Chart",
        "LTE_LTE Line Chart",
        "Data_GSM Data Line Chart",
        "Data_WCDMA Data Line Chart",
        "Data_LTE Data Line Chart",
        "Data_5G NR Data Line Chart",
    ]
    threadpool = QThreadPool.globalInstance()
    CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))

    # server mode vars (stored in login_dialog class like server, token, user, lhl etc)
    login_dialog = None

    def close_db(gc):
        if gc.azenqosDatabase:
            gc.azenqosDatabase.close()
            QSqlDatabase.removeDatabase(gc.azenqosDatabase.connectionName())
            names = QSqlDatabase.connectionNames()
            for name in names:
                QSqlDatabase.database(name).close()
                QSqlDatabase.removeDatabase(name)
            gc.azenqosDatabase = None
