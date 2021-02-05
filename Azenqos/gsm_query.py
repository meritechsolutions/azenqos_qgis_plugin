from PyQt5.QtSql import QSqlQuery, QSqlDatabase
import pandas as pd
import params_disp_df


class GsmDataQuery:
    def __init__(self, database, currentDateTimeString):
        self.timeFilter = ""
        self.azenqosDatabase = database
        if currentDateTimeString:
            self.timeFilter = currentDateTimeString

    def getRadioParameters(self):
        self.openConnection()
        dataList = []
        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)
            dataList.append(["Time", self.timeFilter, ""])
        gcmFieldList = ["RxLev", "RxQual"]
        gcmQueryString = (
            """SELECT gsm_rxlev_full_dbm || ' ' || gsm_rxlev_sub_dbm as "RxLev", gsm_rxqual_full || ' ' || gsm_rxqual_sub as "RxQual" FROM gsm_cell_meas %s ORDER BY time DESC LIMIT 1"""
            % (condition)
        )
        gcmQuery = QSqlQuery()
        queryStatus = gcmQuery.exec_(gcmQueryString)
        if queryStatus:
            hasData = gcmQuery.first()
            if hasData:
                for field in gcmFieldList:
                    fullValue = ""
                    subValue = ""
                    if field in ["RxLev", "RxQual"]:
                        if gcmQuery.value(field):
                            splitValue = gcmQuery.value(field).split(" ")
                            fullValue = splitValue[0] or ""
                            subValue = splitValue[1] or ""
                    dataList.append([field, fullValue, subValue])
            else:
                for field in gcmFieldList:
                    fullValue = ""
                    subValue = ""
                    dataList.append([field, fullValue, subValue])

        elementDictList = [
            {"element": "TA", "table": "gsm_tx_meas", "column": 'gsm_ta as "TA"'},
            {
                "element": "RLT (Max)",
                "table": "gsm_rl_timeout_counter",
                "column": 'gsm_radiolinktimeout_max as "RLT (Max)"',
            },
            {
                "element": "RLT (Current)",
                "table": "gsm_rlt_counter",
                "column": 'gsm_radiolinktimeout_current as "RLT (Current)"',
            },
            {
                "element": "DTX Used",
                "table": "gsm_rr_measrep_params",
                "column": 'gsm_dtxused as "DTX Used"',
            },
            {
                "element": "TxPower",
                "table": "gsm_tx_meas",
                "column": 'gsm_txpower as "TxPower"',
            },
            {"element": "FER", "table": "vocoder_info", "column": 'gsm_fer as "FER"'},
        ]
        for dic in elementDictList:
            element = dic["element"]
            column = dic["column"]
            table = dic["table"]
            if element and column and table:
                queryString = """SELECT %s
                                FROM %s
                                %s
                                ORDER BY time DESC
                                LIMIT 1""" % (
                    column,
                    table,
                    condition,
                )
                query = QSqlQuery()
                queryStatus = query.exec_(queryString)
                if queryStatus:
                    hasData = query.first()
                    value = ""
                    if query.value(element):
                        value = query.value(element)
                    dataList.append([element, value, ""])
        self.closeConnection()
        return dataList

    def getServingAndNeighbors(self):
        self.openConnection()
        dataList = []
        fieldsList = [
            "Cellname",
            "LAC",
            "BSIC",
            "ARFCN",
            "RxLev",
            "C1",
            "C2",
            "C31",
            "C32",
        ]
        selectedColumns = " gsm_cellfile_matched_cellname, gsm_lac, gsm_bsic, gsm_arfcn_bcch, gsm_rxlev_full_dbm, gsm_c1, gsm_c2, gsm_c31, gsm_c32"
        condition = ""
        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)
        dataList.append([self.timeFilter, "", "", "", "", "", "", "", "", ""])
        temp = []
        queryString = None
        elementDictList = [
            {
                "element": "Cellname",
                "name": "gcm",
                "table": "gsm_cell_meas",
                "column": "gsm_cellfile_matched_cellname",
                "join": [
                    {
                        "element": "LAC",
                        "name": "gsci",
                        "table": "gsm_serv_cell_info",
                        "column": "gsm_lac ",
                    },
                    {
                        "element": "BSIC,ARFCN,RxLev,C1,C2,C31,C32",
                        "name": "gcm2",
                        "table": "gsm_cell_meas",
                        "column": "gsm_bsic, gsm_arfcn_bcch, gsm_rxlev_full_dbm, gsm_c1, gsm_c2, gsm_c31, gsm_c32 ",
                    },
                ],
            }
        ]

        for dic in elementDictList:
            temp = []
            name = dic["name"]
            element = dic["element"]
            mainElement = dic["element"]
            mainColumn = dic["column"]
            subColumn = dic["column"]
            table = dic["table"]
            join = None
            joinString = ""
            onString = ""
            if not len(dic["join"]) == 0:
                for join in dic["join"]:
                    onString = """ON %s.row_num = %s.row_num""" % (name, join["name"],)
                    joinString += """LEFT JOIN ( SELECT %s,1 as row_num 
                                            FROM %s 
                                            %s 
                                            ORDER BY time DESC 
                                            LIMIT 1 
                                        ) %s
                                        %s """ % (
                        join["column"],
                        join["table"],
                        condition,
                        join["name"],
                        onString,
                    )

                    mainColumn += ",%s" % join["column"]
                    mainElement += ",%s" % join["element"]

            if element and mainColumn and table:
                queryString = """SELECT %s
                                FROM ( SELECT %s,1 as row_num
                                        FROM %s 
                                        %s 
                                        ORDER BY time DESC 
                                        LIMIT 1 
                                    ) %s
                                %s 
                                """ % (
                    mainColumn,
                    subColumn,
                    table,
                    condition,
                    name,
                    joinString,
                )
                query = QSqlQuery()
                query.exec_(queryString)
                elements = mainElement.split(",")
                if query.first():
                    for i in range(0, len(elements)):
                        temp.append(
                            "" if str(query.value(i)) == "NULL" else query.value(i)
                        )
                else:
                    for elem in elements:
                        temp.append("")
            if not all(v == "" for v in temp):
                temp.insert(0, "")
                dataList.append(temp)
        self.closeConnection()
        return dataList

    def getCurrentChannel(self):
        self.openConnection()

        dataList = []
        condition = ""
        gsmFields = [
            {
                "element": "Cellname",
                "column": 'gsm_cellfile_matched_cellname as "Cellname"',
                "table": "gsm_cell_meas",
            },
            {"element": "CGI", "column": 'gsm_cgi as "CGI"', "table": "gsm_cell_meas"},
            {
                "element": "Channel type",
                "column": 'gsm_channeltype as "Channel type"',
                "table": "gsm_rr_chan_desc",
            },
            {
                "element": "Sub channel number",
                "column": 'gsm_subchannelnumber as "Sub channel number"',
                "table": "gsm_rr_subchan",
            },
            {
                "element": "Mobile Allocation Index Offset (MAIO)",
                "column": 'gsm_maio as "Mobile Allocation Index Offset (MAIO)"',
                "table": "gsm_rr_chan_desc",
            },
            {
                "element": "Hopping Sequence Number (HSN)",
                "column": 'gsm_hsn as "Hopping Sequence Number (HSN)"',
                "table": "gsm_rr_chan_desc",
            },
            {
                "element": "Cipering Algorithm",
                "column": 'gsm_cipheringalgorithm as "Cipering Algorithm"',
                "table": "gsm_rr_cipher_alg",
            },
            {
                "element": "MS Power Control Level",
                "column": 'gsm_ms_powercontrollevel as "MS Power Control Level"',
                "table": "gsm_rr_power_ctrl",
            },
            {
                "element": "Channel Mode",
                "column": 'gsm_channelmode as "Channel Mode"',
                "table": "gsm_chan_mode",
            },
            {
                "element": "Speech Codec TX",
                "column": 'gsm_speechcodectx as "Speech Codec TX"',
                "table": "vocoder_info",
            },
            {
                "element": "Speech Codec RX",
                "column": 'gsm_speechcodecrx as "Speech Codec RX"',
                "table": "vocoder_info",
            },
            {
                "element": "Hopping Channel",
                "column": 'gsm_hoppingchannel as "Hopping Channel"',
                "table": "gsm_rr_chan_desc",
            },
            {
                "element": "Hopping Frequencies",
                "column": 'gsm_hoppingfrequencies as "Hopping Frequencies"',
                "table": "gsm_hopping_list",
            },
            {
                "element": "ARFCN BCCH",
                "column": 'gsm_arfcn_bcch as "ARFCN BCCH"',
                "table": "gsm_cell_meas",
            },
            {
                "element": "ARFCN TCH",
                "column": 'gsm_arfcn_tch as "ARFCN TCH"',
                "table": "gsm_rr_chan_desc",
            },
            {
                "element": "Time slot",
                "column": 'gsm_timeslot as "Time slot"',
                "table": "gsm_rr_chan_desc",
            },
        ]

        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)
            dateString = "%s" % (self.timeFilter)

        dataList.append(["Time", self.timeFilter])
        for dic in gsmFields:
            element = dic["element"]
            column = dic["column"]
            table = dic["table"]
            if element and column and table:
                queryString = """ SELECT %s
                                FROM %s
                                %s
                                ORDER BY time DESC
                                LIMIT 1 """ % (
                    column,
                    table,
                    condition,
                )
                query = QSqlQuery()
                queryStatus = query.exec_(queryString)
                if queryStatus:
                    firstRow = query.first()
                    value = query.value(element) or ""
                    dataList.append([element, value])

        self.closeConnection()
        return dataList

    def getCSlashI(self):
        self.openConnection()
        dataList = []
        condition = ""
        maxUnits = 10

        if self.timeFilter:
            condition = "WHERE time <= '%s'" % (self.timeFilter)
        dataList.append([self.timeFilter, "", ""])
        queryString = """SELECT gsm_coi_avg, gsm_coi_worst
                        FROM gsm_coi_per_chan
                        %s
                        ORDER BY time DESC
                        LIMIT 1""" % (
            condition
        )
        query = QSqlQuery()
        query.exec_(queryString)
        while query.next():

            dataList.append(["Worst", query.value("gsm_coi_worst"), ""])
            dataList.append(["Avg", query.value("gsm_coi_avg"), ""])

        for unit in range(1, maxUnits):
            column = "gsm_coi_arfcn_%s, gsm_coi_%s" % (unit, unit)
            queryString = """SELECT %s
                            FROM gsm_coi_per_chan
                            %s
                            ORDER BY time DESC
                            LIMIT 1""" % (
                column,
                condition,
            )
            query = QSqlQuery()
            queryStatus = query.exec_(queryString)
            if queryStatus:
                firstRow = query.first()
                if query.value(0) or query.value(1):
                    dataList.append(
                        ["", query.value(0) or "", query.value(1) or "",]
                    )
        self.closeConnection()
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


