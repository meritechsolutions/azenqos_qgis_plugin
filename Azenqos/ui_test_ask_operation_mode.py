from PyQt5.QtWidgets import QApplication

import azenqos_qgis_plugin


def test():
    QApplication([])
    reply = azenqos_qgis_plugin.ask_operation_mode()
    print("reply: {}".format(reply))


if __name__ == "__main__":
    test()
