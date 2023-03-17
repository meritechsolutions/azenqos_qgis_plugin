import os
import sys
import time
import asyncio

# Adding folder path
from PyQt5 import QtCore
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QSlider

sys.path.insert(1, os.path.dirname(os.path.realpath(__file__)))

import numpy as np


class timeSlider(QSlider):
    def __init__(self, parent, gc):
        super().__init__(parent)
        self.gc = parent.gc
        self.update()

    def update(self):
        # Set integer max and min on parent. These stay constant.
        # self._min_int = self.gc.minTimeValue
        super().setMinimum(0)
        self._max_int = int(self.gc.sliderLength)
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
        print(
            "ts setValue:",
            value,
            "self._value_range",
            self._value_range,
            "self._max_int",
            self._max_int,
        )
        resultValue = value / self._value_range * self._max_int
        resultValue = round(resultValue)
        super().setValue(resultValue)
        # super().repaint()

    def setMinimum(self, value):
        self.setRange(value, self._max_value)

    def setMaximum(self, value):
        self.setRange(self._min_value, value)

    def setRange(self, minimum, maximum):
        # old_value = self.value()
        self._min_value = minimum
        self._max_value = maximum
        # self.setValue(old_value)  # Put slider in correct position
        self.update()

    def proportion(self):
        return (self.value() - self._min_value) / self._value_range


class timeSliderThread(QThread):
    changeValue = pyqtSignal(float)

    def __init__(self, gc):
        QThread.__init__(self)
        self.gc = gc
        self.currentSliderValue = None

    def __del__(self):
        try:
            self.wait()
        except:
            pass

    def run(self):
        asyncio.run(self.playTime())

    def getCurrentValue(self):
        if self.currentSliderValue:
            return self.currentSliderValue
        else:
            return 0

    async def playTime(self):
        self.gc.timeSlider.setDisabled(True)
        timeskip = 0
        if float(1 / self.gc.fastForwardValue) >= 0.25:
            sleeptime = 1 / self.gc.fastForwardValue
        else:
            sleeptime = 0.25
            timeskip = (self.gc.fastForwardValue - (1 / sleeptime)) * sleeptime

        # self.gc.isSliderPlay = True
        if self.gc.isSliderPlay:
            print(
                "timeslider self.currentSliderValue: {}".format(self.currentSliderValue)
            )
            if self.currentSliderValue:
                while self.gc.isSliderPlay and self.currentSliderValue < self.gc.sliderLength:
                    await asyncio.sleep(sleeptime)
                    value = self.gc.timeSlider.value() + ((1 * self.gc.slowDownValue) + timeskip)
                    self.gc.selected_point_match_dict["log_hash"] = None
                    self.changeValue.emit(value)
                    self.currentSliderValue += ((1 * self.gc.slowDownValue) + timeskip)
                    
                if self.currentSliderValue >= self.gc.sliderLength:
                    self.gc.isSliderPlay = False
            else:
                x = 0
                while self.gc.isSliderPlay and x < self.gc.sliderLength:
                    await asyncio.sleep(sleeptime)
                    value = self.gc.timeSlider.value() + ((1 * self.gc.slowDownValue) + timeskip)
                    self.changeValue.emit(value)
                    x += ((1 * self.gc.slowDownValue) + timeskip)
                    
                if x >= self.gc.sliderLength:
                    self.gc.isSliderPlay = False
        else:
            self.quit()

    def set(self, value):
        self.currentSliderValue = value
