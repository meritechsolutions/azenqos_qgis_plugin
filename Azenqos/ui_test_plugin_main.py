import azenqos_plugin
from PyQt5.QtWidgets import *


def test():
    app = QApplication([])
    azq = azenqos_plugin.Azenqos(app)
    azq.run()


if __name__ == "__main__":
    test()
