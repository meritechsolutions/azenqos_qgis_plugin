import os
import sys
import traceback
import uuid
import xml.etree.ElementTree as xet
import struct
import datetime

import pandas as pd
import numpy as np

import azq_theme_manager
import azq_utils
import preprocess_azm
import system_sql_query

elm_table_main_col_types = {
    "log_hash": "BIGINT",
    "time": "TEXT",
    "seqid": "INT",
    "posid": "INT",
    "geom": "BLOB",
    "event_id": "INT",
    "msg_id": "INT",
    "name": "TEXT",
    "symbol": "TEXT",
    "protocol": "TEXT",    
    "info": "TEXT",
    "detail": "TEXT",
    "detail_hex": "TEXT",
    "detail_str": "TEXT",
}

def prepare_spatialite_required_tables(dbcon):
    dbcon.execute(
        """
        CREATE TABLE IF NOT EXISTS spatial_ref_sys (srid INTEGER NOT NULL PRIMARY KEY,auth_name VARCHAR(256) NOT NULL,auth_srid INTEGER NOT NULL,ref_sys_name VARCHAR(256),proj4text VARCHAR(2048) NOT NULL);
        """
    )

    try:
        dbcon.execute(
            """
            INSERT INTO spatial_ref_sys VALUES(4326,'epsg',4326,'WGS 84','+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs');
            """
        )
    except Exception as ex:
        type_, value_, traceback_ = sys.exc_info()
        exstr = str(traceback.format_exception(type_, value_, traceback_))
        if "UNIQUE constraint failed" in exstr:
            pass
        else:
            print("ERROR: insert failed with exception: %s", exstr)
            raise ex

    dbcon.execute(
        """
        CREATE TABLE IF NOT EXISTS geometry_columns (f_table_name VARCHAR(256) NOT NULL,f_geometry_column VARCHAR(256) NOT NULL,type VARCHAR(30) NOT NULL,coord_dimension INTEGER NOT NULL,srid INTEGER,spatial_index_enabled INTEGER NOT NULL);
        """
    )

    dbcon.execute(
        """
        delete from geometry_columns where true;
        """
    )

    dbcon.execute(
        """CREATE TABLE IF NOT EXISTS 'layer_styles' ( "id" INTEGER PRIMARY KEY AUTOINCREMENT, 'f_table_catalog' VARCHAR(256), 'f_table_schema' VARCHAR(256), 'f_table_name' VARCHAR(256), 'f_geometry_column' VARCHAR(256), 'stylename' VARCHAR(30), 'styleqml' VARCHAR, 'stylesld' VARCHAR, 'useasdefault' INTEGER_BOOLEAN, 'description' VARCHAR, 'owner' VARCHAR(30), 'ui' VARCHAR(30), 'update_time' TIMESTAMP DEFAULT CURRENT_TIMESTAMP);"""
    )
    dbcon.execute("delete from layer_styles;")


