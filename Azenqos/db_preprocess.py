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
        """CREATE TABLE IF NOT EXISTS 'layer_styles' ( "id" INTEGER PRIMARY KEY AUTOINCREMENT, 'f_table_catalog' VARCHAR(256), 'f_table_schema' VARCHAR(256), 'f_table_name' VARCHAR(256), 'f_geometry_column' VARCHAR(256), 'stylename' VARCHAR(30), 'styleqml' VARCHAR, 'stylesld' VARCHAR, 'useasdefault' INTEGER_BOOLEAN, 'description' VARCHAR, 'owner' VARCHAR(30), 'ui' VARCHAR(30), 'update_time' TIMESTAMP DEFAULT CURRENT_TIMESTAMP);"""
    )
    dbcon.execute("delete from layer_styles;")

    default_qml_fp = os.path.join(azq_utils.get_module_path(), "default_style.qml")
    default_qml = None
    with open(default_qml_fp, "rb") as f:
        default_qml = f.read().decode("ascii")
    default_qml_param = "lte_inst_rsrp_1"

    ### we will make views one per param so drop all existing tables from geom_columns
    dbcon.execute(
        """ delete from geometry_columns where f_table_name not in ('events','signalling'); """
    )

    ### create views one per param as specified in default_theme.xml file
    # get list of params in azenqos theme xml
    params_to_gen = azq_theme_manager.get_matching_col_names_list_from_theme_rgs_elm()
    print("params_to_gen:", params_to_gen)

    # create layer_styles table if not exist

    layer_style_id = 0
    for param in params_to_gen:
        layer_style_id += 1
        try:
            print("create param table for param %s" % param)
            table = preprocess_azm.get_table_for_column(param)
            assert table
            view = param
            sqlstr = "create table {col} as select log_hash, time, modem_time, geom, {col} from {table} ;".format(
                col=view, table=table
            )
            print("create view sqlstr: %s" % sqlstr)
            dbcon.execute(sqlstr)
            sqlstr = """insert into geometry_columns values ('{}', 'geom', 'POINT', '2', 4326, 0);""".format(
                view
            )
            dbcon.execute(sqlstr)

            # get theme df for this param
            theme_df = azq_theme_manager.get_theme_df_for_column(param)
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
            print("WARNING: prepare_spatialte_views exception:", exstr)

    ## for each param
    # create view for param
    # put param view into geometry_columns to register for display
    # create param QML theme based on default_style.qml
    # put qml entry into 'layer_styles' table
