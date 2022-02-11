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

    "default_mnc": "15",
    "default_mcc": "520"

}
SELECTED_POINT_MATCH_PARAMS = ("log_hash", "posid", "seqid", "time", "lat", "lon")


class analyzer_vars:

    def __init__(self):
        self.load_preferences()
        self.DEFAULT_LOOKBACK_DUR_MILLIS = 2000
        self.maxColumns = 50
        self.maxRows = 1000
        self.schemaList = []
        self.mdi = None
        self.qgis_iface = None
        self.mostFeaturesLayer = None
        self.log_mode = ""
        self.databasePath = None
        self.db_fp = None  # same as databasePath but in snake_case
        self.cell_files = []
        self.minTimeValue = 0
        self.maxTimeValue = 99
        self.fastForwardValue = 1
        self.slowDownValue = 1
        self.currentTimestamp = None
        self.currentDateTimeString = None
        self.recentDateTimeString = ""
        self.selected_row_time = None
        self.selected_row_log_hash = None
        # these are set from mainwindow directly on clickcanvas match, not from timeslider
        self.selected_point_match_dict = dict.fromkeys(SELECTED_POINT_MATCH_PARAMS)
        self.sliderLength = 0
        self.main_window = None
        self.openedWindows = []
        self.timeSlider = None
        self.isSliderPlay = False
        self.log_list = []
        self.device_configs = []
        self.is_indoor = False
        self.easy_overview_mode = False
        self.overview_opened = False
        self.allLayers = []
        self.live_process_list = []
        # tableList = []
        self.highlight_list = []
        self.linechartWindowname = [
            "GSM_GSM Line Chart",
            "WCDMA_Line Chart",
            "LTE_LTE Line Chart",
            "Data_GSM Data Line Chart",
            "Data_WCDMA Data Line Chart",
            "Data_LTE Data Line Chart",
            "Data_5G NR Data Line Chart",
        ]
        self.threadpool = QThreadPool.globalInstance()
        self.CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
        # server mode vars (stored in login_dialog class like server, token, user, lhl etc)
        self.login_dialog = None
        self.pref = DEFAULT_PREF.copy()

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

    def close_db(self):
        pass # now we dont use qsqldatabase anymore

    def is_logged_in(self):
        return self.login_dialog and self.login_dialog.token

    def is_easy_mode(self):
        return self.easy_overview_mode

def get_pref_fp():
    import azq_utils
    return azq_utils.get_settings_fp("preferences.ini")
