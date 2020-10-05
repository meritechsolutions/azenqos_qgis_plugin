import random
from time import sleep
from qgis.core import *
from qgis.utils import *
from qgis.gui import *
from qgis.PyQt.QtCore import QVariant
from PyQt5.QtGui import *
import pandas as pd
from .azq_cell_file import read_cell_file, g_main_cell_col
from .azq_utils import get_default_color_for_index
import azq_utils

MESSAGE_CATEGORY = "RandomIntegerSumTask"

fields = QgsFields()
fields.append(QgsField("cell_id", QVariant.Int))
fields.append(QgsField("site", QVariant.String))
fields.append(QgsField("system", QVariant.String))
fields.append(QgsField("latitude", QVariant.Double))
fields.append(QgsField("longitude", QVariant.Double))
fields.append(QgsField("dir", QVariant.Int))
fields.append(QgsField("ant_bw", QVariant.Int))
fields.append(QgsField("mcc", QVariant.Int))
fields.append(QgsField("mnc", QVariant.Int))
fields.append(QgsField("mnc", QVariant.Int))
fields.append(QgsField("PCI", QVariant.Int))
fields.append(QgsField("PSC", QVariant.Int))
fields.append(QgsField("BCCH", QVariant.Int))


def cell_to_polygon(cell):
    poly = QgsFeature()
    distance = 0.001
    point2_dir = cell.dir + (cell.ant_bw / 2)
    point3_dir = cell.dir - (cell.ant_bw / 2)
    point1 = QgsPointXY(cell.lon, cell.lat)
    point2 = point1.project(distance, point2_dir)
    point3 = point1.project(distance, point3_dir)
    points = [point1, point2, point3]
    poly.setFields(fields)
    poly["cell_id"] = cell.cell_id
    poly["site"] = cell.site
    poly["system"] = cell.system
    poly["latitude"] = cell.lat
    poly["longitude"] = cell.lon
    poly["dir"] = cell.dir
    poly["ant_bw"] = cell.ant_bw
    poly["longitude"] = cell.lon
    poly["longitude"] = cell.lon
    poly["mcc"] = cell.mcc
    poly["mnc"] = cell.mnc
    system = cell.system.lower()
    poly[g_main_cell_col[system].upper()] = cell[g_main_cell_col[system]]
    poly.setGeometry(QgsGeometry.fromPolygonXY([points]))
    return poly


class CellLayerTask(QgsTask):
    def __init__(self, description, files):
        super().__init__(description)
        self.files = files
        self.cells_layers = []

    def create_cell_layer(self, df, system, name, color):
        features = (
            df[df["system"].str.lower() == system]
            .apply(cell_to_polygon, axis=1)
            .values.tolist()
        )
        layer = QgsVectorLayer("Polygon?system=" + system, name, "memory")
        pr = layer.dataProvider()
        pr.addAttributes(fields)
        layer.updateFields()
        pr.addFeatures(features)
        layer.updateExtents()
        symbol = layer.renderer().symbol()
        symbol.setColor(QColor(color))
        return layer

    def run(self):
        frames = []
        print("before load cell files")
        for path in self.files:
            try:
                print("read " + path)
                frames.append(read_cell_file(path))
            except:
                type_, value_, traceback_ = sys.exc_info()
                exstr = str(traceback.format_exception(type_, value_, traceback_))
                print("WARNING: read cell file - exception: {}".format(exstr))
        print("after load cell files")
        df = pd.concat(frames)
        try:
            nr_cells_layer = self.create_cell_layer(
                df, "nr", "5G cells", get_default_color_for_index(0)
            )
            lte_cells_layer = self.create_cell_layer(
                df, "lte", "4G cells", get_default_color_for_index(1)
            )
            wcdma_cells_layer = self.create_cell_layer(
                df, "wcdma", "3G cells", get_default_color_for_index(2)
            )
            gsm_cells_layer = self.create_cell_layer(
                df, "gsm", "2G cells", get_default_color_for_index(3)
            )
            self.cells_layers = [
                nr_cells_layer,
                lte_cells_layer,
                wcdma_cells_layer,
                gsm_cells_layer,
            ]
            azq_utils.write_local_file("config_prev_cell_file", ",".join(self.files))
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print("WARNING: load cell file - exception: {}".format(exstr))
        return True

    def finished(self, result):
        try:
            QgsProject.instance().addMapLayers(self.cells_layers)
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print("WARNING: load cell file - exception: {}".format(exstr))

    def cancel(self):
        super().cancel()
