from PyQt5 import QtGui, Qt
from PyQt5.QtCore import QRect, QSize, QCoreApplication, QMetaObject, QDir
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QWidget,
    QGroupBox,
    QSizePolicy,
    QCheckBox,
    QComboBox,
    QLabel,
    QLineEdit,
    QToolButton,
    QFileDialog,
    QDialogButtonBox,
)


class CellInformation(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

    def setupUi(self, CellInformation):
        CellInformation.setObjectName("Cell Information")
        CellInformation.resize(640, 522)
        CellInformation.setGeometry(QRect(0, 0, 640, 522))
        CellInformation.setMinimumSize(640, 522)
        self.verticalLayoutWidget = QWidget(CellInformation)
        self.verticalLayoutWidget.setGeometry(QRect(0, 320, 601, 151))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.SettingLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.SettingLayout.setContentsMargins(10, 10, 10, 10)
        self.SettingLayout.setObjectName("SettingLayout")
        self.Setting = QGroupBox(self.verticalLayoutWidget)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Setting.sizePolicy().hasHeightForWidth())
        self.Setting.setSizePolicy(sizePolicy)
        self.Setting.setMinimumSize(QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.Setting.setFont(font)
        self.Setting.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignTop)
        self.Setting.setObjectName("Setting")
        self.OpacityCheckbox = QCheckBox(self.Setting)
        self.OpacityCheckbox.setGeometry(QRect(30, 30, 86, 31))
        self.OpacityCheckbox.setObjectName("OpacityCheckbox")
        self.PercentageCombobox = QComboBox(self.Setting)
        self.PercentageCombobox.setGeometry(QRect(100, 30, 71, 31))
        self.PercentageCombobox.setObjectName("PercentageCombobox")
        self.PercentageLabel = QLabel(self.Setting)
        self.PercentageLabel.setGeometry(QRect(170, 30, 21, 31))
        self.PercentageLabel.setObjectName("PercentageLabel")
        self.CellDefinitionLabel = QLabel(self.Setting)
        self.CellDefinitionLabel.setGeometry(QRect(30, 70, 121, 16))
        self.CellDefinitionLabel.setObjectName("CellDefinitionLabel")
        self.CellDefinitionCombobox = QComboBox(self.Setting)
        self.CellDefinitionCombobox.setGeometry(QRect(160, 60, 121, 41))
        self.CellDefinitionCombobox.setObjectName("CellDefinitionCombobox")
        self.SearchCellDistanceLabel = QLabel(self.Setting)
        self.SearchCellDistanceLabel.setGeometry(QRect(30, 100, 131, 16))
        self.SearchCellDistanceLabel.setObjectName("SearchCellDistanceLabel")
        self.KiloAmount = QLineEdit(self.Setting)
        self.KiloAmount.setGeometry(QRect(180, 100, 61, 21))
        self.KiloAmount.setObjectName("KiloAmount")
        self.KilometerLabel = QLabel(self.Setting)
        self.KilometerLabel.setGeometry(QRect(260, 100, 59, 16))
        self.KilometerLabel.setObjectName("KilometerLabel")
        self.SettingLayout.addWidget(self.Setting)
        self.verticalLayoutWidget_2 = QWidget(CellInformation)
        self.verticalLayoutWidget_2.setGeometry(QRect(0, 0, 601, 321))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.CellLayout = QVBoxLayout(self.verticalLayoutWidget_2)
        self.CellLayout.setContentsMargins(10, 20, 10, 10)
        self.CellLayout.setObjectName("CellLayout")
        self.CellDefinitionFile = QGroupBox(self.verticalLayoutWidget_2)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.CellDefinitionFile.sizePolicy().hasHeightForWidth()
        )
        self.CellDefinitionFile.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(13)
        self.CellDefinitionFile.setFont(font)
        self.CellDefinitionFile.setObjectName("CellDefinitionFile")
        self.FilePath4 = QLineEdit(self.CellDefinitionFile)
        self.FilePath4.setGeometry(QRect(110, 270, 341, 21))
        self.FilePath4.setObjectName("FilePath4")
        self.CdmaCellFileCheckbox = QCheckBox(self.CellDefinitionFile)
        self.CdmaCellFileCheckbox.setGeometry(QRect(30, 240, 151, 20))
        self.CdmaCellFileCheckbox.setObjectName("CdmaCellFileCheckbox")
        self.LteCellFileCheckbox = QCheckBox(self.CellDefinitionFile)
        self.LteCellFileCheckbox.setGeometry(QRect(30, 170, 131, 20))
        self.LteCellFileCheckbox.setObjectName("LteCellFileCheckbox")
        self.FilePath2 = QLineEdit(self.CellDefinitionFile)
        self.FilePath2.setGeometry(QRect(110, 130, 341, 21))
        self.FilePath2.setObjectName("FilePath2")
        self.FilenameLabel1 = QLabel(self.CellDefinitionFile)
        self.FilenameLabel1.setGeometry(QRect(40, 60, 59, 16))
        self.FilenameLabel1.setObjectName("FilenameLabel1")
        self.FilenameLabel4 = QLabel(self.CellDefinitionFile)
        self.FilenameLabel4.setGeometry(QRect(40, 270, 59, 16))
        self.FilenameLabel4.setObjectName("FilenameLabel4")
        self.WcdmaCellFileCheckbox = QCheckBox(self.CellDefinitionFile)
        self.WcdmaCellFileCheckbox.setGeometry(QRect(30, 100, 161, 20))
        self.WcdmaCellFileCheckbox.setObjectName("WcdmaCellFileCheckbox")
        self.FilePath1 = QLineEdit(self.CellDefinitionFile)
        self.FilePath1.setGeometry(QRect(110, 60, 341, 21))
        self.FilePath1.setObjectName("FilePath1")
        self.FilePath3 = QLineEdit(self.CellDefinitionFile)
        self.FilePath3.setGeometry(QRect(110, 200, 341, 21))
        self.FilePath3.setObjectName("FilePath3")
        self.FilenameLabel3 = QLabel(self.CellDefinitionFile)
        self.FilenameLabel3.setGeometry(QRect(40, 200, 59, 16))
        self.FilenameLabel3.setObjectName("FilenameLabel3")
        self.GsmCellFileCheckbox = QCheckBox(self.CellDefinitionFile)
        self.GsmCellFileCheckbox.setGeometry(QRect(30, 30, 141, 20))
        self.GsmCellFileCheckbox.setObjectName("GsmCellFileCheckbox")
        self.FilenameLabel2 = QLabel(self.CellDefinitionFile)
        self.FilenameLabel2.setGeometry(QRect(40, 130, 59, 16))
        self.FilenameLabel2.setObjectName("FilenameLabel2")
        self.BrowseButton1 = QToolButton(self.CellDefinitionFile)
        self.BrowseButton1.setGeometry(QRect(460, 60, 51, 22))
        self.BrowseButton1.setObjectName("BrowseButton1")
        self.BrowseButton2 = QToolButton(self.CellDefinitionFile)
        self.BrowseButton2.setGeometry(QRect(460, 130, 51, 22))
        self.BrowseButton2.setObjectName("BrowseButton2")
        self.BrowseButton3 = QToolButton(self.CellDefinitionFile)
        self.BrowseButton3.setGeometry(QRect(460, 200, 51, 22))
        self.BrowseButton3.setObjectName("BrowseButton3")
        self.BrowseButton4 = QToolButton(self.CellDefinitionFile)
        self.BrowseButton4.setGeometry(QRect(460, 270, 51, 22))
        self.BrowseButton4.setObjectName("BrowseButton4")
        self.CellLayout.addWidget(self.CellDefinitionFile)
        self.verticalLayoutWidget_3 = QWidget(CellInformation)
        self.verticalLayoutWidget_3.setGeometry(QRect(0, 470, 601, 55))
        self.verticalLayoutWidget_3.setObjectName("verticalLayoutWidget_3")
        self.ButtonLayout = QVBoxLayout(self.verticalLayoutWidget_3)
        self.ButtonLayout.setContentsMargins(10, 10, 10, 10)
        self.ButtonLayout.setObjectName("ButtonLayout")
        self.buttonBox = QDialogButtonBox(self.verticalLayoutWidget_3)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.setObjectName("buttonBox")
        self.ButtonLayout.addWidget(self.buttonBox)

        self.BrowseButton1.clicked.connect(lambda: self.browseFile("1"))
        self.BrowseButton2.clicked.connect(lambda: self.browseFile("2"))
        self.BrowseButton3.clicked.connect(lambda: self.browseFile("3"))
        self.BrowseButton4.clicked.connect(lambda: self.browseFile("4"))

        self.retranslateUi(CellInformation)
        QMetaObject.connectSlotsByName(CellInformation)

    def retranslateUi(self, CellInformation):
        _translate = QCoreApplication.translate
        CellInformation.setWindowTitle(
            _translate("CellInformation", "Cell Information")
        )
        self.Setting.setTitle(_translate("CellInformation", "Setting"))
        self.OpacityCheckbox.setText(_translate("CellInformation", "Opacity"))
        self.PercentageLabel.setText(_translate("CellInformation", "%"))
        self.CellDefinitionLabel.setText(
            _translate("CellInformation", "Cell Definition Text")
        )
        self.SearchCellDistanceLabel.setText(
            _translate("CellInformation", "Search Cell Distance")
        )
        self.KilometerLabel.setText(_translate("CellInformation", "Kilometer"))
        self.CellDefinitionFile.setTitle(
            _translate("CellInformation", "Cell definition file")
        )
        self.CdmaCellFileCheckbox.setText(
            _translate("CellInformation", "Use CDMA cell file")
        )
        self.LteCellFileCheckbox.setText(
            _translate("CellInformation", "Use LTE cell file")
        )
        self.FilenameLabel1.setText(_translate("CellInformation", "Filename"))
        self.FilenameLabel4.setText(_translate("CellInformation", "Filename"))
        self.WcdmaCellFileCheckbox.setText(
            _translate("CellInformation", "Use WCDMA cell file")
        )
        self.FilenameLabel3.setText(_translate("CellInformation", "Filename"))
        self.GsmCellFileCheckbox.setText(
            _translate("CellInformation", "Use GSM cell file")
        )
        self.FilenameLabel2.setText(_translate("CellInformation", "Filename"))
        self.BrowseButton1.setText(_translate("CellInformation", "Browse"))
        self.BrowseButton2.setText(_translate("CellInformation", "Browse"))
        self.BrowseButton3.setText(_translate("CellInformation", "Browse"))
        self.BrowseButton4.setText(_translate("CellInformation", "Browse"))

    def browseFile(self, buttonNo):
        if buttonNo == "1":
            fileName, _ = QFileDialog.getOpenFileName(
                self, "Single File", QDir.rootPath(), "*.cel"
            )
            if fileName != "":

                self.FilePath1.setText(fileName)
            return False
        elif buttonNo == "2":
            fileName, _ = QFileDialog.getOpenFileName(
                self, "Single File", QDir.rootPath(), "*.cel"
            )
            if fileName != "":

                self.FilePath2.setText(fileName)
            return False
        elif buttonNo == "3":
            fileName, _ = QFileDialog.getOpenFileName(
                self, "Single File", QDir.rootPath(), "*.cel"
            )
            if fileName != "":

                self.FilePath3.setText(fileName)
            return False
        elif buttonNo == "4":
            fileName, _ = QFileDialog.getOpenFileName(
                self, "Single File", QDir.rootPath(), "*.cel"
            )
            if fileName != "":

                self.FilePath4.setText(fileName)
            return False
        return False
