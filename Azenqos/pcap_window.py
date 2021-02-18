from PyQt5.QtSql import QSqlQuery, QSqlDatabase
import pandas as pd
import numpy as np
import params_disp_df
import os
import azq_utils
import shutil
import zipfile
from os import path
import subprocess
import tshark_util
import azq_utils


def get_pcap_path_list(azm_path):
    pcap_path_list = []
    azm_path = azm_path.replace("\\", os.path.sep)
    azm_path = azm_path.replace("/", os.path.sep)
    if os.name != 'nt':
        extensions=('.csv')
    else:
        extensions = ('.csv', '.pcap')
    for root, dirs, files in os.walk(azm_path):
        for name in files:
            pcap_file = os.path.join(root, name)
            if pcap_file.endswith(extensions):
                pcap_path_list.append(pcap_file)

    pcap_path_list = [os.path.splitext(x)[0] for x in pcap_path_list]
    pcap_path_list = list(dict.fromkeys(pcap_path_list))
    return pcap_path_list


def get_pcap_df(pcap_path_list):
    pcap_df_list = []
    for pcap_path in pcap_path_list:
        pcap_file_name = os.path.basename(pcap_path)
        csv_path = pcap_path+".csv"
        pcap_path = pcap_path+".pcap"
        if path.isfile(csv_path):
            pass
        else:
            env = tshark_util.prepare_env_and_libs()
            tsharkPath = os.path.join(
                azq_utils.get_module_path(),
                os.path.join(
                    "wireshark_" + os.name,
                    "tshark" + ("" if os.name == "posix" else ".exe"),
                ),
            )
            cmd = (
                tsharkPath
                + ' -r '
                + ' "' + pcap_path + '" '
                + '-t ud -n -p -2 -T fields -E separator=, -E quote=d -E header=y -e _ws.col.No. -e _ws.col.Time -e _ws.col.Source -e _ws.col.Destination -e _ws.col.Protocol -e tcp.srcport -e tcp.dstport -e udp.srcport -e udp.dstport -e _ws.col.Length -e _ws.col.Info > '
                + ' "' + csv_path + '" '
            )
            cmdret = subprocess.call(cmd, shell=True, env=env)

        f = open(csv_path)
        if "Running as user" not in f.readline():
            f.seek(0)
        pcap_df = pd.read_csv(f)
        f.close()
        pcap_df["file_name"] = pcap_file_name
        pcap_df_list.append(pcap_df)

    pcap_df_all = pd.concat(pcap_df_list)
    pcap_df_all = pcap_df_all.drop_duplicates(keep="first").rename(columns={'_ws.col.Time': 'time'}).sort_values(by="time").drop(columns=['_ws.col.No.']).reset_index(drop=True)
    tdelta = pd.Timedelta(np.timedelta64(25200000, "ms"))
    pcap_df_all["time"] = pd.to_datetime(pcap_df_all["time"]) + tdelta
    return pcap_df_all

def get_all_pcap_content(azm_path):
    pcap_path_list = get_pcap_path_list(azm_path)
    return get_pcap_df(pcap_path_list)

pcap_path_list =None
def new_get_all_pcap_content(azm_path):
    global pcap_path_list
    pcap_path_list = get_pcap_path_list(azm_path)
    return tmp
    
def tmp(time,dbcon):
    global pcap_path_list
    return get_pcap_df(pcap_path_list)




# def get_pcap_path_list_df(azm_path):
#     pcap_path_list = get_pcap_path_list(azm_path)
#     # print(gc.logPath)
#     return pd.DataFrame(pcap_path_list, columns=['Path'])


# def get_pcap_df(pcap_path):
#     csv_path = pcap_path+".csv"
#     pcap_path = pcap_path+".pcap"
#     if path.isfile(csv_path):
#         pass
#     else:
#         env = tshark_util.prepare_env_and_libs()
#         tsharkPath = os.path.join(
#             gc.CURRENT_PATH,
#             os.path.join(
#                 "wireshark_" + os.name,
#                 "tshark" + ("" if os.name == "posix" else ".exe"),
#             ),
#         )
#         cmd = (
#             tsharkPath
#             + ' -r '
#             + ' "' + pcap_path + '" '
#             + '-t ud -n -p -2 -T fields -E separator=, -E quote=d -E header=y -e _ws.col.No. -e _ws.col.Time -e _ws.col.Source -e _ws.col.Destination -e _ws.col.Protocol -e tcp.srcport -e tcp.dstport -e udp.srcport -e udp.dstport -e _ws.col.Length -e _ws.col.Info > '
#             + ' "' + csv_path + '" '
#         )
#         cmdret = subprocess.call(cmd, shell=True, env=env)

#     f = open(csv_path)
#     if "Running as user" not in f.readline():
#         f.seek(0)
#     pcap_df = pd.read_csv(f)
#     f.close()
#     return pcap_df

