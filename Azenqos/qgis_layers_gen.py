import contextlib
import os
import sqlite3

from PyQt5.QtCore import QVariant

try:
    from qgis.core import (
        QgsProject,
        QgsFeature,
        QgsField,
        QgsFields,
        QgsPointXY,
        QgsGeometry,
        QgsVectorLayer,
        QgsDataSourceUri
    )
except:
    pass
import pathlib
import db_preprocess
import fill_geom_in_location_df
import sys
import traceback


def dump_df_to_spatialite_db(df, dbfp, table, is_indoor=False):
    assert df is not None

    if "lat" not in df.columns:
        if "positioning_lat" in df.columns:
            df["lat"] = df["positioning_lat"]
    if "lon" not in df.columns:
        if "positioning_lon" in df.columns:
            df["lon"] = df["positioning_lon"]

    with contextlib.closing(sqlite3.connect(dbfp)) as dbcon:
        assert "lat" in df.columns and "lon" in df.columns
        if is_indoor:
            assert "log_hash" in df.columns
            assert "time" in df.columns
            idf = df[["log_hash", "time", "lat", "lon"]]
            idf = idf.dropna(subset=["time"])
            idf = idf.drop_duplicates(subset='time').set_index('time')
            idf.loc[(idf.lat.duplicated()) & (idf.lon.duplicated()) , ("lat", "lon")] = None
            idf = idf.groupby('log_hash').apply(lambda sdf: sdf.interpolate(method='time'))
            idf = idf.reset_index()
            df["lat"] = idf["lat"]
            df["lon"] = idf["lon"]
            if "geom" in df.columns:
                del df["geom"]
        if 'geom' not in df.columns:
            print("fill geom start")
            df = fill_geom_in_location_df.fill_geom_in_location_df(df)
            print("fill geom done")
        assert 'geom' in df
        print("to_sql dbfp:", dbfp, "START")
        df.to_sql(table, dbcon, dtype=db_preprocess.elm_table_main_col_types)
        print("to_sql dbfp:", dbfp, "DONE")
        sqlstr = """insert into geometry_columns values ('{}', 'geom', 'POINT', '2', 4326, 0);""".format(
            table
        )
        db_preprocess.prepare_spatialite_required_tables(dbcon)
        print("insert into geometry_columns view {} sqlstr: {}".format(table, sqlstr))
        dbcon.execute(sqlstr)
        dbcon.commit()
    assert os.path.isfile(dbfp)


def create_qgis_layer_from_spatialite_db(dbfp, table, label_col=None, style_qml_fp=None, visible=True, expanded=False, add_to_qgis=True, theme_param=None, display_name=None, dbcon_for_theme_legend_counts=None, custom_sql=None):
    print("create_qgis_layer_from_spatialite_db: table", table)
    # https://qgis-docs.readthedocs.io/en/latest/docs/pyqgis_developer_cookbook/loadlayer.html
    schema = ''
    table = table
    uri = QgsDataSourceUri()
    uri.setDatabase(dbfp)
    uri.setDataSource(schema, table, 'geom', custom_sql)
    if display_name is None:
        display_name = table
    print("create QgsVectorLayer for uri start")
    layer = QgsVectorLayer(uri.uri(), display_name, 'spatialite')
    print("create QgsVectorLayer for uri done")
    if style_qml_fp is None and theme_param is not None:
        print("create qml for uri start")
        try:
            qml_fp = db_preprocess.gen_style_qml_for_theme(None, table, None, theme_param, dbcon_for_theme_legend_counts, to_tmp_file=True)
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print(
                "WARNING: getn style_qml_fpfailed exception: {}".format(
                    exstr
                )
            )
        print("create qml for uri done:", qml_fp)
        style_qml_fp = qml_fp
    if style_qml_fp is not None:
        print("style_qml_fp:", style_qml_fp)
        if os.path.isfile(style_qml_fp):
            print("loading style file")
            layer.loadNamedStyle(style_qml_fp)
            print("loading style file done")
        else:
            print("not loading style file as file not found")
    if add_to_qgis:
        print("adding map layer")
        QgsProject.instance().addMapLayer(layer)
        print("adding map layer done")
        print("find layer")
        ltlayer = QgsProject.instance().layerTreeRoot().findLayer(layer.id())
        print("set visi")
        ltlayer.setItemVisibilityChecked(visible)
        print("set expanded")
        ltlayer.setExpanded(expanded)
        print("set expanded done")
    return layer


