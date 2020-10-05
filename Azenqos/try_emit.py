from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import *
import sys


class Main(QWidget):
    def __init__(self):
        super().__init__()

        self.test = ExecuteThread()
        self.test.start()
        self.test.my_signal.connect(self.my_event)

    def thread_finished(self):
        # gets executed if thread finished
        pass

    def my_event(self):
        # gets executed on my_signal
        print("my_event")
        pass


class ExecuteThread(QThread):
    my_signal = pyqtSignal()

    def run(self):
        # do something here
        print("execthread run()")
        self.my_signal.emit()
        pass


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Main()
    window.show()
    app.exec_()
