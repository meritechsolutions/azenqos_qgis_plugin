# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Cell_content.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class HeaderContent(QtWidgets.QWidget):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        self.setupUi()

    def setupUi(self):
        self.setObjectName("HeaderContent")
        self.resize(420, 360)
        self.tabWidget = QtWidgets.QTabWidget(self)
        self.tabWidget.setGeometry(QtCore.QRect(20, 20, 381, 291))
        self.tabWidget.setObjectName("tabWidget")
        self.headerTab = QtWidgets.QWidget()
        self.headerTab.setObjectName("HeaderTab")
        self.formLayoutWidget = QtWidgets.QWidget(self.headerTab)
        self.formLayoutWidget.setGeometry(QtCore.QRect(10, 30, 361, 31))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        self.lblName = QtWidgets.QLabel(self.formLayoutWidget)
        self.lblName.setObjectName("lblName")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.lblName)
        self.leName = QtWidgets.QLineEdit(self.formLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.leName.sizePolicy().hasHeightForWidth())
        self.leName.setSizePolicy(sizePolicy)
        self.leName.setObjectName("leName")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.leName)
        self.tabWidget.addTab(self.headerTab, "")
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(250, 320, 164, 32))
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.retranslateUi()
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("HeaderContent", "Form"))
        self.lblName.setText(_translate("HeaderContent", "Name"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.HeaderTab), _translate("HeaderContent", "Header"))


