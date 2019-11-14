# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'form.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import sys


class PropertiesWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=None)
        self.setupUi()

    def setupUi(self):
        self.setObjectName("Properties")
        self.setFixedSize(360,360)
        self.setMouseTracking(False)
        self.verticalLayoutWidget = QtWidgets.QWidget(self)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 360, 300))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(10, 20, 10, 10)
        self.verticalLayout.setObjectName("verticalLayout")

        self.tabWidget = QtWidgets.QTabWidget(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.North)
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tabWidget.setElideMode(QtCore.Qt.ElideRight)
        self.tabWidget.setObjectName("tabWidget")

        self.setupTableTab()
        self.setupContentTab()

        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(13, 310, 331, 32))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.buttonBox.setFont(font)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok|QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.accepted.connect(self.close)
        self.buttonBox.rejected.connect(self.close)

        self.verticalLayout.addWidget(self.tabWidget)

        self.retranslateUi()
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self)

    def createTable(self):
        return False

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Properties", "Properties"))
        self.lblTitle.setText(_translate("Properties", "Title"))
        self.lblRow.setText(_translate("Properties", "Row"))
        self.lblColumns.setText(_translate("Properties", "Columns"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Table), _translate("Properties", "Table"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.CellContent), _translate("Properties", "Cell Content"))
        self.editBtn.setText(_translate("Properties", "Edit"))
        self.mobileLbl.setText(_translate("Properties", "Mobile"))
        self.setAllBtn.setText(_translate("Properties", "Set All"))

    def setupTableTab(self):
        self.Table = QtWidgets.QWidget()
        self.Table.setEnabled(True)
        self.Table.setObjectName("Table")
        self.formLayoutWidget = QtWidgets.QWidget(self.Table)
        self.formLayoutWidget.setGeometry(QtCore.QRect(0, 0, 331, 301))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.formLayout.setContentsMargins(30, 20, 10, 10)
        self.formLayout.setSpacing(10)
        self.formLayout.setObjectName("formLayout")
        self.lblTitle = QtWidgets.QLabel(self.formLayoutWidget)
        self.lblTitle.setObjectName("lblTitle")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.lblTitle)
        self.ledtTitle = QtWidgets.QLineEdit(self.formLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ledtTitle.sizePolicy().hasHeightForWidth())
        self.ledtTitle.setSizePolicy(sizePolicy)
        self.ledtTitle.setObjectName("ledtTitle")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.ledtTitle)
        self.lblRow = QtWidgets.QLabel(self.formLayoutWidget)
        self.lblRow.setObjectName("lblRow")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.lblRow)
        self.cbColumns = QtWidgets.QComboBox(self.formLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbColumns.sizePolicy().hasHeightForWidth())
        self.cbColumns.setSizePolicy(sizePolicy)
        self.cbColumns.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.cbColumns.setObjectName("cbColumns")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.cbColumns)
        self.lblColumns = QtWidgets.QLabel(self.formLayoutWidget)
        self.lblColumns.setObjectName("lblColumns")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.lblColumns)
        self.cbRow = QtWidgets.QComboBox(self.formLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbRow.sizePolicy().hasHeightForWidth())
        self.cbRow.setSizePolicy(sizePolicy)
        self.cbRow.setObjectName("cbRow")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.cbRow)
        self.tabWidget.addTab(self.Table, "")

    def setupContentTab(self):
        self.CellContent = QtWidgets.QWidget()
        self.CellContent.setObjectName("CellContent")
        self.treeView = QtWidgets.QTreeView(self.CellContent)
        self.treeView.setGeometry(QtCore.QRect(10, 20, 251, 192))
        self.treeView.setObjectName("treeView")
        self.editBtn = QtWidgets.QPushButton(self.CellContent)
        self.editBtn.setGeometry(QtCore.QRect(262, 20, 71, 31))
        self.editBtn.setObjectName("editBtn")
        self.mobileLbl = QtWidgets.QLabel(self.CellContent)
        self.mobileLbl.setGeometry(QtCore.QRect(10, 220, 61, 31))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.mobileLbl.setFont(font)
        self.mobileLbl.setObjectName("mobileLbl")
        self.mobileCb = QtWidgets.QComboBox(self.CellContent)
        self.mobileCb.setGeometry(QtCore.QRect(60, 220, 71, 31))
        self.mobileCb.setObjectName("mobileCb")
        self.setAllBtn = QtWidgets.QPushButton(self.CellContent)
        self.setAllBtn.setGeometry(QtCore.QRect(130, 220, 91, 32))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.setAllBtn.setFont(font)
        self.setAllBtn.setObjectName("setAllBtn")
        self.tabWidget.addTab(self.CellContent, "")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ex = PropertiesWindow()
    ex.show()
    sys.exit(app.exec_())