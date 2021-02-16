from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtSql import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi
import threading
import sys
import traceback
import os
import csv
import pandas as pd
import numpy as np
from urllib.parse import urlparse
import requests

import azq_utils
import analyzer_vars
GUI_SETTING_NAME_PREFIX = "{}/".format(os.path.basename(__file__))
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)  # exit upon ctrl-c
import time


class login_dialog(QDialog):

    progress_update_signal = pyqtSignal(int)
    status_update_signal = pyqtSignal(str)
    login_done_signal = pyqtSignal(str)
    
    def __init__(self, parent, gc):
        super(login_dialog, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.gc = gc                
        self.setupUi()
        self.ret_dict = {}
        self.valid = False

        self.server = None
        self.token = None
        self.proc_uuid = None
        self.lhl = None
        
        self.login_thread = None
        self.login_done_signal.connect(
            self.ui_thread_handler_login_completed
        )
        self.status_update_signal.connect(
            self.status_update
        )
        self.progress_update_signal.connect(
            self.progress_update
        )

        

    def setupUi(self):
        dirname = os.path.dirname(__file__)
        self.setWindowIcon(QIcon(QPixmap(os.path.join(dirname, "icon.png"))))
        self.ui = loadUi(azq_utils.get_local_fp("login_dialog.ui"), self)
        self.ui.pass_le.setEchoMode(QLineEdit.Password)
        self.ui.progressbar.setVisible(False)
        self.setWindowTitle("AZENQOS Server login")
        self.ui.server_url_le.setText(azq_utils.read_local_file("prev_login_dialog_server_url"))
        self.ui.login_le.setText(azq_utils.read_local_file("prev_login_dialog_login"))
        self.ui.lhl_le.setText(azq_utils.read_local_file("prev_login_dialog_lhl"))
        

    def get_result_dict(self):
        ret_dict = {
            "server_url": self.ui.server_url_le.text(),
            "login": self.ui.login_le.text(),
            "pass": self.ui.pass_le.text(),            
            "lhl": self.ui.lhl_le.text(),
        }
        return ret_dict

    def progress_update(self, val):
        print("progress_update: {}".format(val))
        self.ui.progressbar.setValue(val)

    def status_update(self, val):
        print("status_update: {}".format(val))
        self.ui.label_status.setText(val)

    def ui_login_thread_start(self):
        self.ui.buttonBox.setEnabled(False)
        self.progress_update(0)
        self.status_update("")
        self.ui.progressbar.setVisible(True)

    def ui_login_thread_failed(self):
        self.ui.buttonBox.setEnabled(True)
        self.progress_update(0)
        self.status_update("Login failed...")
        self.ui.progressbar.setVisible(False)
    
    def accept(self):
        print("login_dialog: accept")        
        if self.validate():
            
            if self.login_thread is None or (self.login_thread.is_alive() == False):
                self.ui_login_thread_start()
                self.login_thread = threading.Thread(target=self.login_and_dl_db_zip, args=())
                self.login_thread.start()
            else:
                QtWidgets.QMessageBox.critical(
                    None,
                    "Please wait...",
                    "Already trying to log to server...",
                    QtWidgets.QMessageBox.Ok,
                )

            
    def validate(self):
        self.ret_dict = self.get_result_dict()
        for key in self.ret_dict.keys():
            self.ret_dict[key] = str(self.ret_dict[key])
            val = self.ret_dict[key]
            if not val:        
                QtWidgets.QMessageBox.critical(
                    None,
                    "Missing data",
                    "Please complete all fields...",
                    QtWidgets.QMessageBox.Ok,
                )
                return False

        azq_utils.write_local_file(
            "prev_login_dialog_server_url", self.ret_dict["server_url"]
        )
        azq_utils.write_local_file(
            "prev_login_dialog_login", self.ret_dict["login"]
        )
        azq_utils.write_local_file(
            "prev_login_dialog_lhl", self.ret_dict["lhl"]
        )

        ###### check lhl
        lhl = self.ret_dict["lhl"].strip()
        if "," in lhl:
            lhl = lhl.split(",")
        else:
            lhl = [lhl]
        try:
            lhl = pd.Series(lhl, dtype=np.int64)
        except:
            QtWidgets.QMessageBox.critical(
                    None,
                    "Invalid log_hash list",
                    "Provided log_hash list must be numbers and commas only",
                    QtWidgets.QMessageBox.Ok,
                )
            return False

        try:
            assert urlparse(self.ret_dict["server_url"]).netloc
        except:
            QtWidgets.QMessageBox.critical(
                None,
                "Invalid server url",
                "Provided a valid server URL. Example: https://test0.azenqos.com",
                QtWidgets.QMessageBox.Ok,
            )
            return False

        
        self.valid = True
        return True

    
    def login_and_dl_db_zip(self):        
        try:
            # the emit() below would fail/raise if dialog was closed so no need to check dialog closed flag etc
            self.progress_update_signal.emit(0)
            self.status_update_signal.emit("Connecting to server...")

            self.lhl = self.ret_dict["lhl"]
            self.server = self.ret_dict["server_url"]
            self.token = login(self.ret_dict)            
            self.status_update_signal.emit("Login success...")
            self.progress_update_signal.emit(10)
            
            self.proc_uuid = api_dump_db_get_proc_uuid(self.server, self.token, self.lhl)
            self.status_update_signal.emit("server preparing data for specified log_hashes...")
            self.progress_update_signal.emit(15)

            resp_dict = None

            loop_count = 0
            # loop check task status until success
            while True:
                loop_count += 1
                time.sleep(3)
                resp_dict = api_get_process(self.server, self.token, self.proc_uuid)
                print('resp_dict["returncode"]:', resp_dict["returncode"])
                if resp_dict["returncode"] is not None:        
                    break
                self.status_update_signal.emit("server process running - loop_count: {}".format(loop_count))

            self.status_update_signal.emit("server dump data process completed...")
            print('server process complete - resp_dict:', resp_dict)
            self.progress_update_signal.emit(50)
            cret = api_delete_process(self.server, self.token, self.proc_uuid)
            self.proc_uuid = None # as process was already cleanedup...
            print('server process cleanup...')
            self.progress_update_signal.emit(55)

            if resp_dict["returncode"] != 0:
                raise Exception('Server process failed with code: {}, stdout_log_tail: {}'.format(resp_dict["returncode"], resp_dict["stdout_log_tail"]))

            # TODO - check out dump dict string format - if cant find then raise

            self.progress_update_signal.emit(100)
            self.login_done_signal.emit("")
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print("WARNING: login_and_dl_db_zip exception: {}", exstr)
            try:
                self.login_done_signal.emit(exstr)
            except:
                pass
            if self.proc_uuid:
                print("login_and_dl_db_zip: cleanup server proc_uuid as we had exception above - START")
                try:
                    cret = api_delete_process(self.server, self.token, self.proc_uuid)
                    print("login_and_dl_db_zip: cleanup server proc_uuid as we had exception above - DONE ret: {}".format(cret))
                except:
                    type_, value_, traceback_ = sys.exc_info()
                    exstr = str(traceback.format_exception(type_, value_, traceback_))
                    print("WARNING: api_delte_process failed exception: {}", exstr)

            

    def ui_thread_handler_login_completed(self, error):
        if error:
            QtWidgets.QMessageBox.critical(
                None,
                "Operation failed...",
                error,
                QtWidgets.QMessageBox.Ok,
            )
            self.ui_login_thread_failed()
        else:            
            self.done(QtWidgets.QDialog.Accepted)


def login(args_dict):
    token = None
    host = urlparse(args_dict["server_url"]).netloc
    print("login host: %s" % host)
    assert args_dict["server_url"]
    assert args_dict["login"]
    assert args_dict["pass"]
    token = azq_utils.login_get_token(args_dict["login"], args_dict["pass"], host)
    return token


def api_create_process(server, token, lhl, azq_report_gen_expression):
    host = urlparse(server).netloc
    resp = requests.post(
        "https://{}/api_livegen/livegen_process".format(host),
        headers={
            "Authorization": "Bearer {}".format(token),
        },
        json={
            "process_type": "azq_report_gen",
            "pg_host": "azq_pg",
            "pg_port": "5432",
            "sqlite_db_file": "PG_AZM_DB_MERGE",
            "pg_log_hash_list": lhl,
            "GET_PYPROCESS_OUTPUT": "PY_EVAL {}".format(azq_report_gen_expression),
            "_post_back_tar_file_list": []
        },
        verify=False,
    )    
    #print("resp.status_code", resp.status_code)
    #print("resp.text:", resp.text)
    if resp.status_code != 200:
        raise Exception(
            "Got failed status_code: {} resp.text: {}".format(
                resp.status_code,
                resp.text,
            )
        )
    resp_dict = resp.json()
    return resp_dict


def api_get_process(server, token, proc_uuid):
    host = urlparse(server).netloc
    resp = requests.get(
        "https://{}/api_livegen/livegen_process/{}".format(host, proc_uuid),
        headers={
            "Authorization": "Bearer {}".format(token),
        },
        verify=False,
    )    
    #print("resp.status_code", resp.status_code)
    #print("resp.text:", resp.text)
    if resp.status_code != 200:
        raise Exception(
            "Got failed status_code: {} resp.text: {}".format(
                resp.status_code,
                resp.text,
            )
        )
    resp_dict = resp.json()
    return resp_dict


def api_resp_get_stdout(server, token, resp_dict):
    host = urlparse(server).netloc
    resp = requests.get(
        "https://{}/{}".format(host, resp_dict["stdout_log_url"]),
        headers={
            "Authorization": "Bearer {}".format(token),
        },
        verify=False,
    )    
    #print("resp.status_code", resp.status_code)
    #print("resp.text:", resp.text)
    if resp.status_code != 200:
        raise Exception(
            "Got failed status_code: {} resp.text: {}".format(
                resp.status_code,
                resp.text,
            )
        )
    return resp.text


def api_delete_process(server, token, proc_uuid):
    host = urlparse(server).netloc
    resp = requests.delete(
        "https://{}/api_livegen/livegen_process/{}".format(host, proc_uuid),
        headers={
            "Authorization": "Bearer {}".format(token),
        },
        verify=False,
    )    
    #print("resp.status_code", resp.status_code)
    #print("resp.text:", resp.text)
    if resp.status_code != 200:
        raise Exception(
            "Got failed status_code: {} resp.text: {}".format(
                resp.status_code,
                resp.text,
            )
        )
    resp_dict = resp.json()
    return resp_dict


def api_dump_db_get_proc_uuid(server, token, lhl):
    proc_uuid = api_create_process(server, token, lhl, "dump_db.process_cell(dbcon, '')")["proc_uuid"]
    print("task_uuid:", proc_uuid)
    assert proc_uuid
    return proc_uuid


def api_wait_until_process_completed(server, token, proc_uuid):
    resp_dict = None    
    # loop check task status until success
    while True:
        time.sleep(3)
        resp_dict = api_get_process(server, token, proc_uuid)
        print('resp_dict["returncode"]:', resp_dict["returncode"])
        if resp_dict["returncode"] is not None:        
            break
    return resp_dict