def prepare_spatialite_views(dbcon, cre_table=True, gen_qml_styles_into_db=False, start_date=None, end_date=None, main_rat_params_only=False, pre_create_index=False, time_bin_secs=None, gc = None):
    assert dbcon is not None
    prepare_spatialite_required_tables(dbcon)

    if gc is not None:
        gc.log_list = pd.read_sql("select distinct log_hash from logs", dbcon)["log_hash"].values.tolist()

    df = pd.read_sql("select * from geometry_columns", dbcon)
    print("geometry_columns df:\n{}".format(df.head()))
    assert len(df) == 0

    ### we will make views one per param so drop all existing tables from geom_columns
    try:
        dbcon.execute(
            """ delete from geometry_columns where f_table_name not in ('events','signalling'); """
        )
    except:
        type_, value_, traceback_ = sys.exc_info()
        exstr = str(traceback.format_exception(type_, value_, traceback_))
        print("WARNING: del from geom cols exception: ", exstr)


    ### get list of log_hash, posids where location table's positioning_lat is -1.0 and positioning_lon is -1.0 caused by pressing load indoor logs
    gps_cancel_list = []
    df_posids_indoor_start = pd.DataFrame()
    try:
        df_posids_indoor_start = pd.read_sql(
            "select log_hash, posid from location where positioning_lat = -1.0 and positioning_lon = -1.0",
            dbcon,
        )
        df_posids_indoor_gps_cancel = pd.read_sql(
            "select log_hash, time from events where name = 'AddGPSCancel'",
            dbcon,
        )
        df_location_posid_time = pd.read_sql(
            "select log_hash, posid, time from location",
            dbcon,
        )
        for index, row in df_posids_indoor_gps_cancel.iterrows():
            posid = df_location_posid_time.loc[(df_location_posid_time.log_hash == row.log_hash) & (df_location_posid_time.time <= row.time), "posid"].max()
            df_location_posid_time = df_location_posid_time.loc[df_location_posid_time.posid != posid]
            gps_cancel_list.append((row.log_hash, posid+1))
    except:
        type_, value_, traceback_ = sys.exc_info()
        exstr = str(traceback.format_exception(type_, value_, traceback_))
        print("WARNING: prepare_spatialite_views indoor failed exception: ", exstr)

    # gps_cancel_list = []

    ### create views one per param as specified in default_theme.xml file
    # get list of params in azenqos theme xml
    params_to_gen = []
    if main_rat_params_only:
        params_to_gen = list(system_sql_query.rat_to_main_param_dict.values())
    else:
        params_to_gen = azq_theme_manager.get_matching_col_names_list_from_theme_rgs_elm()

        
    print("params_to_gen:", params_to_gen)
    dbcon.commit()
    # create layer_styles table if not exist
    tables_to_rm_stray_neg1_rows = ["signalling", "events"]
    layer_style_id = 0
    tables_added_to_geom_cols = []
    for param in params_to_gen:
        layer_style_id += 1
        try:
            print("create param table for param %s" % param)
            table = preprocess_azm.get_table_for_column(param)
            if gc is not None:
                if table not in gc.params_to_gen:
                    gc.params_to_gen[table] = []
                gc.params_to_gen[table].append(param)
            assert table
            view = param
            table_cols = pd.read_sql("select * from {} where false".format(table), dbcon).columns
            table_has_geom = "geom" in table_cols
            # table_has_modem_time = "modem_time" in table_cols
            print("table: {} table_has_geom {}".format(table, table_has_geom))
            if cre_table:
                print("read count")
                table_len = pd.read_sql("select count(*) from {}".format(table), dbcon).iloc[0,0]
                if not table_len:
                    continue  # skip this param as no rows
            else:
                if is_table_empty(dbcon, table, param):
                    continue
            if not table_has_geom:
                print("not table_has_geom so gen sql merge in from location table by time - START")
                '''
                sqlstr_old = """
                create table polqa_mos_1 as
                select pm.log_hash, pm.time, l.modem_time, l.posid, l.geom, pm.polqa_mos from
                (select strftime('%Y-%m-%d %H:%M:%S', pm.time) as t, pm.log_hash, pm.time, pm.polqa_mos from polqa_mos as pm group by t) as pm
                left join (select strftime('%Y-%m-%d %H:%M:%S', l.time) as t, l.modem_time, l.posid, l.geom from location l  group by t) as l on pm.t = l.t;
                """
                '''
                max_gps_diff_seconds = 5
                if table == view:
                    view = table+"_1"
                sqlstr = """
                create table {col} as
                select a.log_hash, a.time,
                (SELECT geom FROM location b WHERE a.log_hash = b.log_hash and b.geom is not null and a.time >= b.time and (strftime('%s',a.time) - strftime('%s', b.time) <= {max_gps_diff_seconds}) ORDER BY b.time DESC limit 1)
                as geom,
                {param}                
                FROM {table} a where {param} is not null""".format(
                    col=view,
                    param=param,
                    table=table,
                    max_gps_diff_seconds=max_gps_diff_seconds,
                )
                print("not table_has_geom so gen sql merge in from location table by time - DONE")
            else:
                print("start cre")
                cre_type = "table"
                if cre_table == False:
                    cre_type = "view"
                date_filt_where_and = ""
                if start_date is not None and end_date is not None:
                    if "time_bin" in table_cols and time_bin_secs:
                        sd = datetime.datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0)
                        ed = datetime.datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59)
                        stb = int(sd.timestamp()/time_bin_secs)
                        etb = int(ed.timestamp()/time_bin_secs)
                        date_filt_where_and = "and time_bin >= {} and time_bin < {}".format(stb, etb)
                    else:
                        date_filt_where_and = "and time >= '{}' and time <= '{} 24:00:00'".format(start_date, end_date)
                print("date_filt_where_and:", date_filt_where_and)
                drop_view_sqlstr = "drop {cre_type} if exists {view}".format(cre_type=cre_type, view=view)
                if "cell_meas" in table or table in ["ping"]:
                    sqlstr = "create {} {col} as select * from {table} where {col} is not null {date_filt_where_and};".format(cre_type, col=view, table=table, date_filt_where_and=date_filt_where_and)   # need to create table because create view casues get nearest feature id to fail - getting only 0
                else:
                    optional_cols_as = [(x if x in table_cols else "null as {}".format(x)) for x in ["modem_time", "posid", "seqid"]]
                    optional_cols_part = ",".join(optional_cols_as)
                    sqlstr = "create {} {col} as select log_hash, time, {optional_cols_part}, geom, {col} from {table} where {col} is not null {date_filt_where_and};".format(
                        cre_type, col=view, table=table,
                        optional_cols_part=optional_cols_part,
                        date_filt_where_and=date_filt_where_and
                    )
            print("create view sqlstr: %s" % sqlstr)
            if table_or_view_exists(dbcon, view):
                print("exec drop view")
                dbcon.execute(drop_view_sqlstr)
            print("exec sql")
            dbcon.execute(sqlstr)
            print("read cols")
            view_cols = pd.read_sql("select * from {} where false".format(view), dbcon).columns
            assert "geom" in view_cols
            assert param in view_cols
            if cre_table:
                print("read count")
                view_len = pd.read_sql("select count(*) from {} where {} is not null".format(view, view), dbcon).iloc[0,0]
                if not view_len:
                    continue
            else:
                print("read first row")
                if is_table_empty(dbcon, view, param):
                    continue

            tables_to_rm_stray_neg1_rows.append(view)

            sqlstr = """insert into geometry_columns values ('{}', 'geom', 'POINT', '2', 4326, 0);""".format(
                view
            )
            print("insert into geometry_columns view {} sqlstr: {}".format(view, sqlstr))
            dbcon.execute(sqlstr)
            print("commit")
            dbcon.commit()

            if not table in tables_added_to_geom_cols:
                sqlstr = """insert into geometry_columns values ('{}', 'geom', 'POINT', '2', 4326, 0);""".format(
                    table
                )
                print("insert into geometry_columns table {} sqlstr: {}".format(table, sqlstr))
                dbcon.execute(sqlstr)
                dbcon.commit()
                tables_added_to_geom_cols.append(table)

            qml = None
            if gen_qml_styles_into_db:
                # get theme df for this param
                theme_df = azq_theme_manager.get_theme_df_for_column(param, dbcon=dbcon)
                print("db_preprocess theme_df:\n", theme_df)
                if 'match_value' in theme_df.columns:
                    # id columns like pci, earfcn
                    theme_df.Lower = theme_df.match_value
                    theme_df.Upper = theme_df.match_value
                if theme_df is None:
                    continue
                print("param: {} got theme_df:\n{}".format(param, theme_df))

                qml = gen_style_qml_for_theme(theme_df, view, view_len, param, dbcon)
                # print("qml_xml: %s" % xet.tostring(root))

            df = pd.DataFrame(
                {
                    "id": [layer_style_id],
                    "f_table_name": [view],
                    "f_geometry_column": ["geom"],
                    "stylename": [param],
                    "styleqml": [
                        "<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>\n {}".format(
                            str(qml, "utf8")
                        ) if qml else None
                    ],
                    "useasdefault": [1],
                    "update_time": [pd.to_datetime(pd.Timestamp.now())],
                    "description": [pd.to_datetime(pd.Timestamp.now())],
                    "f_table_catalog": [
                        ""
                    ],  # REQUIRED TO SHOW IN QGIS BY DEFAULT - it wont show theme by default if this is None
                    "f_table_schema": [""],  # REQUIRED TO SHOW IN QGIS BY DEFAULT
                }
            )
            df.to_sql("layer_styles", dbcon, if_exists="append", index=False)
            dbcon.execute(
                """ INSERT INTO sqlite_sequence VALUES('layer_styles',{}); """.format(
                    layer_style_id
                )
            )
            # gen theme qml for this param
            # insert into layer_styles table
            dbcon.commit()
            print("create view success")
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            if "no such table" in exstr:
                continue
            print("WARNING: prepare_spatialte_views exception:", exstr)

    def lat_lon_to_geom(lat, lon):
        if lat is None or lon is None:
            return None
        geomBlob = bytearray(60)
        geomBlob[0] = 0
        geomBlob[1] = 1
        geomBlob[2] = 0xe6
        geomBlob[3] = 0x10
        geomBlob[4] = 0
        geomBlob[5] = 0
        bx = bytearray(struct.pack("d", lon)) 
        by = bytearray(struct.pack("d", lat)) 
        geomBlob[6:6+8] = bx
        geomBlob[14:14+8] = by 
        geomBlob[22:22+8] = bx
        geomBlob[30:30+8] = by
        geomBlob[38] = 0x7c
        geomBlob[39] = 1
        geomBlob[40] = 0
        geomBlob[41] = 0
        geomBlob[42] = 0
        geomBlob[43:43+8] = bx
        geomBlob[51:51+8] = by 
        geomBlob[59] = 0xfe
        return geomBlob
    df_indoor_location = None
    try:
        df_indoor_location = pd.read_sql_query("select * from indoor_location", dbcon)
    except:
        pass
    if len(df_posids_indoor_start) > 0:
        try:
            sqlstr = "update location set geom = null, positioning_lat = null, positioning_lon = null where positioning_lat < 0 or positioning_lon < 0 or positioning_lat > 1 or positioning_lon > 1;"
            dbcon.execute(sqlstr)
            dbcon.commit()
        except:
            pass
        try:
            if df_indoor_location is not None and len(df_indoor_location) > 0: 
                sqlstr = "update location set positioning_lat = (select indoor_location_lat from indoor_location where posid = location.posid), positioning_lon = (select indoor_location_lon from indoor_location where posid = location.posid);"
                print("copy indoor_location lat lon to location: %s" % sqlstr)
                dbcon.execute(sqlstr)
                dbcon.commit()
        except:
            pass
        for log_hash, posid in gps_cancel_list:
            try:
                sqlstr = "update location set geom = null, positioning_lat = null, positioning_lon = null where log_hash = {} and posid = {};".format(
                    log_hash, posid-1
                )
                print("delete gps cancel sqlstr: %s" % sqlstr)
                dbcon.execute(sqlstr)
                dbcon.commit()
            except:
                type_, value_, traceback_ = sys.exc_info()
                exstr = str(traceback.format_exception(type_, value_, traceback_))
                print("WARNING: remove gps cancel rows exception:", exstr)

    try:
        df_location = pd.read_sql_query("select time, log_hash, positioning_lat, positioning_lon from location where positioning_lat is not null and positioning_lon is not null", dbcon, parse_dates=['time'])

        # remove stray -1 -1 rows
        for view in tables_to_rm_stray_neg1_rows:
            for index, row in df_posids_indoor_start.iterrows():
                try:
                    for posid in [
                        row.posid,
                        row.posid + 1,
                    ]:  # del with same posid and next posid as found in log case: 354985102910027 20_1_2021 7.57.38.azm
                        # sqlstr = "delete from {} where log_hash = {} and posid = {};".format(
                        #     view, row.log_hash, posid
                        # )

                        sqlstr = "update {} set geom = null where log_hash = {} and posid <= {};".format(
                            view, row.log_hash, posid
                        )
                        print("delete stray -1 -1 lat lon sqlstr: %s" % sqlstr)
                        dbcon.execute(sqlstr)
                        dbcon.commit()
                except:
                    type_, value_, traceback_ = sys.exc_info()
                    exstr = str(traceback.format_exception(type_, value_, traceback_))
                    print("WARNING: remove stray -1 -1 rows exception:", exstr)
            if len(gps_cancel_list) > 0:
                for log_hash, posid in gps_cancel_list:
                    try:
                        sqlstr = "update {} set geom = null where log_hash = {} and posid = {};".format(
                            view, log_hash, posid
                        )
                        print("delete gps cancel sqlstr: %s" % sqlstr)
                        dbcon.execute(sqlstr)
                        dbcon.commit()
                    except:
                        type_, value_, traceback_ = sys.exc_info()
                        exstr = str(traceback.format_exception(type_, value_, traceback_))
                        print("WARNING: remove gps cancel rows exception:", exstr)
            if len(df_posids_indoor_start) > 0:
                view_df = pd.read_sql("select * from {}".format(view), dbcon, parse_dates=['time'])
                if len(view_df) > 0:
                    view_df = add_pos_lat_lon_to_indoor_df(view_df, df_location)
                    view_df["geom"]  = view_df.apply(lambda x: lat_lon_to_geom(x["positioning_lat"], x["positioning_lon"]), axis=1)
                    view_df = view_df.drop(columns=['positioning_lat', 'positioning_lon'])
                    view_df = view_df.sort_values(by="time").reset_index(drop=True)
                    view_df["log_hash"] = view_df["log_hash"].astype(np.int64)
                    view_df.to_sql(view, dbcon, index=False, if_exists="replace", dtype=elm_table_main_col_types)
    except:
        type_, value_, traceback_ = sys.exc_info()
        exstr = str(traceback.format_exception(type_, value_, traceback_))
        print("WARNING: indoor prepare failed exception:", exstr)
    main_param_list = ["nr_cell_meas", "lte_cell_meas", "wcdma_cell_meas", "gsm_cell_meas", "ping", "android_info_1sec"]
    if pre_create_index:
        try:
            n = 0
            for param in main_param_list:
                dbcon.execute("SELECT CreateSpatialIndex('{}', 'geom')".format(param))
                n += 1
        except:
            pass

    preprocess_azm.update_default_element_csv_for_dbcon_azm_ver(dbcon)
    ## for each param
    # create view for param
    # put param view into geometry_columns to register for display
    # create param QML theme based on default_style.qml
    # put qml entry into 'layer_styles' table

