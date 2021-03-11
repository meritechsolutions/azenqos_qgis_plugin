from PyQt5.QtSql import QSqlQuery, QSqlDatabase
import numpy as np


class LineChartQueryNew:
    def __init__(self, azenqosDatabase):
        self.result = dict()
        self.azenqosDatabase = azenqosDatabase
        self.selectField = []
        self.yRange = [0.00, 0.00]

    def getGsm(self):
        self.selectField = ["time", "gsm_rxlev_sub_dbm", "gsm_rxqual_sub"]
        self.openConnection()
        query = QSqlQuery()
        queryString = (
            "select time, gsm_rxlev_sub_dbm, gsm_rxqual_sub from gsm_cell_meas"
        )
        query.exec_(queryString)
        while query.next():
            for field in range(len(self.selectField)):
                fieldName = self.selectField[field]
                validatedValue = self.valueValidation(query.value(field))
                if fieldName in self.result:
                    if isinstance(self.result[fieldName], list):
                        self.result[fieldName].append(validatedValue)
                    else:
                        self.result[fieldName] = [validatedValue]
                else:
                    self.result[fieldName] = [validatedValue]

        if not self.result:
            for field in range(len(self.selectField)):
                fieldName = self.selectField[field]
                self.result[fieldName] = ""
        self.closeConnection()
        return self.result

    def getGsmData(self):
        self.selectField = [
            "time",
            "data_gsm_rlc_ul_throughput",
            "data_app_dl_throughput_1",
            "data_download_session_average",
        ]
        self.openConnection()
        query = QSqlQuery()

        # recheck later
        # queryString = """SELECT dat.time, des.data_gsm_rlc_ul_throughput, dat.data_app_dl_throughput_1, dat.data_download_session_average
        #                 FROM data_app_throughput dat
        #                 LEFT JOIN data_egprs_stats des ON dat.time = des.time;"""

        queryString = """SELECT DISTINCT dat.time, NULL as data_wcdma_rlc_dl_throughput, dat.data_app_dl_throughput_1, dat.data_download_session_average, NULL as data_hsdpa_thoughput
                        FROM data_app_throughput dat
                        WHERE data_app_dl_throughput_1 IS NOT NULL 
                        UNION
                        SELECT DISTINCT dwrs.time, dwrs.data_wcdma_rlc_dl_throughput, NULL as data_app_dl_throughput_1, NULL as data_download_session_average, NULL as data_hsdpa_thoughput
                        FROM data_wcdma_rlc_stats dwrs
                        WHERE data_wcdma_rlc_dl_throughput IS NOT NULL 
                        UNION
                        SELECT DISTINCT whs.time, NULL as data_wcdma_rlc_dl_throughput, NULL as data_app_dl_throughput_1, NULL as data_download_session_average, whs.data_hsdpa_thoughput
                        FROM wcdma_hsdpa_stats whs
                        WHERE data_hsdpa_thoughput IS NOT NULL;"""

        query.exec_(queryString)
        while query.next():
            for field in range(len(self.selectField)):
                fieldName = self.selectField[field]
                validatedValue = self.valueValidation(query.value(field))
                if fieldName in self.result:
                    if isinstance(self.result[fieldName], list):
                        self.result[fieldName].append(validatedValue)
                    else:
                        self.result[fieldName] = [validatedValue]
                else:
                    self.result[fieldName] = [validatedValue]

        if not self.result:
            for field in range(len(self.selectField)):
                fieldName = self.selectField[field]
                self.result[fieldName] = ""
        self.closeConnection()
        return self.result

    def getWcdma(self):
        self.selectField = [
            "time",
            "wcdma_aset_ecio_avg",
            "wcdma_aset_rscp_avg",
            "wcdma_rssi",
            "wcdma_bler_average_percent_all_channels",
        ]
        self.openConnection()
        query = QSqlQuery()
        queryString = """SELECT wcm.time, wcm.wcdma_aset_ecio_avg, wcm.wcdma_aset_rscp_avg, wrp.wcdma_rssi, wb.wcdma_bler_average_percent_all_channels
                        FROM wcdma_cell_meas wcm
                        LEFT JOIN wcdma_rx_power wrp ON wcm.time = wrp.time
                        LEFT JOIN wcdma_bler wb ON wcm.time = wb.time"""
        query.exec_(queryString)
        while query.next():
            for field in range(len(self.selectField)):
                fieldName = self.selectField[field]
                validatedValue = self.valueValidation(query.value(field))
                if fieldName in self.result:
                    if isinstance(self.result[fieldName], list):
                        self.result[fieldName].append(validatedValue)
                    else:
                        self.result[fieldName] = [validatedValue]
                else:
                    self.result[fieldName] = [validatedValue]

        if not self.result:
            for field in range(len(self.selectField)):
                fieldName = self.selectField[field]
                self.result[fieldName] = ""
        self.closeConnection()
        return self.result

    def getWcdmaData(self):
        self.selectField = [
            "time",
            "data_wcdma_rlc_dl_throughput",
            "data_app_dl_throughput_1",
            "data_download_session_average",
            "data_hsdpa_thoughput",
        ]
        self.openConnection()
        query = QSqlQuery()
        # queryString = """SELECT dat.time, dwrs.data_wcdma_rlc_dl_throughput, dat.data_app_dl_throughput_1, dat.data_download_session_average, whs.data_hsdpa_thoughput
        #                 FROM data_app_throughput dat
        #                 LEFT JOIN data_wcdma_rlc_stats dwrs ON dwrs.time = dat.time
        #                 LEFT JOIN wcdma_hsdpa_stats whs ON whs.time = dwrs.time"""
        queryString = """SELECT dat.time, NULL as data_wcdma_rlc_dl_throughput, dat.data_app_dl_throughput_1, dat.data_download_session_average, NULL as data_hsdpa_thoughput
                        FROM data_app_throughput dat
                        WHERE data_app_dl_throughput_1 IS NOT NULL
                        UNION
                        SELECT dwrs.time, dwrs.data_wcdma_rlc_dl_throughput, NULL as data_app_dl_throughput_1, NULL as data_download_session_average, NULL as data_hsdpa_thoughput
                        FROM data_wcdma_rlc_stats dwrs
                        WHERE data_wcdma_rlc_dl_throughput IS NOT NULL
                        UNION
                        SELECT whs.time, NULL as data_wcdma_rlc_dl_throughput, NULL as data_app_dl_throughput_1, NULL as data_download_session_average, whs.data_hsdpa_thoughput
                        FROM wcdma_hsdpa_stats whs
                        WHERE data_hsdpa_thoughput IS NOT NULL"""
        query.exec_(queryString)
        while query.next():
            for field in range(len(self.selectField)):
                fieldName = self.selectField[field]
                validatedValue = self.valueValidation(query.value(field))
                if fieldName in self.result:
                    if isinstance(self.result[fieldName], list):
                        self.result[fieldName].append(validatedValue)
                    else:
                        self.result[fieldName] = [validatedValue]
                else:
                    self.result[fieldName] = [validatedValue]

        if not self.result:
            for field in range(len(self.selectField)):
                fieldName = self.selectField[field]
                self.result[fieldName] = ""
        self.closeConnection()
        return self.result

    def getLte(self):
        self.selectField = [
            "time",
            "lte_sinr_rx0_1",
            "lte_sinr_rx1_1",
            "lte_inst_rsrp_1",
            "lte_inst_rsrq_1",
            "lte_inst_rssi_1",
        ]
        self.openConnection()
        query = QSqlQuery()
        queryString = """SELECT time, lte_sinr_rx0_1, lte_sinr_rx1_1,
                        lte_inst_rsrp_1, lte_inst_rsrq_1, lte_inst_rssi_1
                        FROM lte_cell_meas"""
        query.exec_(queryString)
        while query.next():
            for field in range(len(self.selectField)):
                fieldName = self.selectField[field]
                validatedValue = self.valueValidation(query.value(field))
                if fieldName in self.result:
                    if isinstance(self.result[fieldName], list):
                        self.result[fieldName].append(validatedValue)
                    else:
                        self.result[fieldName] = [validatedValue]
                else:
                    self.result[fieldName] = [validatedValue]

        if not self.result:
            for field in range(len(self.selectField)):
                fieldName = self.selectField[field]
                self.result[fieldName] = ""
        self.closeConnection()
        return self.result

    def getLteData(self):
        self.selectField = [
            "time",
            "data_download_overall",
            "data_upload_overall",
            "lte_l1_throughput_mbps_1",
            "lte_bler_1",
        ]
        self.openConnection()
        query = QSqlQuery()
        # queryString = """SELECT dat.time, dat.data_download_overall, dat.data_upload_overall, lldt.lte_l1_throughput_mbps_1, lldt.lte_bler_1
        #                 FROM data_app_throughput dat
        #                 LEFT JOIN lte_l1_dl_tp lldt ON lldt.time = dat.time"""
        queryString = """SELECT dat.time, dat.data_download_overall, dat.data_upload_overall, NULL as lte_l1_throughput_mbps_1, NULL as lte_bler_1
                        FROM data_app_throughput dat
                        WHERE data_download_overall IS NOT NULL OR data_upload_overall IS NOT NULL
                        UNION
                        SELECT lldt.time, NULL as data_download_overall, NULL as data_upload_overall, lldt.lte_l1_throughput_mbps_1, lldt.lte_bler_1
                        FROM lte_l1_dl_tp lldt
                        WHERE lte_l1_throughput_mbps_1 IS NOT NULL OR lte_bler_1 IS NOT NULL"""
        query.exec_(queryString)
        while query.next():
            for field in range(len(self.selectField)):
                fieldName = self.selectField[field]
                validatedValue = self.valueValidation(query.value(field))
                if fieldName in self.result:
                    if isinstance(self.result[fieldName], list):
                        self.result[fieldName].append(validatedValue)
                    else:
                        self.result[fieldName] = [validatedValue]
                else:
                    self.result[fieldName] = [validatedValue]

        if not self.result:
            for field in range(len(self.selectField)):
                fieldName = self.selectField[field]
                self.result[fieldName] = ""
        self.closeConnection()
        return self.result

    def getNrData(self):
        self.selectField = [
            "time",
            "app_dl",
            "app_ul",
            "nr_lte_dl",
            "nr_lte_ul",
            "nr_dl",
            "nr_ul",
            "lte_dl",
            "lte_ul",
        ]
        self.openConnection()
        query = QSqlQuery()
        queryString = """SELECT 
            dat.time, 
            (dat.data_download_overall / 1000) as app_dl, 
            (dat.data_upload_overall / 1000) as app_ul, 
            NULL as nr_lte_dl, 
            NULL as nr_lte_ul,
            NULL as nr_dl,
            NULL as nr_ul,
            NULL as lte_dl,
            NULL as lte_ul
        FROM data_app_throughput dat
        WHERE data_download_overall IS NOT NULL OR data_upload_overall IS NOT NULL
        UNION
            SELECT 
                lldt.time, 
                NULL as app_dl, 
                NULL as app_ul, 
                (IFNULL(lldt.nr_p_plus_scell_nr_pdsch_tput_mbps,0) + IFNULL(lldt.nr_p_plus_scell_lte_dl_pdcp_tput_mbps,0)) as nr_lte_dl, 
                (IFNULL(lldt.nr_p_plus_scell_nr_pusch_tput_mbps,0) + IFNULL(lldt.nr_p_plus_scell_lte_ul_pdcp_tput_mbps,0)) as nr_lte_ul,
                lldt.nr_p_plus_scell_nr_pdsch_tput_mbps as nr_dl,
                lldt.nr_p_plus_scell_nr_pusch_tput_mbps as nr_ul,
                lldt.nr_p_plus_scell_lte_dl_pdcp_tput_mbps as lte_dl,
                lldt.nr_p_plus_scell_lte_ul_pdcp_tput_mbps  as lte_ul
            FROM nr_cell_meas lldt
            WHERE 
                nr_lte_dl IS NOT NULL 
                OR nr_lte_ul IS NOT NULL
                OR nr_dl IS NOT NULL
                OR nr_ul IS NOT NULL
                OR lte_dl IS NOT NULL
                OR lte_ul IS NOT NULL"""
        query.exec_(queryString)
        while query.next():
            for field in range(len(self.selectField)):
                fieldName = self.selectField[field]
                validatedValue = self.valueValidation(query.value(field))
                if fieldName in self.result:
                    if isinstance(self.result[fieldName], list):
                        self.result[fieldName].append(validatedValue)
                    else:
                        self.result[fieldName] = [validatedValue]
                else:
                    self.result[fieldName] = [validatedValue]

        if not self.result:
            for field in range(len(self.selectField)):
                fieldName = self.selectField[field]
                self.result[fieldName] = ""
        self.closeConnection()
        return self.result

    def valueValidation(self, value):
        validatedValue = np.nan
        if value:
            validatedValue = value
        return validatedValue

    def openConnection(self):
        if self.azenqosDatabase is not None:
            self.azenqosDatabase.open()

    def closeConnection(self):
        self.azenqosDatabase.close()

    def findMinMax(self, minList, maxList):
        yRange = [0.00, 0.00]
        if len(minList) > 0:
            yRange[0] = min(minList)
        if len(maxList) > 0:
            yRange[1] = max(maxList)
        return yRange
