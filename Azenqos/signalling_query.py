from PyQt5.QtSql import QSqlQuery, QSqlDatabase
import pandas as pd
import global_config as gc
import params_disp_df


class SignalingDataQuery:
    def __init__(self, database, currentDateTimeString):
        self.timeFilter = ""
        self.azenqosDatabase = database
        if currentDateTimeString:
            self.timeFilter = currentDateTimeString

    def getEvents(self, pd_mode=True):
        if pd_mode:
            df = pd.read_sql(
                "SELECT ev.time, ev.name, ev.info FROM events ev UNION ALL SELECT pm.time, 'MOS Score' as name, CAST(pm.polqa_mos AS CHAR) FROM polqa_mos pm WHERE pm.polqa_mos IS NOT NULL ORDER BY time",
                gc.dbcon,
                # parse_dates=["time"], after comment millisecond of time is 3 decimals
            )
            return df

        self.openConnection()
        queryString = "SELECT ev.time, ev.name, ev.info FROM events ev UNION ALL SELECT pm.time, 'MOS Score' as name, CAST(pm.polqa_mos AS CHAR) FROM polqa_mos pm WHERE pm.polqa_mos IS NOT NULL ORDER BY time"
        query = QSqlQuery()
        query.exec_(queryString)
        timeField = query.record().indexOf("time")
        nameField = query.record().indexOf("name")
        detailField = query.record().indexOf("info")
        dataList = []
        while query.next():
            timeValue = query.value(timeField)
            nameValue = query.value(nameField)
            detailStrValue = query.value(detailField)
            dataList.append([timeValue, "", "MS1", nameValue, detailStrValue])
        self.closeConnection()
        return dataList

    """
    def getLayerOneMessages(self, pd_mode=True):  ##ต้องแก้ query
        if pd_mode:
            df = pd.read_sql(
                "SELECT time, name, info FROM events", gc.dbcon, parse_dates=["time"]
            )
            return df

        self.openConnection()
        query = QSqlQuery()
        query.exec_("SELECT * FROM events")
        timeField = query.record().indexOf("time")
        nameField = query.record().indexOf("name")
        detailField = query.record().indexOf("info")
        dataList = []
        while query.next():
            timeValue = query.value(timeField)
            nameValue = query.value(nameField)
            detailStrValue = query.value(detailField)
            dataList.append([timeValue, "", "MS1", nameValue, detailStrValue])
        self.closeConnection()
        return dataList
        """

    def getLayerThreeMessages(self, pd_mode=True):
        if pd_mode:
            df = pd.read_sql(
                "SELECT time, name, symbol, protocol, detail_str FROM signalling",
                gc.dbcon,
                # parse_dates=["time"], after comment millisecond of time is 3 decimals
            )
            return df

        self.openConnection()
        query = QSqlQuery()
        query.exec_("SELECT time, name, symbol, protocol, detail_str FROM signalling")
        timeField = query.record().indexOf("time")
        nameField = query.record().indexOf("name")
        symbolField = query.record().indexOf("symbol")
        detailField = query.record().indexOf("detail_str")
        protocolField = query.record().indexOf("protocol")
        dataList = []
        while query.next():
            timeValue = query.value(timeField)
            nameValue = query.value(nameField)
            symbolValue = query.value(symbolField)
            detailStrValue = query.value(detailField)
            protocolValue = query.value(protocolField)
            # detailStrValue = query.value(detailField).split(",")
            # if detailStrValue[0].startswith("LTE") == True:
            #     detailStrValue = "LTE RRC"
            # else:
            #     detailStrValue = ""
            # if detailStrValue != "":
            #     dataList.append(
            #         [timeValue, symbolValue, "MS1", detailStrValue, nameValue, ""]
            #     )
            dataList.append(
                [
                    timeValue,
                    symbolValue,
                    "MS1",
                    protocolValue,
                    nameValue,
                    detailStrValue,
                ]
            )
        self.closeConnection()
        return dataList

    def getBenchmark(self):
        self.openConnection()
        dataList = []
        condition = ""

        # Voice section (ยังไม่มีข้อมูลใน database)
        dataList.append(["---- Voice ----", "", "", "", ""])
        dataList.append(["Call Count", 0, 0, 0, 0])
        dataList.append(["Drop Count", 0, 0, 0, 0])
        dataList.append(["Block Count", 0, 0, 0, 0])
        dataList.append(["Handover Fail Count", 0, 0, 0, 0])

        # LTE section
        lteField = [
            "---- LTE ----",
            "SINR Rx[0][1]",
            "SINR RX[1][1]",
            "Inst RSRP[1]",
            "Inst RSRQ[1]",
            "Inst RSSI",
            "Cell ID",
            "Cell Name",
        ]
        if self.timeFilter:
            condition = "WHERE lcm.time <= '%s'" % (self.timeFilter)
        queryString = """SELECT '' as header,lcm.lte_sinr_rx0_1,lcm.lte_sinr_rx1_1,lcm.lte_inst_rsrp_1,lcm.lte_inst_rsrq_1,
                         lcm.lte_inst_rssi_1,lsci.lte_serv_cell_info_eci,lsci.lte_serv_cell_info_cellname
                         FROM lte_cell_meas lcm
                         LEFT JOIN lte_serv_cell_info lsci ON lcm.time = lsci.time
                         %s
                         ORDER BY lcm.time DESC LIMIT 1""" % (
            condition
        )
        query = QSqlQuery()
        query.exec_(queryString)
        for field in range(len(lteField)):
            dataList.append([lteField[field], "", "", "", ""])
        while query.next():
            for field in range(len(lteField)):
                if query.value(field):
                    dataList[field + 5][1] = query.value(field)
                    # dataList.append(
                    #     [lteField[field],
                    #      query.value(field), '', '', ''])
                else:
                    dataList[field + 5][1] = ""
                    # dataList.append([lteField[field], '', '', '', ''])

        # WCDMA section
        wcdmaField = [
            "---- WCDMA ----",
            "ASET Ec/Io Avg.",
            "ASET RSCP Avg.",
            "RSSI",
            "BLER Avg.",
            "Cell ID",
            "Cell Name",
        ]
        if self.timeFilter:
            condition = "WHERE wcm.time <= '%s'" % (self.timeFilter)
        queryString = """SELECT '' as header,wcm.wcdma_aset_ecio_avg,wcm.wcdma_aset_rscp_avg,wrp.wcdma_rssi,
                         wb.wcdma_bler_average_percent_all_channels,wici.wcdma_cellid, '' as cellname
                         FROM wcdma_cell_meas wcm
                         LEFT JOIN wcdma_rx_power wrp ON wcm.time = wrp.time
                         LEFT JOIN wcdma_bler wb ON wcm.time = wb.time
                         LEFT JOIN wcdma_idle_cell_info wici ON wcm.time = wici.time
                         %s
                         ORDER BY wcm.time DESC LIMIT 1""" % (
            condition
        )
        # ยังหา WCDMA Cellname ไม่เจอ

        # Real Query Code (รันไม่ได้เพราะ no data in DB)
        # -----------------------------------------------
        # query = QSqlQuery()
        # query.exec_(queryString)
        # while query.next():
        #     for field in range(len(wcdmaField)):
        #         if query.value(field):
        #             dataList.append([wcdmaField[field],query.value(field),'','',''])
        #         else:
        #             dataList.append([wcdmaField[field],'','','',''])

        # Table Ui Test for WCDMA section
        for field in range(len(wcdmaField)):
            dataList.append([wcdmaField[field], "", "", "", ""])

        # #Data Section
        dataField = [
            "---- Data ----",
            "DL Application Throughput",
            "UL Application Throughput",
        ]
        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)
        queryString = """SELECT '' as header,data_app_dl_throughput_1,data_app_ul_throughput_1
                            FROM data_app_throughput
                            %s
                            ORDER BY time DESC LIMIT 1""" % (
            condition
        )

        # Real Query Code (รันไม่ได้เพราะ no data in DB)
        # -----------------------------------------------
        # query = QSqlQuery()
        # query.exec_(queryString)
        # while query.next():
        #     for field in range(len(dataField)):
        #         if query.value(field):
        #             dataList.append([dataField[field],query.value(field),'','',''])
        #         else:
        #             dataList.append([dataField[field],'','','',''])

        # Table Ui Test for Data section
        for field in range(len(dataField)):
            dataList.append([dataField[field], "", "", "", ""])
        #'Data Connect Fail Count','Download Timeout'
        dataList.append(["Data Connect Fail Count", 0, 0, 0, 0])
        dataList.append(["Download Timeout", 0, 0, 0, 0])

        # LTE RLC section
        lte_rlcField = ["---- LTE ----", "RLC DL Thoughput", "RLC UL Thoughput"]
        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)
        queryString = """SELECT '' as header,lte_rlc_dl_tp,lte_rlc_ul_tp
                         FROM lte_rlc_stats
                         %s
                         ORDER BY time DESC LIMIT 1""" % (
            condition
        )

        query = QSqlQuery()
        query.exec_(queryString)
        for field in range(len(lte_rlcField)):
            dataList.append([lte_rlcField[field], "", "", "", ""])
        while query.next():
            for field in range(len(lte_rlcField)):
                if query.value(field):
                    dataList[field + 25][1] = query.value(field)
                # dataList.append(
                #     [lte_rlcField[field],
                #      query.value(field), '', '', ''])
                else:
                    dataList[field + 25][1] = query.value(field)
                #     dataList.append([lte_rlcField[field], '', '', '', ''])

        # WCDMA RLC section
        wcdma_rlcField = [
            "---- WCDMA ----",
            "HS-DSCH Throughput",
            "WCDMA RLC DL Thoughput",
            "WCDMA RLC UL Thoughput",
        ]
        if self.timeFilter:
            condition = "WHERE whs.time <= '%s'" % (self.timeFilter)
        queryString = """SELECT '' as header,whs.data_hsdpa_thoughput,dwrs.data_wcdma_rlc_dl_throughput,
                         dwrs.data_wcdma_rlc_ul_throughput
                         FROM wcdma_hsdpa_stats whs
                         LEFT JOIN data_wcdma_rlc_stats dwrs ON whs.time = dwrs.time
                         %s
                         ORDER BY whs.time DESC LIMIT 1""" % (
            condition
        )

        # Real Query Code (รันไม่ได้เพราะ no data in DB)
        # -----------------------------------------------
        # query = QSqlQuery()
        # query.exec_(queryString)
        # while query.next():
        #     for field in range(len(wcdma_rlcField)):
        #         if query.value(field):
        #             dataList.append([wcdma_rlcField[field],query.value(field),'','',''])
        #         else:
        #             dataList.append([wcdma_rlcField[field],'','','',''])

        # Table Ui Test for Data section
        for field in range(len(wcdma_rlcField)):
            dataList.append([wcdma_rlcField[field], "", "", "", ""])

        self.closeConnection()
        return dataList

    def getMmRegStates(self):
        self.openConnection()
        dataList = []
        fieldsList = [
            "Time",
            "MM State",
            "MM Substate",
            "MM Update Status",
            "MM Network Operation Mode",
            "MM Service Type",
            "MM MCC",
            "MM MNC",
            "MM Lac",
            "MM Rai",
            "REG State",
            "REG UE Operation Mode",
            "GMM State",
            "GMM Substate",
            "GMM Update",
        ]
        selectedColumns = """ms.time,ms.mm_state_state,ms.mm_state_substate,ms.mm_state_update_status,
                             ms.mm_characteristics_network_operation_mode,ms.mm_characteristics_service_type,
                             ms.mm_characteristics_mcc,ms.mm_characteristics_mnc,ms.mm_characteristics_lac,ms.mm_characteristics_rai,
                             rs.reg_state_state,rs.reg_state_ue_operation_mode,gs.gmm_state_state,gs.gmm_state_substate,gs.gmm_state_update"""
        condition = ""
        if self.timeFilter:
            condition = "WHERE ms.time <= '%s'" % (self.timeFilter)
        queryString = """SELECT %s FROM mm_state ms
                        LEFT JOIN reg_state rs ON ms.time = rs.time
                        LEFT JOIN gmm_state gs ON ms.time = gs.time
                        %s
                        ORDER BY ms.time DESC LIMIT 1""" % (
            selectedColumns,
            condition,
        )
        query = QSqlQuery()
        query.exec_(queryString)
        queryRowCount = query.record().count()
        for field in range(len(fieldsList)):
            dataList.append([fieldsList[field], ""])
        while query.next():
            for field in range(len(fieldsList)):
                if query.value(field):
                    dataList[field][1] = query.value(field)
                    # dataList.append(
                    #     [fieldsList[field],
                    #      query.value(field)])
        self.closeConnection()
        return dataList

    def getServingSystemInfo(self):
        self.openConnection()
        dataList = []
        fieldsList = [
            "Time",
            "mcc",
            "mnc",
            "lac",
            "service status",
            "service domain",
            "service capability",
            "system mode",
            "roaming status",
            "system id type",
        ]
        selectedColumns = "time,serving_system_mcc,serving_system_mnc,serving_system_lac,cm_service_status,cm_service_domain,cm_service_capability,cm_system_mode,cm_roaming_status,cm_system_id_type"
        condition = ""
        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)
        queryString = "select %s from serving_system %s order by time desc limit 1" % (
            selectedColumns,
            condition,
        )
        query = QSqlQuery()
        query.exec_(queryString)
        for field in range(len(fieldsList)):
            dataList.append([fieldsList[field], ""])
        while query.next():
            for field in range(len(fieldsList)):
                if query.value(field):
                    if field == 0:
                        dataList[field][1] = self.timeFilter
                        # dataList.append([fieldsList[field], self.timeFilter])
                    else:
                        dataList[field][1] = query.value(field)
                        # dataList.append(
                        #     [fieldsList[field],
                        #      query.value(field)])
                else:
                    dataList[field][1] = ""
                    # dataList.append([fieldsList[field], ''])
        self.closeConnection()
        return dataList

    def getDebugAndroidEvent(self):  # ยังไม่มีข้อมูลใน database

        self.openConnection()
        # query = QSqlQuery()
        # query.exec_("select * from events")
        # timeField = query.record().indexOf("time")
        # nameField = query.record().indexOf("name")
        # detailField = query.record().indexOf("info")
        dataList = []
        # while query.next():
        #     timeValue = query.value(timeField)
        #     nameValue = query.value(nameField)
        #     detailStrValue = query.value(detailField)
        #     dataList.append([timeValue, '', 'MS1', nameValue, detailStrValue])
        self.closeConnection()

        fieldsList = [
            "Time",
            "Device Time Stamp",
            "Raw Layer Message",
            "Processed Event",
        ]
        fieldCount = len(fieldsList)
        dataList.append(["Time", self.timeFilter])
        for index in range(1, len(fieldsList)):
            columnName = fieldsList[index]
            dataList.append([columnName, ""])
        return dataList

    def openConnection(self):
        if self.azenqosDatabase is not None:
            self.azenqosDatabase.open()

    def closeConnection(self):
        self.azenqosDatabase.close()

    def defaultData(self, fieldsList):
        fieldCount = len(fieldsList)
        if fieldCount > 0:
            dataList = []
            for index in range(fieldCount):
                columnName = fieldsList[index]
                value = ""
                dataList.append([columnName, value, "", ""])
            return dataList
