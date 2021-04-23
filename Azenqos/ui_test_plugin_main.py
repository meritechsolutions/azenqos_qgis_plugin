from PyQt5.QtWidgets import QApplication

import azenqos_qgis_plugin


def test():
    app = QApplication([])
    azq = azenqos_qgis_plugin.azenqos_qgis_plugin(app)
    azq.run()


if __name__ == "__main__":
    test()
