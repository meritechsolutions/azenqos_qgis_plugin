from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5 import QtCore
from PyQt5.uic import loadUi
import os
import azq_utils
import color_button


class ColorDialog(QDialog):
    def __init__(self, name=None, color=None, onColorSet=None):
        super(ColorDialog, self).__init__(None)
        self._color = color
        self._name = name
        self._onColorSet = onColorSet
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setupUi()

    def setupUi(self):
        dirname = os.path.dirname(__file__)
        self.ui = loadUi(azq_utils.get_module_fp("color_dialog.ui"), self)
        self.setWindowIcon(QIcon(QPixmap(os.path.join(dirname, "icon.png"))))
        self.setWindowTitle("Change Line Color")
        self.ui.label.setText(self._name)
        self.ui.horizontalLayout_2.addWidget(
            color_button.ColorButton(self._name, self._color, self._onColorSet)
        )
