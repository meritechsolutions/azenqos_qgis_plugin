import sys
import traceback

from PyQt5.QtCore import pyqtSlot, QRunnable

import tshark_util
from worker import WorkerSignals


class TsharkDecodeWorker(QRunnable):
    ret = None

    def __init__(self, gc, name, side, protocol, detail):
        assert name is not None
        assert side is not None
        assert protocol is not None
        assert detail is not None
        super(TsharkDecodeWorker, self).__init__()
        self.gc = gc
        self.name = name
        self.side = side
        self.protocol = protocol
        self.detail = detail
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        result = ""
        try:
            result = tshark_util.tshark_decode_hex(self.side, self.name, self.protocol, self.detail)
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print("WARNING: tsharkworker - exception: {}".format(exstr))
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