################################## df get functions


def get_gsm_radio_params_disp_df(dbcon, time_before):
    df_list = []
    parameter_to_columns_list = [
        (
            ["Time", "RxLev Full", "RxLev Sub", "RxQual Full", "RxQual Sub",],
            [
                "time," "gsm_rxlev_full_dbm",
                "gsm_rxlev_sub_dbm",
                "gsm_rxqual_full",
                "gsm_rxqual_sub",
            ],
            "gsm_cell_meas",
        ),
        ("TA", ["gsm_ta"], "gsm_tx_meas"),
        ("RLT (Max)", ["gsm_radiolinktimeout_max"], "gsm_rl_timeout_counter"),
        ("RLT (Current)", ["gsm_radiolinktimeout_current"], "gsm_rlt_counter"),
        ("DTX Used", ["gsm_dtxused"], "gsm_rr_measrep_params"),
        ("TxPower", ["gsm_txpower"], "gsm_tx_meas"),
        ("FER", ["gsm_fer"], "vocoder_info"),
    ]
    df = params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        not_null_first_col=False,
        custom_lookback_dur_millis=gc.DEFAULT_LOOKBACK_DUR_MILLIS,
    )
    df.columns = ["Parameter", "Value"]
    df_list.append(df)

    final_df = pd.concat(df_list, sort=False)
    return final_df


