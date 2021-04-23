import os

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
    )
except:
    pass
import preprocess_azm
import azq_utils
import uuid
import pathlib


def create_qgis_layer_df(df, dbcon, layer_name="layer", auto_add_lat_lon=True):
    assert df is not None
    assert "log_hash" in df.columns
    assert "time" in df.columns

    if "lat" not in df.columns:
        if "positioning_lat" in df.columns:
            df["lat"] = df["positioning_lat"]
    if "lon" not in df.columns:
        if "positioning_lon" in df.columns:
            df["lon"] = df["positioning_lon"]

    if auto_add_lat_lon:
        if ("lat" not in df.columns) and ("lon" not in df.columns):
            assert dbcon is not None
            print("need to merge lat and lon")
            df = preprocess_azm.merge_lat_lon_into_df(dbcon, df).rename(
                columns={"positioning_lat": "lat", "positioning_lon": "lon"}
            )
    assert "lat" in df.columns and "lon" in df.columns
    tmp_csv_fp = os.path.join(
        azq_utils.tmp_gen_path(), "tmp_csv_{}.csv".format(uuid.uuid4())
    )
    df.to_csv(tmp_csv_fp, index=False)
    create_qgis_layer_csv(tmp_csv_fp, layer_name=layer_name)


def create_qgis_layer_csv(csv_fp, layer_name="layer", x_field="lon", y_field="lat"):
    print("create_qgis_layer_csv() START")
    uri = pathlib.Path(csv_fp).as_uri()
    uri += "?crs=epsg:4326&xField={}&yField={}".format(x_field, y_field)
    print("csv uri: {}".format(uri))
    layer = QgsVectorLayer(uri, layer_name, "delimitedtext")
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
