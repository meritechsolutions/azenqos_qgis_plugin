import zipfile
import os
import shutil
import azq_utils
import sqlite3
import pandas as pd
import pcap_window
import integration_test_helpers
import numpy as np


def test():

    if os.name != 'nt':
        return

    azmfp = (
        "../example_logs/pcap/354569110523269 2_2_2021 11.28.6.azm"
    )

    tmpdir = azq_utils.tmp_gen_path()
    if os.path.isdir(tmpdir):
        shutil.rmtree(tmpdir)
    os.mkdir(tmpdir)
    with zipfile.ZipFile(azmfp, "r") as zip_file:
        zip_file.extractall(tmpdir)

    pcap_path_list = pcap_window.get_pcap_path_list(tmpdir)
    print(pcap_path_list)

    # pcap_path_list_df = pcap_window.get_pcap_path_list_df(tmpdir)
    # print(pcap_path_list_df)

    # pcap_path = pcap_path_list[1]
    pcap_df = pcap_window.get_pcap_df(pcap_path_list)
    print(pcap_df)
    
    if os.path.isdir(tmpdir):
        shutil.rmtree(tmpdir)




if __name__ == "__main__":
    test()