def get_gsm_serv_and_neigh__df(dbcon, time_before):
    df_list = []

    cell_col_prefix_renamed = [
        "Cell Name",
        "BSIC",
        "ARFCN ",
        "RxLev",
        "C1",
        "C2",
        "C31",
        "C32",
    ]
    serv_col_prefix_sr = pd.Series(
        [
            "gsm_cellfile_matched_cellname",
            "gsm_bsic",
            "gsm_arfcn_bcch",
            "gsm_rxlev_sub_dbm",
            "gsm_c1",
            "gsm_c2",
            "gsm_c31",
            "gsm_c32",
        ]
    )
    parameter_to_columns_list = [
        ("serv", list(serv_col_prefix_sr),),
    ]
    df = params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        default_table="gsm_cell_meas",
        not_null_first_col=False,
        custom_lookback_dur_millis=gc.DEFAULT_LOOKBACK_DUR_MILLIS,
    )
    df.columns = ["CellGroup"] + cell_col_prefix_renamed
    df_list.append(df)

    lac_col_prefix_sr = pd.Series(["gsm_lac",])
    parameter_to_columns_list = [
        ("serv", list(lac_col_prefix_sr),),
    ]
    df2 = params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        default_table="gsm_serv_cell_info",
        not_null_first_col=False,
        custom_lookback_dur_millis=gc.DEFAULT_LOOKBACK_DUR_MILLIS,
    )
    df2.columns = ["CellGroup", "LAC"]
    df.insert(2, "LAC", df2["LAC"])

    neigh_col_prefix_sr = pd.Series(
        [
            "gsm_cellfile_matched_neighbor_cellname",
            "gsm_cellfile_matched_neighbor_lac_",
            "gsm_neighbor_bsic_",
            "gsm_neighbor_arfcn_",
            "gsm_neighbor_rxlev_dbm_",
            "gsm_neighbor_c1_",
            "gsm_neighbor_c2_",
            "gsm_neighbor_c31_",
            "gsm_neighbor_c32_",
        ]
    )
    neigh_n_param = 32

    def name_map(x, y):
        if x == "gsm_cellfile_matched_neighbor_cellname":
            if y == 0:
                return "gsm_cellfile_matched_neighbor_cellname"
            else:
                return '"" as unsed_{}'.format(y + 1)
        return x + "{}".format(y + 1)

    neigh = sum(
        map(
            lambda y: list(map(lambda x: name_map(x, y), neigh_col_prefix_sr)),
            range(neigh_n_param),
        ),
        [],
    )
    parameter_to_columns_list = [
        (list(map(lambda x: "neigh{}".format(x + 1), range(neigh_n_param))), neigh,),
    ]
    df = params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        default_table="gsm_cell_meas",
        not_null_first_col=False,
        custom_lookback_dur_millis=gc.DEFAULT_LOOKBACK_DUR_MILLIS,
    )
    df.columns = [
        "CellGroup",
        "Cell Name",
        "LAC",
        "BSIC",
        "ARFCN ",
        "RxLev",
        "C1",
        "C2",
        "C31",
        "C32",
    ]
    df_list.append(df)

    final_df = pd.concat(df_list, sort=False)
    return final_df