def is_table_empty(dbcon, table, col):
    df_first_row = pd.read_sql("select {} from {} where {} is not null limit 1".format(col, table, col), dbcon)
    if not len(df_first_row):
        return True
    return False

def table_or_view_exists(dbcon, table_or_view):
    return bool(len(pd.read_sql("SELECT name FROM sqlite_master WHERE (type='table' or type='view') AND name='{}';".format(table_or_view), dbcon)))

def get_geom_cols_df(dbcon):
    df = pd.read_sql("select * from geometry_columns", dbcon)
    print("geom df:\n{}".format(df.head()))
    return df


def add_pos_lat_lon_to_indoor_df(df, df_location):
    # we want to interpolate by time on lat/lon only - not the values, make new tmp df for this
    indoor_location_df_interpolated = df_location[
        ["log_hash", "time", "positioning_lat", "positioning_lon"]].copy()
    indoor_location_df_interpolated = azq_utils.resample_per_log_hash_time(indoor_location_df_interpolated,
                                                                           "100ms", use_last=True)
    cols = ["positioning_lat", "positioning_lon"]
    azq_utils.set_none_to_repetetive_rows(indoor_location_df_interpolated, cols)
    indoor_location_df_interpolated = indoor_location_df_interpolated.dropna(subset=["time"])
    indoor_location_df_interpolated = indoor_location_df_interpolated.drop_duplicates(
        subset='time').set_index('time')
    indoor_location_df_interpolated = indoor_location_df_interpolated.groupby('log_hash').apply(
        lambda sdf: sdf.interpolate(method='time')).reset_index()
    
    # merge indoor lat/lon into df

    by = None
    if "log_hash" in df.columns and "log_hash" in indoor_location_df_interpolated.columns:
        print('indoor merge df_location using by log_hash')
        by = 'log_hash'
        df['log_hash'] = df['log_hash'].astype(np.int64)
        indoor_location_df_interpolated['log_hash'] = indoor_location_df_interpolated['log_hash'].astype(np.int64)

    df = pd.merge_asof(df.sort_values("time"), indoor_location_df_interpolated.sort_values("time"),
                           on="time", by=by,
                           direction="backward", allow_exact_matches=True)
    return df


