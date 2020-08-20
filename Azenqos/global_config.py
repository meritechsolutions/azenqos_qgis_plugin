import os
from PyQt5.QtCore import *
from PyQt5 import QtCore

DEFAULT_LOOKBACK_DUR_MILLIS = 2000
maxColumns = 50
maxRows = 1000
schemaList = []
activeLayers = []
mostFeaturesLayer = None
azenqosDatabase = None
databasePath = None
dbcon = None
minTimeValue = None
maxTimeValue = None
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
tableList = []
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
threadpool = QThreadPool()
CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))