def get_gsm_current_channel_disp_df(dbcon, time_before):
    df_list = []
    parameter_to_columns_list = [
        (
            ["Time", "Cellname", "CGI",],
            ["time," "gsm_cellfile_matched_cellname", "gsm_cgi",],
            "gsm_cell_meas",
        ),
        ("Channel Type", ["gsm_channeltype"], "gsm_rr_chan_desc"),
        ("Sub Channel Number", ["gsm_subchannelnumber"], "gsm_rr_subchan"),
        (
            ["Mobile Allocation Index Offset (MAIO)", "Hopping Sequence Number (HSN)"],
            ["gsm_maio", "gsm_hsn"],
            "gsm_rr_chan_desc",
        ),
        ("Cipering Algorithm", ["gsm_cipheringalgorithm"], "gsm_rr_cipher_alg"),
        ("MS Power Control Level", ["gsm_ms_powercontrollevel"], "gsm_rr_power_ctrl"),
        ("Channel Mode", ["gsm_channelmode"], "gsm_chan_mode"),
        (
            ["Speech Codec TX", "Speech Codec RX"],
            ["gsm_speechcodectx", "gsm_speechcodecrx"],
            "vocoder_info",
        ),
        ("Hopping Frequencies", ["gsm_hoppingfrequencies"], "gsm_hopping_list"),
        ("ARFCN BCCH", ["gsm_arfcn_bcch"], "gsm_cell_meas"),
        ("ARFCN TCH", ["gsm_arfcn_tch"], "gsm_rr_chan_desc"),
        ("Time Slot", ["gsm_timeslot"], "gsm_rr_chan_desc"),
    ]
    df = params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        not_null_first_col=False,
        custom_lookback_dur_millis=gc.DEFAULT_LOOKBACK_DUR_MILLIS,
    )
    df.columns = ["Parameter", "Value"]
    df_list.append(df)

    final_df = pd.concat(df_list, sort=False)
    return final_df


def get_coi_df(dbcon, time_before):
    df_list = []

    cell_col_prefix_renamed = ["ARFCN", "VALUE"]
    worst_col_prefix_sr = pd.Series(["gsm_coi_worst_arfcn_1", "gsm_coi_worst"])
    parameter_to_columns_list = [
        ("Time", ["time"]),
        ("Worst", list(worst_col_prefix_sr),),
    ]
    df = params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        default_table="gsm_coi_per_chan",
        not_null_first_col=True,
        custom_lookback_dur_millis=gc.DEFAULT_LOOKBACK_DUR_MILLIS,
    )
    df.columns = ["CellGroup"] + cell_col_prefix_renamed
    df_list.append(df)

    avg_col_prefix_sr = pd.Series(["gsm_coi_arfcn_", "gsm_coi_"])
    avg_n_param = 32

    avg = sum(
        map(
            lambda y: list(map(lambda x: x + "{}".format(y + 1), avg_col_prefix_sr)),
            range(avg_n_param),
        ),
        [],
    )
    parameter_to_columns_list = [
        ("Avg", ['""']),
        (list(map(lambda x: "", range(avg_n_param))), avg,),
    ]
    df = params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        default_table="gsm_coi_per_chan",
        not_null_first_col=True,
        custom_lookback_dur_millis=gc.DEFAULT_LOOKBACK_DUR_MILLIS,
    )
    df.columns = ["CellGroup"] + cell_col_prefix_renamed
    df_list.append(df)

    final_df = pd.concat(df_list, sort=False)
    return final_df
