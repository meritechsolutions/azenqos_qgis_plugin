import traceback, sys
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *  # QAbstractTableModel, QVariant, Qt, pyqtSignal, QThread
from PyQt5.QtSql import *  # QSqlQuery, QSqlDatabase
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QColor
from .worker import WorkerSignals
import subprocess
import tempfile
import os
import global_config as gc
import uuid
import re
import tshark_util


class TsharkDecodeWorker(QRunnable):
    ret = None

    def __init__(self, name, side, protocol, detail):
        assert name is not None
        assert side is not None
        assert protocol is not None
        assert detail is not None
        super(TsharkDecodeWorker, self).__init__()
        self.name = name
        self.side = side
        self.protocol = protocol
        self.detail = detail
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        result = ""
        try:
            env = tshark_util.prepare_env_and_libs()
            tsharkPath = os.path.join(
                gc.CURRENT_PATH,
                os.path.join(
                    "wireshark_" + os.name,
                    "tshark" + ("" if os.name == "posix" else ".exe"),
                ),
            )
            text2pcapPath = os.path.join(
                gc.CURRENT_PATH,
                os.path.join(
                    "wireshark_" + os.name,
                    "text2pcap" + ("" if os.name == "posix" else ".exe"),
                ),
            )
            print("tsharkPath", tsharkPath)
            print("text2pcapPath", text2pcapPath)
            hexStr = ""
            if self.side == "recv":
                hexStr = "i "
            else:
                hexStr = "o "
            hexStr = hexStr + "000000 "
            msg = "msg_raw_hex: "
            hexStr = hexStr + self.detail[self.detail.rindex(msg) + len(msg) :]
            print("text2pcap input content:", hexStr)

            tempName = uuid.uuid4().hex
            tempHexPath = os.path.join(gc.FILE_PATH, tempName + ".txt")
            tempPcapPath = os.path.join(gc.FILE_PATH, tempName + ".pcap")
            print("tempHexPath", tempHexPath)
            print("tempPcapPath", tempPcapPath)

            tempHexFile = open(tempHexPath, "w")
            tempHexFile.write(hexStr)
            tempHexFile.close()

            cmd = text2pcapPath + ' -l 161 "{}" "{}"'.format(tempHexPath, tempPcapPath)
            print("text2pcap cmd:", cmd)
            cmdret = subprocess.call(cmd, shell=True, env=env)
            print("text2pcap ret:", cmdret)

            if cmdret != 0:
                print("text2pcap failed - abort")
            else:
                channelType = None
                match = re.search(r"\((.*)\)", self.name)
                if match is not None:
                    channelType = match.group(1)

                print("channelType", channelType)

                dissector = protocolToDissector(self.protocol, channelType)
                cmd = (
                    tsharkPath
                    + ' -o "uat:user_dlts:\\"User 14 (DLT=161)\\",\\"{}\\",\\"0\\",\\"\\",\\"0\\",\\"\\"" -r {} -V'.format(
                        dissector, tempPcapPath
                    )
                )
                print("tshark cmd:", cmd)
                decodeResult = subprocess.check_output(cmd, shell=True, env=env)
                decodeResult = decodeResult.decode("utf-8")
                # print("decodeResult", decodeResult)
                result = decodeResult
                if "DLT: 161," in result:
                    result = result[result.index("DLT: 161,") :]
                    result = result[result.index("\n") :]
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print("WARNING: Worker - exception: {}".format(exstr))
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


def protocolToDissector(protocol, channelType):
    if protocol in ["RR", "MM", "CC", "GMM", "SM"]:
        return "gsm_a_dtap"
    elif protocol in ["EMM", "ESM"]:
        return "nas-eps_plain"
    elif protocol in ["RRC"]:
        return "rrc." + str(getWcdmaSubdissector(channelType))
    elif protocol in ["ERRC"]:
        return "lte_rrc." + str(getLetSubdissector(channelType))
    return None


def getWcdmaSubdissector(channelType):
    if channelType in ["UL-CCCH"]:
        return "ul.ccch"
    elif channelType in ["UL-DCCH"]:
        return "ul.dcch"
    elif channelType in ["DL-CCCH"]:
        return "dl.ccch"
    elif channelType in ["DL-DCCH"]:
        return "dl.dcch"
    elif channelType in ["BCCH-BCH"]:
        return "bcch.bch"
    elif channelType in ["BCCH-FACH"]:
        return "bcch.fach"
    elif channelType in ["PCCH"]:
        return "pcch"
    elif channelType in ["MCCH"]:
        return "mcch"
    elif channelType in ["MSCH"]:
        return "msch"
    elif channelType in ["SysInfoType19"]:
        return "si.sib19"
    elif channelType in ["SysInfoType11bis"]:
        return "si.sib11bis"
    elif channelType in ["SysInfoType3", "SysInfoType5bis", "SysInfoType11"]:
        return "bcch.bch"
    return None


def getLetSubdissector(channelType):
    if channelType in ["BCCH-DL-SCH"]:
        return "bcch_dl_sch"
    elif channelType in ["PCCH"]:
        return "pcch"
    elif channelType in ["DL-CCCH"]:
        return "dl_ccch"
    elif channelType in ["DL-DCCH", "DL_DCCH"]:
        return "dl_dcch"
    elif channelType in ["UL-CCCH"]:
        return "ul_ccch"
    elif channelType in ["UL-DCCH"]:
        return "ul_dcch"
    elif channelType in ["V15_PDU_NUMBER_BCCH_DL_SCH_NB"]:
        return "bcch_dl_sch.nb"
    elif channelType in ["DL-CCCH-Message-NB"]:
        return "dl_ccch.nb"
    elif channelType in ["DL-DCCH-Message-NB"]:
        return "dl_dcch.nb"
    elif channelType in ["UL-CCCH-Message-NB"]:
        return "ul_ccch.nb"
    elif channelType in ["UL-DCCH-Message-NB"]:
        return "ul_dcch.nb"
    return None
