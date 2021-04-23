import os
import zipfile

import azq_utils


def unzip_azm_to_tmp_get_dbfp(azmfp):
    tmpdir = azq_utils.tmp_gen_path()
    with zipfile.ZipFile(azmfp, "r") as zip_ref:
        zip_ref.extract("azqdata.db", tmpdir)
    dbfp = os.path.join(tmpdir, "azqdata.db")
    assert os.path.isfile(dbfp)
    return dbfp
