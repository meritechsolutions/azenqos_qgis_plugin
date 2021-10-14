import contextlib
import sqlite3
import sys
import traceback

import pandas as pd

try:
    from qgis.core import (
        QgsProject,
        QgsCoordinateReferenceSystem,
    )
except:
    pass


def create_layers(gc, ogr_mode=False):
    try:
        if gc.qgis_iface:
            # gc.mostFeaturesLayer = None
            print("db_layer_task.py add_layers_from_ui_thread 0")
            # Setting CRS
            my_crs = QgsCoordinateReferenceSystem(4326)
            QgsProject.instance().setCrs(my_crs)
            print("db_layer_task.py add_layers_from_ui_thread() 3 addVectorLayer")
            # geom_column = "geom"
            table_list = None
            with contextlib.closing(sqlite3.connect(gc.db_fp)) as dbcon:
                table_list = pd.read_sql("select f_table_name from geometry_columns", dbcon).f_table_name.values

            if ogr_mode:
                gc.qgis_iface.addVectorLayer(gc.db_fp, None, "ogr")
            else:
                import qgis_layers_gen
                last_visible_layer = None
                table_to_layer_dict = {}
                layer_id_to_visible_flag_dict = {}
                for table in table_list:
                    print("Adding table layer to UI:", table)
                    try:
                        import azq_utils
                        import system_sql_query
                        visible = False
                        if table in system_sql_query.rat_to_main_param_dict.values():
                            visible = True
                        layer = qgis_layers_gen.create_qgis_layer_from_spatialite_db(
                            gc.db_fp, table, visible=visible,
                            style_qml_fp=azq_utils.tmp_gen_fp("style_{}.qml".format(table)), add_to_qgis=False
                        )
                        layer_id_to_visible_flag_dict[layer.id()] = visible
                        table_to_layer_dict[table] = layer
                        if visible:
                            last_visible_layer = layer
                    except:
                        type_, value_, traceback_ = sys.exc_info()
                        exstr = str(traceback.format_exception(type_, value_, traceback_))
                        print("WARNING: create_qgis_layer_from_spatialite_db table {} failed exception: {}".format(
                            table, exstr
                        )
                        )

                return table_to_layer_dict, layer_id_to_visible_flag_dict, last_visible_layer
    except:
        type_, value_, traceback_ = sys.exc_info()
        exstr = str(traceback.format_exception(type_, value_, traceback_))
        print("WARNING: add_layers_from_ui_thread - exception: {}".format(exstr))
    return None


def ui_thread_add_layers_to_qgis(gc, table_to_layer_dict, layer_id_to_visible_flag_dict, last_visible_layer):
    try:
        layers = table_to_layer_dict.values()
        print("ui_thread_add_layers_to_qgis1")
        QgsProject.instance().addMapLayers(layers)
        print("ui_thread_add_layers_to_qgis2")
        for lid in layer_id_to_visible_flag_dict.keys():
            visible = layer_id_to_visible_flag_dict[lid]
            ltlayer = QgsProject.instance().layerTreeRoot().findLayer(lid)
            ltlayer.setItemVisibilityChecked(visible)

        for layer in layers:
            ltlayer = QgsProject.instance().layerTreeRoot().findLayer(layer.id())
            ltlayer.setExpanded(False)
            if last_visible_layer is not None and last_visible_layer.id() == layer.id():
                gc.qgis_iface.setActiveLayer(last_visible_layer)
    except:
        type_, value_, traceback_ = sys.exc_info()
        exstr = str(traceback.format_exception(type_, value_, traceback_))
        print("WARNING: ui_thread_add_layers_to_qgis - exception: {}".format(exstr))
    return None

