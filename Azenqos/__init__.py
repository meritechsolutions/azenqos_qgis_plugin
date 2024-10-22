# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Azenqos
                                 A QGIS plugin
 Azenqos Plugin
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2019-03-18
        copyright            : Copyright (C) 2019-2020 Freewill FX Co., Ltd. All rights reserved
        email                : support@azenqos.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""
import os

from PyQt5.QtWidgets import QMessageBox, QPushButton

def add_src_folder_to_import_path():
    import os
    import sys
    import inspect

    currentdir = os.path.dirname(
        os.path.abspath(inspect.getfile(inspect.currentframe()))
    )
    sys.path.insert(0, currentdir)


# noinspection PyPep8Naming

def classFactory(qgis_iface):  # pylint: disable=invalid-name
    """Load Azenqos class from file Azenqos.

    :param qgis_iface: A QGIS interface instance.
    :type qgis_iface: QgsInterface
    """
    add_src_folder_to_import_path()
    import check_and_install_requirements
    if os.name == "nt":
        if not check_and_install_requirements.check_and_install_requirements():
            msgBox = QMessageBox(None)
            msgBox.setWindowTitle("Restart")
            msgBox.setText("Please restart QGIS")
            msgBox.addButton(QPushButton("OK"), QMessageBox.YesRole)
            msgBox.exec_()
    
    from azenqos_qgis_plugin import azenqos_qgis_plugin
    return azenqos_qgis_plugin(qgis_iface)
