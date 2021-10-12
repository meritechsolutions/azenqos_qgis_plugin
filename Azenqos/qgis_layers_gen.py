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
import azq_utils
import uuid


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
            idf = idf.groupby('log_hash').apply(lambda sdf: sdf.interpolate(method='time'))
            idf = idf.reset_index()
            df["lat"] = idf["lat"]
            df["lon"] = idf["lon"]
            if "geom" in df.columns:
                del df["geom"]
        if 'geom' not in df.columns:
            df = fill_geom_in_location_df.fill_geom_in_location_df(df)
        assert 'geom' in df
        print("to_sql dbfp:", dbfp)
        df.to_sql(table, dbcon, dtype=db_preprocess.elm_table_main_col_types)
        sqlstr = """insert into geometry_columns values ('{}', 'geom', 'POINT', '2', 4326, 0);""".format(
            table
        )
        db_preprocess.prepare_spatialite_required_tables(dbcon)
        print("insert into geometry_columns view {} sqlstr: {}".format(table, sqlstr))
        dbcon.execute(sqlstr)
        dbcon.commit()
    assert os.path.isfile(dbfp)


def create_qgis_layer_from_spatialite_db(dbfp, table, label_col=None, style_qml_fp=None, visible=True, expanded=False, add_to_qgis=True, theme_param=None, display_name=None):
    print("create_qgis_layer_from_spatialite_db: table", table)
    '''
    # now we create from spatialite dbcon instead
    tmp_csv_fp = os.path.join(
        azq_utils.tmp_gen_path(), "tmp_csv_{}.csv".format(uuid.uuid4())
    )
<<<<<<< HEAD
    df.to_csv(tmp_csv_fp, index=False, quoting=csv.QUOTE_ALL)
    create_qgis_layer_csv(tmp_csv_fp, layer_name=layer_name, label_col=label_col)
    '''
    # https://qgis-docs.readthedocs.io/en/latest/docs/pyqgis_developer_cookbook/loadlayer.html
    schema = ''
    table = table
    uri = QgsDataSourceUri()
    uri.setDatabase(dbfp)
    uri.setDataSource(schema, table, 'geom')
    if display_name is None:
        display_name = table
    layer = QgsVectorLayer(uri.uri(), display_name, 'spatialite')
    if style_qml_fp is None and theme_param is not None:
        with contextlib.closing(sqlite3.connect(dbfp)) as dbcon:
            qml_bytes = db_preprocess.gen_style_qml_for_theme(None, table, None, theme_param, dbcon)
            qml_fp = azq_utils.tmp_gen_fp("tmp_theme_{}.qml".format(uuid.uuid4()))
            with open(qml_fp, "wb") as f:  # ret is a buffer so use wb
                f.write(qml_bytes)
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
