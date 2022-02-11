import os
import sqlite3
import subprocess
from os import path
import contextlib

import numpy as np
import pandas as pd

import azq_utils
import tshark_util


def get_pcap_path_list(azm_path, log_list):
    pcap_path_list = []
    azm_path = azm_path.replace("\\", os.path.sep)
    azm_path = azm_path.replace("/", os.path.sep)
    for log_hash in log_list:
        resource_path = os.path.join(azm_path, str(log_hash))
        if os.name != "nt":
            extensions = ".csv"
        else:
            extensions = (".csv", ".pcap")
        for root, dirs, files in os.walk(resource_path):
            for name in files:
                pcap_file = os.path.join(root, name)
                if pcap_file.endswith(extensions):
                    pcap_path_list.append(pcap_file)

    pcap_path_list = [os.path.splitext(x)[0] for x in pcap_path_list]
    pcap_path_list = list(dict.fromkeys(pcap_path_list))
    return pcap_path_list


def get_pcap_df(pcap_path_list, log_list):
    global time_offset
    pcap_df_list = []
    for pcap_path in pcap_path_list:
        pcap_file_name = os.path.basename(pcap_path)
        csv_path = pcap_path + ".csv"
        pcap_path = pcap_path + ".pcap"
        for log_hash in log_list:
            if str(log_hash) in csv_path or str(log_hash) in pcap_path:
                pcap_log = log_hash
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
                + " -r "
                + ' "'
                + pcap_path
                + '" '
                + "-t ud -n -p -2 -T fields -E separator=, -E quote=d -E header=y -e _ws.col.No. -e _ws.col.Time -e _ws.col.Source -e _ws.col.Destination -e _ws.col.Protocol -e tcp.srcport -e tcp.dstport -e udp.srcport -e udp.dstport -e _ws.col.Length -e _ws.col.Info > "
                + ' "'
                + csv_path
                + '" '
            )
            subprocess.call(cmd, shell=True, env=env)

        f = open(csv_path)
        if "Running as user" not in f.readline():
            f.seek(0)
        pcap_df = pd.read_csv(f)
        f.close()
        pcap_df["file_name"] = pcap_file_name
        if "_ws.col.Time" not in pcap_df.columns:
            return
        pcap_df["log_hash"] = pcap_log
        pcap_df_list.append(pcap_df)
    if len(pcap_df_list) == 0:
        return
    pcap_df_all = pd.concat(pcap_df_list)
    pcap_df_all = (
        pcap_df_all.drop_duplicates(keep="first")
        .rename(
            columns={
                "_ws.col.Time": "time",
                "_ws.col.Source": "source",
                "_ws.col.Destination": "destination",
                "_ws.col.Protocol": "protocol",
                "_ws.col.Length": "packet_size",
                "_ws.col.Info": "info",
            }
        )
        .sort_values(by="time")
        .drop(columns=["_ws.col.No."])
        .reset_index(drop=True)
    )
    tdelta = pd.Timedelta(np.timedelta64(time_offset, "ms"))
    pcap_df_all["time"] = pd.to_datetime(pcap_df_all["time"]) + tdelta
    first_column = pcap_df_all.pop("log_hash")
    pcap_df_all.insert(0, "log_hash", first_column)
    return pcap_df_all


def get_all_pcap_content(azm_path):
    pcap_path_list = get_pcap_path_list(azm_path)
    return get_pcap_df(pcap_path_list)


pcap_path_list = None
log_list = None
time_offset = None


def new_get_all_pcap_content(azm_path, gc, selected_ue):
    global pcap_path_list
    global log_list
    global time_offset
    db_path = os.path.join(azm_path, "azqdata.db")
    with contextlib.closing(sqlite3.connect(db_path)) as dbcon:
        time_offset = pd.read_sql(
            "select log_timezone_offset from logs limit 1", dbcon
        ).iloc[0, 0]
        print(time_offset)
        print(log_list)
    log_list = gc.log_list
    if selected_ue is not None: 
        log_list = gc.device_configs[selected_ue]["log_list"]

    pcap_path_list = get_pcap_path_list(azm_path, log_list)

    return tmp()


def tmp():
    global pcap_path_list
    global log_list
    return get_pcap_df(pcap_path_list, log_list)


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
