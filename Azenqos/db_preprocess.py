import azq_theme_manager
import sys
import traceback
import preprocess_azm
import azq_utils
import os
import xml.etree.ElementTree as xet
import io
import pandas as pd


def prepare_spatialite_views(dbcon):
    assert dbcon is not None

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
        if 'UNIQUE constraint failed' in exstr:
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
        """CREATE TABLE IF NOT EXISTS 'layer_styles' ( "id" INTEGER PRIMARY KEY AUTOINCREMENT, 'f_table_catalog' VARCHAR(256), 'f_table_schema' VARCHAR(256), 'f_table_name' VARCHAR(256), 'f_geometry_column' VARCHAR(256), 'stylename' VARCHAR(30), 'styleqml' VARCHAR, 'stylesld' VARCHAR, 'useasdefault' INTEGER_BOOLEAN, 'description' VARCHAR, 'owner' VARCHAR(30), 'ui' VARCHAR(30), 'update_time' TIMESTAMP DEFAULT CURRENT_TIMESTAMP);"""
    )
    dbcon.execute("delete from layer_styles;")

    default_qml_fp = os.path.join(azq_utils.get_module_path(), "default_style.qml")
    default_qml = None
    with open(default_qml_fp, "rb") as f:
        default_qml = f.read().decode("ascii")
    default_qml_param = "lte_inst_rsrp_1"

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
    df_posids_indoor_start = pd.read_sql("select log_hash, posid from location where positioning_lat = -1.0 and positioning_lon = -1.0", dbcon)

    ### create views one per param as specified in default_theme.xml file
    # get list of params in azenqos theme xml
    params_to_gen = azq_theme_manager.get_matching_col_names_list_from_theme_rgs_elm()
    print("params_to_gen:", params_to_gen)

    # create layer_styles table if not exist
    tables_to_rm_stray_neg1_rows = ["signalling", "events"]
    layer_style_id = 0
    for param in params_to_gen:
        layer_style_id += 1
        try:
            print("create param table for param %s" % param)
            table = preprocess_azm.get_table_for_column(param)
            assert table
            view = param
            if view == "polqa_mos":
                view = "polqa_mos_1"
                sqlstr = "create table polqa_mos_1 as select pm.log_hash, pm.time, l.modem_time, l.posid, l.geom, pm.polqa_mos from(select strftime('%Y-%m-%d %H:%M:%S', pm.time) as t, pm.log_hash, pm.time, pm.polqa_mos from polqa_mos as pm group by t) as pm left join (select strftime('%Y-%m-%d %H:%M:%S', l.time) as t, l.modem_time, l.posid, l.geom from  location l  group by t) as l on pm.t = l.t;"
            else:
                sqlstr = "create table {col} as select log_hash, time, modem_time, posid, geom, {col} from {table} ;".format(
                    col=view, table=table
                )
            print("create view sqlstr: %s" % sqlstr)
            dbcon.execute(sqlstr)
            tables_to_rm_stray_neg1_rows.append(view)

            sqlstr = """insert into geometry_columns values ('{}', 'geom', 'POINT', '2', 4326, 0);""".format(
                view
            )
            dbcon.execute(sqlstr)
            
            # get theme df for this param
            theme_df = azq_theme_manager.get_theme_df_for_column(param)
            if theme_df is None:
                continue
            # print("theme_df:\n%s" % theme_df)

            ranges_xml = "<ranges>\n"
            for index, row in theme_df.iterrows():
                ranges_xml += """<range symbol="{index}" label="{lower} to {upper}" render="true" lower="{lower}" upper="{upper}"/>\n""".format(
                    index=index, lower=row.Lower, upper=row.Upper
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

            qml = default_qml.replace(default_qml_param, param)
            root = xet.fromstring(qml)
            renderer = root.find("renderer-v2")
            renderer.remove(renderer.find("ranges"))
            renderer.append(xet.fromstring(ranges_xml))
            renderer.remove(renderer.find("symbols"))
            renderer.append(xet.fromstring(symbols_xml))
            # print("qml_xml: %s" % xet.tostring(root))

            df = pd.DataFrame(
                {
                    "id": [layer_style_id],
                    "f_table_name": [param],
                    "f_geometry_column": ["geom"],
                    "stylename": [param],
                    "styleqml": [
                        "<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>\n {}".format(
                            str(xet.tostring(root), "utf8")
                        )
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

            
    # remove stray -1 -1 rows
    for view in tables_to_rm_stray_neg1_rows:
        for index, row in df_posids_indoor_start.iterrows():
            for posid in [row.posid, row.posid+1]:  # del with same posid and next posid as found in log case: 354985102910027 20_1_2021 7.57.38.azm
                # sqlstr = "delete from {} where log_hash = {} and posid = {};".format(
                #     view, row.log_hash, posid
                # )
                sqlstr = "update {} set geom = null where log_hash = {} and posid = {};".format(
                    view, row.log_hash, posid
                )
                print("delete stray -1 -1 lat lon sqlstr: %s" % sqlstr)
                dbcon.execute(sqlstr)
                dbcon.commit()


    ## for each param
    # create view for param
    # put param view into geometry_columns to register for display
    # create param QML theme based on default_style.qml
    # put qml entry into 'layer_styles' table
