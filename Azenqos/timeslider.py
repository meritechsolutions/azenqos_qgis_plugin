import datetime
import threading
import sys
import os

# Adding folder path
sys.path.insert(1, os.path.dirname(os.path.realpath(__file__)))

import pyqtgraph as pg
import numpy as np

from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *  # QAbstractTableModel, QVariant, Qt, pyqtSignal, QThread
from PyQt5.QtSql import *  # QSqlQuery, QSqlDatabase
from PyQt5.QtGui import *

try:
    from qgis.core import *
    from qgis.utils import *
    from qgis.gui import *
except:
    pass


class timeSlider(QSlider):
    def __init__(self, parent, gc):
        super().__init__(parent)
        self.gc = parent.gc

        # Set integer max and min on parent. These stay constant.
        # self._min_int = self.gc.minTimeValue
        super().setMinimum(0)
        self._max_int = int(self.gc.sliderLength * 1000)
        super().setMaximum(self._max_int)
        # The "actual" min and max values seen by user.
        self._min_value = 0.0
        try:
            self._max_value = self.gc.maxTimeValue - self.gc.minTimeValue
        except:
            self._max_value = 99

    @property
    def _value_range(self):
        return self._max_value - self._min_value

    def value(self):
        thisValue = float(super().value())
        try:
            value = thisValue / self._max_int * self._value_range
        except:
            return 0
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

    def __init__(self, gc):
        QThread.__init__(self)
        self.gc = gc
        self.currentSliderValue = None

    def __del__(self):
        self.wait()

    def run(self):
        self.playTime()

    def getCurrentValue(self):
        if self.currentSliderValue:
            return self.currentSliderValue
        else:
            return 0

    def playTime(self):
        self.gc.timeSlider.setDisabled(True)
        timeskip = 0
        if float(1 / self.gc.fastForwardValue) >= 0.25:
            sleeptime = 1 / self.gc.fastForwardValue
        else:
            sleeptime = 0.25
            timeskip = (self.gc.fastForwardValue - (1 / sleeptime)) * sleeptime

        # self.gc.isSliderPlay = True
        if self.gc.isSliderPlay:
            print("timeslider self.currentSliderValue: {}".format(self.currentSliderValue))
            if self.currentSliderValue:
                for x in np.arange(
                    self.currentSliderValue,
                    self.gc.sliderLength,
                    ((1 * self.gc.slowDownValue) + timeskip),
                ):
                    if not self.gc.isSliderPlay:
                        break
                    else:
                        time.sleep(sleeptime)
                        value = self.gc.timeSlider.value() + (
                            (1 * self.gc.slowDownValue) + timeskip
                        )
                        print("timeslider upper emit: {}".format(value))
                        self.changeValue.emit(value)

                    if x >= self.gc.sliderLength:
                        self.gc.isSliderPlay = False
                        break
            else:
                for x in np.arange(
                    0, self.gc.sliderLength, ((1 * self.gc.slowDownValue) + timeskip)
                ):
                    if not self.gc.isSliderPlay:
                        break
                    else:
                        time.sleep(sleeptime)
                        value = self.gc.timeSlider.value() + (
                            (1 * self.gc.slowDownValue) + timeskip
                        )
                        print("timeslider lower emit: {}".format(value))
                        self.changeValue.emit(value)

                    if x >= self.gc.sliderLength:
                        self.gc.isSliderPlay = False
                        break
        else:
            self.quit()

    def set(self, value):
        self.currentSliderValue = value
