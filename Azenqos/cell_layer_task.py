import os.path
import sys
import traceback

import pandas as pd
from PyQt5.QtGui import QColor
from qgis.PyQt.QtCore import QVariant
from qgis.core import (
    QgsProject,
    QgsFeature,
    QgsField,
    QgsFields,
    QgsPointXY,
    QgsGeometry,
    QgsTask,
    QgsVectorLayer
)

from azq_cell_file import read_cell_file, RAT_TO_MAIN_CELL_COL_KNOWN_NAMES_DICT
from azq_utils import get_default_color_for_index

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
fields.append(QgsField("cgi", QVariant.String))


def cell_to_polygon(cell, sector_distance=0.001, sector_size_meters=0):
    if sector_size_meters:
        import azq_cell_file
        sector_distance = azq_cell_file.METER_IN_WGS84 * sector_size_meters
    poly = QgsFeature()
    distance = sector_distance
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
    poly["cgi"] = cell.cgi
    system = cell.system.lower()
    poly[RAT_TO_MAIN_CELL_COL_KNOWN_NAMES_DICT[system].upper()] = cell[RAT_TO_MAIN_CELL_COL_KNOWN_NAMES_DICT[system]]
    poly.setGeometry(QgsGeometry.fromPolygonXY([points]))
    return poly


class CellLayerTask(QgsTask):


    def __init__(self, description, files, gc, task_done_signal):
        super().__init__(description)
        self.files = files
        self.cells_layers = []
        self.gc = gc
        self.task_done_signal = task_done_signal
        import azq_cell_file
        azq_cell_file.clear_cell_file_cache()


    def create_cell_layer(self, df, system, name, color):
        system = system.lower()
        import azq_cell_file
        assert system in azq_cell_file.CELL_FILE_RATS
        pref_key = "cell_{}_sector_size_meters".format(system)
        sector_size_meters = float(self.gc.pref[pref_key])
        print("create_cell_layer system {} sector_size_meters {}".format(system, sector_size_meters))
        features = (
            df[df["system"].str.lower() == system]
            .apply(cell_to_polygon, sector_size_meters=sector_size_meters, axis=1)
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
        print("cell_layer_task_run() 0")
        frames = []

        for path in self.files:
            try:
                print("read " + path)
                frames.append(read_cell_file(path))
            except:
                type_, value_, traceback_ = sys.exc_info()
                exstr = str(traceback.format_exception(type_, value_, traceback_))
                print("WARNING: read cell file - exception: {}".format(exstr))
        print("cell_layer_task_run() 1")
        if not len(frames):
            return
        print("cell_layer_task_run() 2")
        try:
            df = pd.concat(frames)
            print("cell_layer_task_run() 3")
            nr_cells_layer = self.create_cell_layer(
                df, "nr", "NR cells", get_default_color_for_index(0)
            )
            print("cell_layer_task_run() 4")
            lte_cells_layer = self.create_cell_layer(
                df, "lte", "LTE cells", get_default_color_for_index(1)
            )
            print("cell_layer_task_run() 5")
            wcdma_cells_layer = self.create_cell_layer(
                df, "wcdma", "WCDMA cells", get_default_color_for_index(2)
            )
            print("cell_layer_task_run() 6")
            gsm_cells_layer = self.create_cell_layer(
                df, "gsm", "GSM cells", get_default_color_for_index(3)
            )
            print("cell_layer_task_run() 7")
            self.cells_layers = [
                nr_cells_layer,
                lte_cells_layer,
                wcdma_cells_layer,
                gsm_cells_layer,
            ]
            print("cell_layer_task_run() 8")
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print("WARNING: load cell file - exception: {}".format(exstr))
        print("cell_layer_task_run() end")
        return True


    def finished(self, result):
        self.task_done_signal.emit(os.path.basename(__file__))

    def add_layers_from_ui_thread(self):
        try:
            print("add_layers_from_ui_thread() 0")
            QgsProject.instance().addMapLayers(self.cells_layers)
            print("add_layers_from_ui_thread() 1")
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print("WARNING: load cell file - exception: {}".format(exstr))
        print("add_layers_from_ui_thread() end")

    def run_blocking(self):
        self.run()
        self.add_layers_from_ui_thread()


    def cancel(self):
        super().cancel()
