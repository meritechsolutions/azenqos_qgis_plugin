import os
import zipfile
import sqlite3
import azq_utils
import preprocess_azm
import analyzer_vars
import login_dialog
import azq_server_api


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
        dlg.user = "trial_admin"
        dlg.passwd = "3.14isnotpina"
        dlg.login_get_token_only()
        gv.login_dialog = dlg
    return gv