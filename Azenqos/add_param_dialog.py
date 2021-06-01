import PyQt5
from PyQt5.QtWidgets import QDialog, QCompleter, QComboBox
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSortFilterProxyModel
import os
from functools import partial
import azq_utils
import preprocess_azm


class AddParamDialog(QDialog):
    def __init__(self, onParamAdded):
        super(AddParamDialog, self).__init__(None)
        self.paramDF = preprocess_azm.get_number_param()
        self.paramDF = self.paramDF.reset_index(drop=True)
        self.onParamAdded = onParamAdded
        self.param = self.paramDF["var_name"][0]
        self.paramName = None
        self.arg = "1"
        self.argCount = "1"
        self.isNotNull = False
        self.isData = False
        self.setAttribute(PyQt5.QtCore.Qt.WA_DeleteOnClose)
        self.setupUi()

    def setupUi(self):
        dirname = os.path.dirname(__file__)
        self.ui = loadUi(azq_utils.get_local_fp("add_param_dialog.ui"), self)
        self.setWindowIcon(QIcon(QPixmap(os.path.join(dirname, "icon.png"))))
        self.setWindowTitle("Add Parameter")
        self.ui.comboBox_2.addItem(self.arg)
        self.ui.comboBox.setEditable(True)
        self.ui.comboBox.setInsertPolicy(QComboBox.NoInsert)
        completer = CustomQCompleter(self.ui.comboBox)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setModel(self.ui.comboBox.model())
        self.ui.comboBox.setCompleter(completer)
        if not preprocess_azm.is_leg_nr_tables():
            self.ui.not_null_checkbox.hide()
        enableNotNullSlot = partial(self.checkNotNull, self.ui.not_null_checkbox)
        disableNotNullSlot = partial(self.unCheckNotNull, self.ui.not_null_checkbox)
        self.ui.not_null_checkbox.stateChanged.connect(
            lambda x: enableNotNullSlot() if x else disableNotNullSlot()
        )
        enableDataSlot = partial(self.checkData, self.ui.data_checkbox)
        disableDataSlot = partial(self.uncheckData, self.ui.data_checkbox)
        self.ui.data_checkbox.stateChanged.connect(
            lambda x: enableDataSlot() if x else disableDataSlot()
        )
        for index, row in self.paramDF.iterrows():
            self.ui.comboBox.addItem(row.var_name)
        self.ui.comboBox.currentIndexChanged.connect(self.selectParam)
        self.ui.comboBox_2.currentIndexChanged.connect(self.selectArg)
        self.paramName = self.param
        if int(self.argCount) > 1:
            self.paramName = self.param + "_" + self.arg
        self.accepted.connect(self.onOkButtonClick)

    def checkNotNull(self, checkbox):
        self.isNotNull = True

    def unCheckNotNull(self, checkbox):
        self.isNotNull = False

    def checkData(self, checkbox):
        self.isData = True

    def uncheckData(self, checkbox):
        self.isData = False

    def selectParam(self):
        self.setParam()
        self.ui.comboBox_2.clear()
        self.argCount = self.paramDF.loc[
            self.paramDF["var_name"] == self.param, "n_arg_max"
        ].item()
        for i in range(int(self.argCount)):
            n = i + 1
            self.ui.comboBox_2.addItem(str(n))
        self.paramName = self.param
        if int(self.argCount) > 1:
            self.paramName = self.param + "_" + self.arg

    def selectArg(self):
        self.setArg()
        self.paramName = self.param
        if int(self.argCount) > 1:
            self.paramName = self.param + "_" + self.arg

    def setParam(self):
        self.param = self.ui.comboBox.currentText()

    def setArg(self):
        self.arg = self.ui.comboBox_2.currentText()

    def onOkButtonClick(self):
        self.onParamAdded(
            {"name": self.paramName, "null": self.isNotNull, "data": self.isData}
        )


class CustomQCompleter(QCompleter):
    def __init__(self, parent=None):
        super(CustomQCompleter, self).__init__(parent)
        self.local_completion_prefix = ""
        self.source_model = None

    def setModel(self, model):
        self.source_model = model
        super(CustomQCompleter, self).setModel(self.source_model)

    def updateModel(self):
        local_completion_prefix = self.local_completion_prefix

        class InnerProxyModel(QSortFilterProxyModel):
            def filterAcceptsRow(self, sourceRow, sourceParent):
                index0 = self.sourceModel().index(sourceRow, 0, sourceParent)
                return (
                    local_completion_prefix.lower()
                    in self.sourceModel().data(index0).lower()
                )

        proxy_model = InnerProxyModel()
        proxy_model.setSourceModel(self.source_model)
        super(CustomQCompleter, self).setModel(proxy_model)

    def splitPath(self, path):
        self.local_completion_prefix = path
        self.updateModel()
        return [""]
