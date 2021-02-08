# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Azenqos
                                 A QGIS plugin
 Azenqos Plugin
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-03-18
        git sha              : $Format:%H$
        copyright            : Copyright (C) 2019-2020 Freewill FX Co., Ltd. All rights reserved
        email                : gritmanoch@longdo.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from PyQt5 import *
from PyQt5.QtWidgets import *
import sys
import traceback
# Initialize Qt resources from file resources.py
from resources import *

# Import the code for the dialog
import os.path


class azenqos_qgis_plugin:
    """QGIS Plugin Implementation."""

    def __init__(self, qgis_iface):
        """Constructor.

        :param qgis_iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type qgis_iface: QgsInterface
        """
        
        from PyQt5.QtCore import QT_VERSION_STR    
        print("azenqos_qgis_plugin start - detected qt_version: {}".format(QT_VERSION_STR))

        # Save reference to the QGIS interface
        self.qgis_iface = qgis_iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value("locale/userLocale")
        if locale:
            locale = locale[0:2]
            locale_path = os.path.join(
                self.plugin_dir, "i18n", "Azenqos_{}.qm".format(locale)
            )

            if os.path.exists(locale_path):
                self.translator = QTranslator()
                self.translator.load(locale_path)

                if qVersion() > "4.3.3":
                    QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u"&Azenqos")

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None
        self.dlg = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate("Azenqos", message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None,
    ):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.qgis_iface.addToolBarIcon(action)

        if add_to_menu:
            self.qgis_iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        dirname = os.path.dirname(__file__)
        # icon_path = ":/plugins/azenqos_plugin/icon.png"
        icon_path = os.path.join(dirname, "icon.png")
        self.add_action(
            icon_path,
            text=self.tr(u"Azenqos Log"),
            callback=self.run,
            parent=self.qgis_iface.mainWindow(),
        )

        # will be set False in run()
        self.first_start = True

    def unload(self):
        print("azenqos_plugin: unload()")
        try:
            if self.dlg is not None:
                if hasattr(self.dlg, "azenqosMainMenu") is True:
                    self.dlg.azenqosMainMenu.cleanup()
                    self.dlg.azenqosMainMenu.close()
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print("WARNING: unload()0  exception:", exstr)

        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            try:
                self.qgis_iface.removePluginMenu(self.tr(u"&Azenqos"), action)
                self.qgis_iface.removeToolBarIcon(action)
            except:
                type_, value_, traceback_ = sys.exc_info()
                exstr = str(traceback.format_exception(type_, value_, traceback_))
                print("WARNING: unload()1 itr exception:", exstr)


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.dlg is None:
            self.first_start = False
            import main_window            
            self.dlg = main_window.main_window(self.qgis_iface)
            
        if self.dlg is not None:
            # show the dialog
            self.dlg.show()


def ask_operation_mode():
    msgBox = QMessageBox()
    msgBox.setWindowTitle('Operation mode')
    msgBox.setText('Please choose operation mode:')
    msgBox.addButton(QPushButton('ONLINE - AZENQOS Cloud Analytics'), QMessageBox.YesRole)
    msgBox.addButton(QPushButton('OFFLINE - AZENQOS .AZM logfile'), QMessageBox.NoRole)
    reply = msgBox.exec_()
    return reply
