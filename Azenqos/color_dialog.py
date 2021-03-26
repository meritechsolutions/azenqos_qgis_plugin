from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtSql import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi
import os
import pandas as pd
import numpy as np
import azq_utils
import color_button

class color_dialog(QDialog):


    def __init__(self, name=None, color=None, onColorSet=None):
        super(color_dialog, self).__init__(None)
        self._color = color
        self._name = name
        self._onColorSet = onColorSet
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setupUi()

    def setupUi(self):
        dirname = os.path.dirname(__file__)
        self.ui = loadUi(azq_utils.get_local_fp("color_dialog.ui"), self)
        self.setWindowIcon(QIcon(QPixmap(os.path.join(dirname, "icon.png"))))
        self.setWindowTitle("Change Line Color")
        self.ui.label.setText(self._name)
        self.ui.horizontalLayout_2.addWidget(color_button.ColorButton(self._name, self._color, self._onColorSet))


