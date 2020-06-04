import datetime
import threading
import sys
import os

# Adding folder path
sys.path.insert(1, os.path.dirname(os.path.realpath(__file__)))

import pyqtgraph as pg
import numpy as np
import global_config as gc

from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *  # QAbstractTableModel, QVariant, Qt, pyqtSignal, QThread
from PyQt5.QtSql import *  # QSqlQuery, QSqlDatabase
from PyQt5.QtGui import *
from qgis.core import *
from qgis.utils import *
from qgis.gui import *


class timeSlider(QSlider):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set integer max and min on parent. These stay constant.
        # self._min_int = gc.minTimeValue
        super().setMinimum(0)
        self._max_int = int(gc.sliderLength * 1000)
        super().setMaximum(self._max_int)
        # The "actual" min and max values seen by user.
        self._min_value = 0.0
        self._max_value = gc.maxTimeValue - gc.minTimeValue

    @property
    def _value_range(self):
        return self._max_value - self._min_value

    def value(self):
        thisValue = float(super().value())
        value = thisValue / self._max_int * self._value_range
        return value

    def setValue(self, value):
        resultValue = value / self._value_range * self._max_int
        resultValue = round(resultValue)
        super().setValue(resultValue)
        # super().repaint()

    def setMinimum(self, value):
        self.setRange(value, self._max_value)

    def setMaximum(self, value):
        self.setRange(self._min_value, value)

    def setRange(self, minimum, maximum):
        old_value = self.value()
        self._min_value = minimum
        self._max_value = maximum
        self.setValue(old_value)  # Put slider in correct position

    def proportion(self):
        return (self.value() - self._min_value) / self._value_range


class timeSliderThread(QThread):
    changeValue = pyqtSignal(float)

    def __init__(self):
        QThread.__init__(self)
        self.currentSliderValue = None

    def __del__(self):
        self.wait()

    def run(self):
        self.playTime()

    def getCurrentValue(self):
        return self.currentSliderValue

    def playTime(self):
        gc.timeSlider.setDisabled(True)
        sleeptime = 1 / gc.fastForwardValue
        # gc.isSliderPlay = True
        if gc.isSliderPlay:
            if self.currentSliderValue:
                for x in np.arange(
                    self.currentSliderValue, gc.sliderLength, (1 * gc.slowDownValue)
                ):
                    if not gc.isSliderPlay:
                        break
                    else:
                        time.sleep(sleeptime)
                        value = gc.timeSlider.value() + (1 * gc.slowDownValue)
                        self.changeValue.emit(value)

                    if x >= gc.sliderLength:
                        gc.isSliderPlay = False
                        break
            else:
                for x in np.arange(0, gc.sliderLength, (1 * gc.slowDownValue)):
                    if not gc.isSliderPlay:
                        break
                    else:
                        time.sleep(sleeptime)
                        value = gc.timeSlider.value() + (1 * gc.slowDownValue)
                        self.changeValue.emit(value)

                    if x >= gc.sliderLength:
                        gc.isSliderPlay = False
                        break
        else:
            self.quit()

    def set(self, value):
        self.currentSliderValue = value
