import datetime
import sys

from PyQt5 import QtWidgets

import analyzer_vars
import integration_test_helpers
import linechart_multi_y_axis


def test():
    azmfp = "../example_logs/lte_benchmark/357008080503008-26_08_2020-16_18_08.azm"
    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp(azmfp)
    gc = analyzer_vars.analyzer_vars()
    gc.databasePath = dbfp

    app = QtWidgets.QApplication(sys.argv)
    main = linechart_multi_y_axis.LineChart(
        gc,
        paramList=[
            {"name": "lte_sinr_1", "null": False, "data": False},
            {"name": "lte_inst_rsrp_1", "null": False, "data": False},
            {"name": "lte_inst_rsrq_1", "null": False, "data": False},
            {"name": "lte_inst_rssi_1", "null": False, "data": False},
        ],
    )

    def updateTime(epoch):
        time = datetime.datetime.fromtimestamp(epoch)
        main.updateTime(time)

    main.timeSelected.connect(updateTime)
    main.updateTime(
        datetime.datetime.strptime("2020-08-26 16:16:30.687", "%Y-%m-%d %H:%M:%S.%f")
    )
    main.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    test()
