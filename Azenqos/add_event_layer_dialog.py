import PyQt5
from PyQt5.QtWidgets import QDialog, QCompleter, QComboBox
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon, QPixmap
import os
from add_param_dialog import CustomQCompleter
import azq_utils
import contextlib
import pandas as pd
import sqlite3


class add_event_layer_dialog(QDialog):
    def __init__(self, event_list, gc):
        super(add_event_layer_dialog, self).__init__(None)
        self.setAttribute(PyQt5.QtCore.Qt.WA_DeleteOnClose)
        self.event_list = event_list
        self.selected_event = self.event_list[0]
        self.gc = gc
        self.setupUi()

    def setupUi(self):
        dirname = os.path.dirname(__file__)
        self.ui = loadUi(azq_utils.get_module_fp("add_event_layer_dialog.ui"), self)
        self.setWindowIcon(QIcon(QPixmap(os.path.join(dirname, "icon.png"))))
        self.setWindowTitle("Add Event Layer")
        self.ui.event_combo_box.setEditable(True)
        self.ui.event_combo_box.setInsertPolicy(QComboBox.NoInsert)
        completer = CustomQCompleter(self.ui.event_combo_box)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setModel(self.ui.event_combo_box.model())
        self.ui.event_combo_box.setCompleter(completer)
        for event in self.event_list:
            self.ui.event_combo_box.addItem(event)
        self.accepted.connect(self.on_ok_button_click)
    
    def on_ok_button_click(self):
        dirname = os.path.dirname(__file__)
        icon_fp = None
        self.selected_event = self.ui.event_combo_box.currentText()
        with contextlib.closing(sqlite3.connect(self.gc.databasePath)) as dbcon:
            event_df = pd.read_sql("select * from events where name = '{}'".format(self.selected_event), dbcon)
        event_id = event_df["event_id"][0]
        icon_fp = os.path.join(dirname, "event_icon", str(event_id) + ".bmp")
        if not os.path.isfile(icon_fp):
            icon_fp = os.path.join(dirname, "event_icon", "event.bmp")
        azq_utils.create_layer_in_qgis(self.gc.databasePath, event_df, self.selected_event, is_indoor=self.gc.is_indoor, icon_fp=icon_fp)