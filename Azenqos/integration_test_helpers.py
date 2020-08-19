import os
import zipfile
import azq_utils
import shutil

def unzip_azm_to_tmp_get_dbfp(azmfp):
    tmpdir = os.path.join(azq_utils.get_module_path(), "tmp_test")
    if os.path.isdir(tmpdir):
        shutil.rmtree(tmpdir)
    os.mkdir(tmpdir)
    with zipfile.ZipFile(azmfp, 'r') as zip_ref:
        zip_ref.extract("azqdata.db", tmpdir)
    dbfp = os.path.join(tmpdir, "azqdata.db")
    assert os.path.isfile(dbfp)
    return dbfp
