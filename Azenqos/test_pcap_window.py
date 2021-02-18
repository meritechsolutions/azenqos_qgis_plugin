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

    azmfp = (
        "../example_logs/pcap/354569110523269 2_2_2021 11.28.6.azm"
    )

    tmp_dir = azq_utils.tmp_gen_path()
    if os.path.isdir(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.mkdir(tmp_dir)
    with zipfile.ZipFile(azmfp, "r") as zip_file:
        zip_file.extractall(tmp_dir)

    pcap_path_list = pcap_window.get_pcap_path_list(tmp_dir)
    print(pcap_path_list)

    pcap_df = pcap_window.get_pcap_df(pcap_path_list)
    print(pcap_df)



if __name__ == "__main__":
    test()
