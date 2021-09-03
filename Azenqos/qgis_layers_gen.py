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


def dump_df_to_spatialite_db(df, dbfp, table):
    assert df is not None
    assert "log_hash" in df.columns
    assert "time" in df.columns

    if "lat" not in df.columns:
        if "positioning_lat" in df.columns:
            df["lat"] = df["positioning_lat"]
    if "lon" not in df.columns:
        if "positioning_lon" in df.columns:
            df["lon"] = df["positioning_lon"]

    with contextlib.closing(sqlite3.connect(dbfp)) as dbcon:
        assert "lat" in df.columns and "lon" in df.columns
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


def create_qgis_layer_from_spatialite_db(dbfp, table, label_col=None):
    '''
    # now we create from spatialite dbcon instead
    tmp_csv_fp = os.path.join(
        azq_utils.tmp_gen_path(), "tmp_csv_{}.csv".format(uuid.uuid4())
    )
    df.to_csv(tmp_csv_fp, index=False, quoting=csv.QUOTE_ALL)
    create_qgis_layer_csv(tmp_csv_fp, layer_name=layer_name, label_col=label_col)
    '''
    # https://qgis-docs.readthedocs.io/en/latest/docs/pyqgis_developer_cookbook/loadlayer.html
    schema = ''
    table = table
    uri = QgsDataSourceUri()
    uri.setDatabase(dbfp)
    uri.setDataSource(schema, table, 'geom')
    display_name = table
    layer = QgsVectorLayer(uri.uri(), display_name, 'spatialite')
    QgsProject.instance().addMapLayer(layer)




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
