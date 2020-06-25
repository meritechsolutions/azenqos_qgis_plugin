from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys


class HeaderContent(QWidget):
    def __init__(self, item=None):
        super().__init__(None)
        self.treeItem = item
        self.headerName = self.treeItem.text(0)
        self.setupUi()

    def setupUi(self):
        self.setObjectName("HeaderContent")
        self.resize(420, 360)

        self.tabWidget = QTabWidget(self)
        self.tabWidget.setGeometry(QRect(20, 20, 381, 291))
        self.tabWidget.setObjectName("tabWidget")

        self.headerTab = QWidget()
        self.headerTab.setObjectName("HeaderTab")

        self.formLayoutWidget = QWidget(self.headerTab)
        self.formLayoutWidget.setGeometry(QRect(10, 30, 361, 31))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QFormLayout(self.formLayoutWidget)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")

        self.lblName = QLabel(self.formLayoutWidget)
        self.lblName.setObjectName("lblName")
        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.lblName)

        self.leName = QLineEdit(self.headerName, self.formLayoutWidget)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.leName.sizePolicy().hasHeightForWidth())
        self.leName.setSizePolicy(sizePolicy)
        self.leName.setObjectName("leName")
        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.leName)
        self.tabWidget.addTab(self.headerTab, "")

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setGeometry(QRect(250, 320, 164, 32))
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.accepted.connect(self.changeHeaderName)

        self.retranslateUi()
        self.tabWidget.setCurrentIndex(0)
        QMetaObject.connectSlotsByName(self)

    def changeHeaderName(self):
        self.treeItem.setText(0, self.leName.text())
        self.close()

    def retranslateUi(self):
        _translate = QCoreApplication.translate
        self.setWindowTitle(_translate("HeaderContent", "Form"))
        self.lblName.setText(_translate("HeaderContent", "Name"))
        # self.leName.setText(self.treeItem.text(0))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.headerTab),
            _translate("HeaderContent", "Header"),
        )


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     ex = HeaderContent()
#     ex.show()
#     sys.exit(app.exec_())
