import os
import sqlite3
import zipfile

import analyzer_vars
import azq_utils
import login_dialog
import preprocess_azm


def unzip_azm_to_tmp_get_dbfp(azmfp):
    tmpdir = azq_utils.tmp_gen_path()
    with zipfile.ZipFile(azmfp, "r") as zip_ref:
        zip_ref.extract("azqdata.db", tmpdir)
    dbfp = os.path.join(tmpdir, "azqdata.db")
    assert os.path.isfile(dbfp)
    return dbfp

def get_dbcon(dbfp):
    dbcon = sqlite3.connect(dbfp)
    preprocess_azm.update_default_element_csv_for_dbcon_azm_ver(dbcon)
    return dbcon

def get_global_vars(login=True):
    gv = analyzer_vars.analyzer_vars()
    if login:
        dlg = login_dialog.login_dialog(None, gv)
        dlg.server = "https://test0.azenqos.com"
        if "TEST_SERVER" in os.environ:
            dlg.server = os.environ["TEST_SERVER"]
        dlg.user = "trial_admin"
        if "TEST_USER" in os.environ:
            dlg.user = os.environ["TEST_USER"]
        dlg.passwd = "3.14isnotpina"
        if "TEST_PASS" in os.environ:
            dlg.passwd = os.environ["TEST_PASS"]
        dlg.login_get_token_only()
        gv.login_dialog = dlg
    return gv