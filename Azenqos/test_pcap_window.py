import os
import shutil
import zipfile

import azq_utils
import pcap_window


def test():

    if os.name != "nt":
        return

    azmfp = "../example_logs/pcap/354569110523269 2_2_2021 11.28.6.azm"

    tmpdir = azq_utils.tmp_gen_path()
    try:
        if os.path.exists(tmpdir) and os.path.isdir(tmpdir):
            shutil.rmtree(tmpdir)

        os.mkdir(tmpdir)
    except:
        pass
    with zipfile.ZipFile(azmfp, "r") as zip_file:
        zip_file.extractall(tmpdir)

    pcap_df = pcap_window.new_get_all_pcap_content(tmpdir)
    print(pcap_df)

    try:
        if os.path.exists(tmpdir) and os.path.isdir(tmpdir):
            shutil.rmtree(tmpdir)
    except:
        pass


if __name__ == "__main__":
    test()
