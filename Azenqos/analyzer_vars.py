import os

from PyQt5.QtCore import QThreadPool

DEFAULT_PREF = {

    "cell_nr_sector_size_meters": "30",
    "cell_lte_sector_size_meters": "40",
    "cell_wcdma_sector_size_meters": "50",
    "cell_gsm_sector_size_meters": "60",

    "spider_match_max_distance_meters": "15000",
    "spider_match_cgi": "0",

    "point_to_site_match_max_distance_meters": "15000",
    "point_to_site_serving_match_cgi": "0",

}
SELECTED_POINT_MATCH_PARAMS = ("log_hash", "posid", "seqid", "time", "lat", "lon")


class analyzer_vars:
    DEFAULT_LOOKBACK_DUR_MILLIS = 2000
    maxColumns = 50
    maxRows = 1000
    schemaList = []
    mdi = None
    qgis_iface = None
    mostFeaturesLayer = None

    databasePath = None
    db_fp = None  # same as databasePath but in snake_case
    cell_files = []

    minTimeValue = 0
    maxTimeValue = 99
    fastForwardValue = 1
    slowDownValue = 1

    currentTimestamp = None
    currentDateTimeString = None
    recentDateTimeString = ""
    selected_row_log_hash = None

    # these are set from mainwindow directly on clickcanvas match, not from timeslider
    selected_point_match_dict = dict.fromkeys(SELECTED_POINT_MATCH_PARAMS)

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

    pref = DEFAULT_PREF.copy()

    def __init__(self):
        self.load_preferences()


    def delete_preferences(self):
        fp = get_pref_fp()
        if os.path.isfile(fp):
            os.remove(fp)
        assert False == os.path.isfile(fp)
        self.pref = DEFAULT_PREF.copy()


    def load_preferences(self):
        import azq_utils
        self.pref = DEFAULT_PREF.copy()  # in case below load fails
        return azq_utils.load_ini_to_dict_keys(get_pref_fp(), self.pref)


    def save_preferences(self):
        import azq_utils
        azq_utils.write_dict_to_ini(self.pref, get_pref_fp())

    def close_db(gc):
        # now we dont use qsqldatabase anymore
        pass

def get_pref_fp():
    import azq_utils
    return azq_utils.get_settings_fp("preferences.ini")