from PyQt5.QtSql import QSqlQuery, QSqlDatabase
import re


class NrDataQuery:
    def __init__(self, database, currentDateTimeString):
        self.timeFilter = ""
        self.azenqosDatabase = database
        if currentDateTimeString:
            self.timeFilter = currentDateTimeString

    def getRadioParameters(self):
        self.openConnection()
        dataList = []
        condition = ""

        MAX_SERVING = 8

        PARAMS = [
            ("Beam ID", "nr_servingbeam_pci_"),
            ("Band", "nr_band_"),
            ("Band Type", "nr_band_type_"),
            ("ARFCN", "nr_dl_arfcn_"),
            ("Frequency", "nr_dl_frequency_"),
            ("PCI", "nr_servingbeam_pci_"),
            ("RSRP", "nr_servingbeam_ss_rsrp_"),
            ("RSRQ", "nr_servingbeam_ss_rsrq_"),
            ("SINR", "nr_servingbeam_ss_sinr_"),
            ("Bandwidth", "nr_bw_"),
            ("SSB SCS", "nr_ssb_scs_"),
            ("SCS", "nr_numerology_scs_"),
            ("PUSCH Power", "nr_pusch_tx_power_"),
            ("PUCCH Power", "nr_pucch_tx_power_"),
            ("SRS Power", "nr_srs_tx_power_"),
        ]

        queryString = """
        SELECT
        *
        FROM
        nr_cell_meas
        WHERE
        time <= '%s'
        ORDER BY time DESC
        LIMIT 1
        """ % (self.timeFilter)

        query = QSqlQuery()

        query.exec_(queryString)
        record = query.record()
        if query.first():
            for i in range(len(PARAMS)):
                (label, prefix) = PARAMS[i]
                row = [""] * (MAX_SERVING + 1)
                row[0] = label
                for arg in range(1, MAX_SERVING + 1):
                    field_name = prefix + str(arg)
                    filed_index = record.indexOf(field_name)
                    if filed_index >= 0:
                        value = query.value(filed_index)
                        row[arg] = str(value or "")
                dataList.append(row)

        self.closeConnection()
        return dataList

    def getServingAndNeighbors(self):
        self.openConnection()
        MAX_SERVING = 8
        MAX_DETECTED = 10
        dataList = []

        COL_LABEL = 0
        COL_PCI = 1
        COL_BEAM_ID = 2
        COL_RSRP = 3
        COL_RSRQ = 4
        COL_SINR = 5
        COL_BAND = 6
        COL_BAND_TYPE = 7
        COL_BANDWIDTH = 8
        COL_SSB_SCS = 9
        COL_DL_FREQ = 10
        COL_DL_ARFCN = 11
        COL_SCS = 12

        HEADERS = [""] * 13
        HEADERS[COL_LABEL] = ""
        HEADERS[COL_PCI] = "PCI"
        HEADERS[COL_BEAM_ID] = "Beam ID"
        HEADERS[COL_RSRP] = "RSRP"
        HEADERS[COL_RSRQ] = "RSRQ"
        HEADERS[COL_SINR] = "SINR"
        HEADERS[COL_BAND] = "Band"
        HEADERS[COL_BAND_TYPE] = "Band Type"
        HEADERS[COL_BANDWIDTH] = "Bandwidth"
        HEADERS[COL_SSB_SCS] = "SSB SCS"
        HEADERS[COL_DL_FREQ] = "Frequency"
        HEADERS[COL_DL_ARFCN] = "ARFCN"
        HEADERS[COL_SCS] = "SCS"

        SER_PARAMS = [
            (COL_PCI, re.compile(r"nr_servingbeam_pci_(\d+)")),
            (COL_BEAM_ID, re.compile(r"nr_servingbeam_ssb_index_(\d+)")),
            (COL_RSRP, re.compile(r"nr_servingbeam_ss_rsrp_(\d+)")),
            (COL_RSRQ, re.compile(r"nr_servingbeam_ss_rsrq_(\d+)")),
            (COL_SINR, re.compile(r"nr_servingbeam_ss_sinr_(\d+)")),
            (COL_BAND, re.compile(r"nr_band_(\d+)")),
            (COL_BAND_TYPE, re.compile(r"nr_band_type_(\d+)")),
            (COL_BANDWIDTH, re.compile(r"nr_bw_(\d+)")),
            (COL_SSB_SCS, re.compile(r"nr_ssb_scs_(\d+)")),
            (COL_DL_FREQ, re.compile(r"nr_dl_frequency_(\d+)")),
            (COL_DL_ARFCN, re.compile(r"nr_dl_arfcn_(\d+)")),
            (COL_SCS, re.compile(r"nr_numerology_scs_(\d+)")),
        ]

        DET_PARAMS = [
            (COL_PCI, re.compile(r"nr_detectedbeam(\d+)_pci")),
            (COL_BEAM_ID, re.compile(r"nr_detectedbeam(\d+)_ssb_index")),
            (COL_RSRP, re.compile(r"nr_detectedbeam(\d+)_ss_rsrp")),
            (COL_RSRQ, re.compile(r"nr_detectedbeam(\d+)_ss_rsrq")),
            (COL_SINR, re.compile(r"nr_detectedbeam(\d+)_ss_sinr")),
        ]

        query = QSqlQuery()

        queryString = """
        SELECT
        *
        FROM 
        nr_cell_meas 
        WHERE 
        time <= '%s'
        ORDER BY time DESC
        LIMIT 1
        """ % (self.timeFilter)

        serv_list = [None] * MAX_SERVING
        for i in range(MAX_SERVING):
            serv_list[i] = [""] * len(HEADERS)

        det_list = [None] * MAX_DETECTED
        for i in range(MAX_DETECTED):
            det_list[i] = [""] * len(HEADERS)

        query.exec_(queryString)
        record = query.record()
        if query.first():
            for i in range(record.count()):
                field_name = record.fieldName(i)
                value = query.value(i)
                if self.try_to_set_field_value(field_name, value, SER_PARAMS, serv_list):
                    continue
                else:
                    self.try_to_set_field_value(
                        field_name, value, DET_PARAMS, det_list)

        time_row = [""] * len(HEADERS)
        time_row[0] = "Time"
        time_row[1] = self.timeFilter
        dataList.append(time_row)
        serving_header_row = [""] * len(SER_PARAMS)
        serving_header_row[0] = "Serving:"
        dataList.append(serving_header_row)
        dataList = dataList + serv_list

        detectected_header_row = [""] * len(SER_PARAMS)
        detectected_header_row[0] = "Detected:"
        dataList.append(detectected_header_row)
        dataList = dataList + det_list

        self.closeConnection()
        return (HEADERS, dataList)

    def try_to_set_field_value(self, field_name, value, params_tuple, result_list):
        for param in params_tuple:
            (field_index, param_test) = param
            m = param_test.match(field_name)
            if(m):
                arg = int(m.group(1)) - 1
                row = result_list[arg]
                row[field_index] = str(value or "")
                return True
        return False

    def defaultData(self, fieldsList, dataList):
        fieldCount = len(fieldsList)
        if fieldCount > 0:
            for index in range(fieldCount):
                columnName = fieldsList[index]
                dataList.append([columnName, "", "", ""])
            return dataList

    def openConnection(self):
        if self.azenqosDatabase is not None:
            self.azenqosDatabase.open()

    def closeConnection(self):
        self.azenqosDatabase.close()
