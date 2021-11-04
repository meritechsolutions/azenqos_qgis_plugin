import contextlib
import os.path
import sqlite3
import sys
import traceback
from multiprocessing.pool import ThreadPool
import multiprocessing as mp

import pandas as pd
import psutil

import azq_utils
import preprocess_azm

try:
    from qgis.core import (
        QgsProject,
        QgsCoordinateReferenceSystem,
    )
except:
    pass


def create_layers(gc, db_fp=None, ogr_mode=False, display_name_prefix="", gen_theme_bucket_counts=True):
    azq_utils.timer_start("create_layers")
    try:
        if db_fp is None:
            db_fp = gc.db_fp
        if True:
            # gc.mostFeaturesLayer = None
            print("db_layer_task.py add_layers_from_ui_thread 0")
            # Setting CRS
            my_crs = QgsCoordinateReferenceSystem(4326)
            QgsProject.instance().setCrs(my_crs)
            print("db_layer_task.py add_layers_from_ui_thread() 3 addVectorLayer")
            # geom_column = "geom"
            if ogr_mode and gc.qgis_iface:
                gc.qgis_iface.addVectorLayer(db_fp, None, "ogr")
            else:

                with contextlib.closing(sqlite3.connect(db_fp)) as dbcon:
                    db_created_views_mode = True  # if false then qgis seems to create/show only the last created layer per same table
                    custom_sql = None
                    param_list = pd.read_sql("select f_table_name from geometry_columns", dbcon).f_table_name.values
                    if db_created_views_mode:
                        table_list = param_list
                    else:
                        param_list = pd.read_sql("select f_table_name from geometry_columns", dbcon).f_table_name.values
                        table_list = [preprocess_azm.get_table_for_column(param) for param in param_list]
                    tp_list = zip(table_list, param_list)
                    import qgis_layers_gen
                    last_visible_layer = None
                    table_to_layer_dict = {}
                    layer_id_to_visible_flag_dict = {}
                    qml_tmp_fp_list = None

                    # pre-gen qml theme file
                    azq_utils.timer_start("gen_theme_qml")
                    qml_tmp_fp_list = []
                    mp_mode = False
                    if mp_mode:
                        print("gen theme qml files mp")
                        pool = mp.Pool(psutil.cpu_count()) if os.name == "posix" else ThreadPool(psutil.cpu_count())  # windows qgis if mp it will open multiple instances of qgis
                        try:
                            args = []
                            for table, param in tp_list:
                                args.append((table, param, db_fp, gen_theme_bucket_counts))
                            qml_tmp_fp_list = pool.starmap(azq_utils.get_theme_qml_tmp_file_for_param, args)
                        finally:
                            pool.close()
                    else:
                        print("gen theme qml files seq")
                        for table, param in tp_list:
                            qml_tmp_fp_list.append(azq_utils.get_theme_qml_tmp_file_for_param(table, param, db_fp, gen_theme_bucket_counts=gen_theme_bucket_counts))
                    azq_utils.timer_print("gen_theme_qml")
                    assert qml_tmp_fp_list is not None
                    assert len(qml_tmp_fp_list) > 0
                    for i in range(len(table_list)):
                        table = table_list[i]
                        param = param_list[i]
                        qml_tmp_fp = qml_tmp_fp_list[i]
                        if not qml_tmp_fp or not os.path.isfile(qml_tmp_fp):
                            continue
                        print("Adding layer to UI:", param)
                        try:
                            import system_sql_query
                            visible = False
                            if table in system_sql_query.rat_to_main_param_dict.values():
                                visible = True
                            layer = qgis_layers_gen.create_qgis_layer_from_spatialite_db(
                                db_fp, table, visible=visible,
                                style_qml_fp=qml_tmp_fp, add_to_qgis=False, display_name=display_name_prefix+param, theme_param=param, custom_sql=custom_sql
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
    finally:
        azq_utils.timer_print("create_layers")
    return None


def ui_thread_add_layers_to_qgis(gc, table_to_layer_dict, layer_id_to_visible_flag_dict, last_visible_layer):
    azq_utils.timer_start("ui_thread_add_layers_to_qgis")
    try:
        layers = table_to_layer_dict.values()
        print("ui_thread_add_layers_to_qgis1")
        QgsProject.instance().addMapLayers(layers)
        print("ui_thread_add_layers_to_qgis2")
        for lid in layer_id_to_visible_flag_dict.keys():
            visible = layer_id_to_visible_flag_dict[lid]
            ltlayer = QgsProject.instance().layerTreeRoot().findLayer(lid)
            if ltlayer is None:
                continue
            ltlayer.setItemVisibilityChecked(visible)
            print("ui_thread_add_layers_to_qgis2 lid {} visible {}".format(lid, visible))
        for layer in layers:
            ltlayer = QgsProject.instance().layerTreeRoot().findLayer(layer.id())
            if ltlayer is None:
                continue
            ltlayer.setExpanded(False)
            if last_visible_layer is not None and last_visible_layer.id() == layer.id():
                if gc.qgis_iface:
                    gc.qgis_iface.setActiveLayer(last_visible_layer)
    except:
        type_, value_, traceback_ = sys.exc_info()
        exstr = str(traceback.format_exception(type_, value_, traceback_))
        print("WARNING: ui_thread_add_layers_to_qgis - exception: {}".format(exstr))
    finally:
        azq_utils.timer_print("ui_thread_add_layers_to_qgis")
    return None