def create_qgis_layer_csv(csv_fp, layer_name="layer", x_field="lon", y_field="lat", label_col=None):
    print("create_qgis_layer_csv() label_col: {} START".format(label_col))
    uri = pathlib.Path(csv_fp).as_uri()
    uri += "?crs=epsg:4326&xField={}&yField={}".format(x_field, y_field)
    print("csv uri: {}".format(uri))
    layer = QgsVectorLayer(uri, layer_name, "delimitedtext")
    if label_col:
        layer.setCustomProperty("labeling", "pal")
        layer.setCustomProperty("labeling/enabled", "true")
        layer.setCustomProperty("labeling/fontFamily", "Arial")
        layer.setCustomProperty("labeling/fontSize", "10")
        layer.setCustomProperty("labeling/fieldName", label_col)
        layer.setCustomProperty("labeling/placement", "2")
    QgsProject.instance().addMapLayers([layer])
    print("create_qgis_layer_csv() DONE")

def check_poi_file(gc, poi_fp, layer_name=None):
    import qt_utils
    ret = create_qgis_poi_layer(gc, poi_fp, layer_name=layer_name)
    if ret != "success":
        print("aaaaaaaaaaaaaa")
        qt_utils.msgbox(ret, title="Invalid POI file")

def create_qgis_poi_layer(gc, poi_fp, layer_name=None):
    import csv
    x_field=None
    y_field=None
    file_name = os.path.basename(poi_fp)
    layer_name = os.path.splitext(file_name)[0]
    extension = os.path.splitext(file_name)[1]
    if extension == ".csv":
        with open(poi_fp, "r") as f:
            d_reader = csv.DictReader(f)
            headers = d_reader.fieldnames
            x_field, y_field = get_lon_lat_column_name(headers)
        if x_field is not None and y_field is not None:
            create_qgis_layer_csv(poi_fp, layer_name, x_field=x_field, y_field=y_field)
            return "success"
        else:
            return "Please make sure that there are longitude and latitude in your csv file."
    else:
        layer = QgsVectorLayer(poi_fp, layer_name, 'ogr')
        if layer.isValid():
            if gc.qgis_iface:
                gc.qgis_iface.addVectorLayer(poi_fp, layer_name, 'ogr')
                return "success"
        else:
            return "{} file type not supported".format(extension)

def get_lon_lat_column_name(column_list):
    column_list= [column.lower() for column in column_list]
    x_field=None
    y_field=None
    if "long" in column_list and "lat" in column_list:
        x_field="long"
        y_field="lat"
    elif "lon" in column_list and "lat" in column_list:
        x_field="lon"
        y_field="lat"
    elif "positioning_long" in column_list and "positioning_lat" in column_list:
        x_field="positioning_long"
        y_field="positioning_lat"
    elif "positioning_lon" in column_list and "positioning_lat" in column_list:
        x_field="positioning_lon"
        y_field="positioning_lat"
    elif "longitude" in column_list and "latitude" in column_list:
        x_field="longitude"
        y_field="latitude"
    elif "x" in column_list and "y" in column_list:
        x_field="x"
        y_field="y"
    return x_field, y_field

def create_test_qgis_layer_py_objs():
    print("create_test_qgis_layer_action() impl START")

    fields = QgsFields()
    fields.append(QgsField("cell_id", QVariant.Int))

    layer = QgsVectorLayer("Point?crs=epsg:4326", "temporary_points", "memory")
    pr = layer.dataProvider()
    pr.addAttributes(fields)
    layer.updateFields()

    fet = QgsFeature()
    fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(25.60278, -33.98113)))

    pr.addFeatures([fet])
    layer.updateExtents()

    QgsProject.instance().addMapLayers([layer])
    print("create_test_qgis_layer_action() impl DONE")