def gen_style_qml_for_theme(theme_df, view, view_len, param, dbcon, to_tmp_file=False):
    if theme_df is None:
        theme_df = azq_theme_manager.get_theme_df_for_column(param, dbcon=dbcon)
    if theme_df is None:
        return None
    if 'match_value' in theme_df.columns:
        # id columns like pci, earfcn
        theme_df.Lower = theme_df.match_value
        theme_df.Upper = theme_df.match_value
    ranges_xml = "<ranges>\n"
    try:
        # QGIS ranges count (right click > show layer count) wont match sql counts below if we dont sort this way
        theme_df["Upper"] = pd.to_numeric(theme_df["Upper"])
        theme_df.sort_values("Upper", ascending=False, inplace=True)
    except:
        type_, value_, traceback_ = sys.exc_info()
        exstr = str(traceback.format_exception(type_, value_, traceback_))
        print("WARNING: theme_df.sort_values exception:", exstr)

    match_value_counts = (theme_df.Lower == theme_df.Upper).all()
    if view_len is None and dbcon is not None:
        view_len = pd.read_sql("select count(*) from {} where {} is not null".format(view, param), dbcon).iloc[0, 0]
    match_value_counts_df = None
    if match_value_counts:
        match_value_counts_df = pd.read_sql("select {param} as match_val, count({param}) as match_count from {view} group by {param}".format(view=view,param=param), dbcon)

    # add legend bucket counts and percentage
    for index, row in theme_df.iterrows():
        percent_part = ""
        if dbcon is not None:
            try:
                rsql = "select count(*) from {view} where {param} >= {lower} and {param} < {upper}".format(view=view,
                                                                                                           param=param,
                                                                                                         lower=row.Lower,
                                                                                                         upper=row.Upper)
                if pd.notnull(row.Lower) and pd.notnull(row.Upper) and row.Lower == row.Upper:
                    rsql = "select count(*) from {view} where {param} = {lower}".format(
                        view=view, lower=row.Lower, param=param)
                count = None
                if match_value_counts_df is not None:
                    dfsl = match_value_counts_df[match_value_counts_df.match_val == row.Lower]
                    if len(dfsl) == 1:
                        count = dfsl.iloc[0].match_count
                else:
                    print("range rsql:", rsql)
                    count = pd.read_sql(
                        rsql,
                        dbcon).iloc[0, 0]
                print("view_len: {} count: {}".format(view_len, count))
                percent_part = " (%d: %.02f%%)" % (count, ((count * 100.0) / view_len))
                print("range percent_part:", percent_part)
            except:
                type_, value_, traceback_ = sys.exc_info()
                exstr = str(traceback.format_exception(type_, value_, traceback_))
                print("WARNING: calc range percent exception:", exstr)
        ranges_xml += """<range symbol="{index}" label="{lower} to {upper}{percent}" render="true" lower="{lower}" upper="{upper}" includeLower="true" includeUpper="false"/>\n""".format(
            index=index, lower=row.Lower, upper=row.Upper, percent=percent_part
        )
    ranges_xml += "</ranges>\n"
    symbols_xml = "<symbols>\n"
    for index, row in theme_df.iterrows():
        color = row.ColorXml
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        symbols_xml += """
          <symbol alpha="1" force_rhr="0" clip_to_extent="1" name="{index}" type="marker">
            <layer enabled="1" locked="0" pass="0" class="SimpleMarker">
              <prop k="angle" v="0"/>
              <prop k="color" v="{r},{g},{b},255"/>
              <prop k="horizontal_anchor_point" v="1"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="name" v="circle"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="35,35,35,255"/>
              <prop k="outline_style" v="no"/>
              <prop k="outline_width" v="0"/>
              <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="outline_width_unit" v="MM"/>
              <prop k="scale_method" v="diameter"/>
              <prop k="size" v="2"/>
              <prop k="size_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="size_unit" v="MM"/>
              <prop k="vertical_anchor_point" v="1"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
                """.format(
            index=index, r=r, g=g, b=b
        )

    symbols_xml += "</symbols>\n"
    # print("symbols_xml: %s" % symbols_xml)
    default_qml_fp = os.path.join(azq_utils.get_module_path(), "default_style.qml")
    default_qml = None
    with open(default_qml_fp, "rb") as f:
        default_qml = f.read().decode("ascii")
    default_qml_param = "lte_inst_rsrp_1"

    qml = default_qml.replace(default_qml_param, param)
    root = xet.fromstring(qml)
    renderer = root.find("renderer-v2")
    renderer.remove(renderer.find("ranges"))
    renderer.append(xet.fromstring(ranges_xml))
    renderer.remove(renderer.find("symbols"))
    renderer.append(xet.fromstring(symbols_xml))
    ret = xet.tostring(root)
    if ret and to_tmp_file:
        qml_fp = get_qml_tmp_fp_for_view(view)
        with open(qml_fp, "wb") as f:  # ret is a buffer so use wb
            f.write(ret)
        return qml_fp
    return ret

def get_qml_tmp_fp_for_view(view):
    return azq_utils.tmp_gen_fp("style_{}_{}.qml".format(view, uuid.uuid4()))