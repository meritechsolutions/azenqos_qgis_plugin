import contextlib
import datetime
import hashlib
import os
import random
import shutil
import sqlite3
import subprocess
import sys
import threading
import time
import traceback
import uuid
import json 
from pathlib import Path
import base64
import re

import pandas as pd
import requests
from PyQt5 import QtWidgets, QtCore

import dprint
try:
    from PIL import ImageGrab
except:
    pass


TMP_FOLDER_NAME = "tmp_gen"
CONTAINER_MODE_TMP_GEN_PATH = "/host_shared_dir/tmp_gen"
AZQ_WORKSTATION_CONTAINER_NAME_ENV_KEY = "AZQ_WORKSTATION_CONTAINER_NAME"
CUSTOM_TAGS_ENV_KEY = "CUSTOM_TAGS"

def is_container_mode():
    return AZQ_WORKSTATION_CONTAINER_NAME_ENV_KEY in os.environ

def get_container_name():
    assert is_container_mode()
    return os.environ[AZQ_WORKSTATION_CONTAINER_NAME_ENV_KEY]

def get_custom_tags():
    custom_tags = []
    print("environ: ", os.environ)
    if CUSTOM_TAGS_ENV_KEY in os.environ:
        custom_tags = os.environ[CUSTOM_TAGS_ENV_KEY].split(",")
        print("custom_tags: ", custom_tags)
    return custom_tags



def debug(s):
    dprint.dprint(s)


def get_module_path():
    return os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


def get_module_fp(fn):
    return os.path.join(get_module_path(), fn)


def get_settings_dp():
    settings_dname = "Azenqos_settings"
    dp = os.path.join(get_module_parent_path(), settings_dname)
    if is_container_mode():
        dp = tmp_gen_fp(settings_dname)
    if not os.path.isdir(dp):
        os.makedirs(dp)
    assert os.path.isdir(dp)
    return dp


def get_settings_fp(fn):
    dp = get_settings_dp()
    fp = os.path.join(dp, fn)
    return fp


def write_settings_file(fname, contents, auto_encode=True, encrypt=False):
    try:
        if auto_encode and isinstance(contents, str):
            contents = contents.encode()  # conv to bytes for write
        if encrypt:
            contents = base64.b64encode(contents)
        with open(get_settings_fp(fname), "wb") as f:
            f.write(contents)
    except:
        type_, value_, traceback_ = sys.exc_info()
        exstr = str(traceback.format_exception(type_, value_, traceback_))
        print("WARNING: write_local_file - exception: {}".format(exstr))


def read_settings_file(fname, auto_decode=True, decrypt=False):
    try:
        with open(get_settings_fp(fname), "rb") as f:
            ret = f.read()
            if decrypt:
                ret = base64.b64decode(ret)
            if auto_decode:
                ret = ret.decode()
            return ret
    except:
        type_, value_, traceback_ = sys.exc_info()
        #exstr = str(traceback.format_exception(type_, value_, traceback_))
        #print("WARNING: read_local_file - exception: {}".format(exstr))
    return None

def df_log_hash_time_resample(fulldf, resample_param, sort_by_time_only=False, add_copy_of_last_row_time_offset_millis=None, use_last=False):
    df = resample_per_log_hash_time(fulldf, resample_param, use_last=use_last)
    if sort_by_time_only:
        df = df.sort_values("time")
    if len(df) and add_copy_of_last_row_time_offset_millis:
        print("add_copy_of_last_row_time_offset_millis")
        last_row_copy = df.tail(1).copy()
        print("last_row_copy ori:", last_row_copy)
        last_row_copy.index += pd.Timedelta('{}ms'.format(add_copy_of_last_row_time_offset_millis))
        print("last_row_copy after add offset ts:", last_row_copy)
        df = pd.concat([df, last_row_copy])
    return df

def get_default_color_for_index(i):
    def r():
        return random.randint(0, 255)

    color_list = [
        "CD5C5C",
        "556B2F",
        "9400D3",
        "00FA9A",
        "000080",
        "C71585",
        "FF8C00",
        "20B2AA",
        "DAA520",
        "00FFFF",
        "228B22",
        "DA70D6",
        "2F4F4F",
        "8B4513",
        "BDB76B",
        "FFE4C4",
        "DB7093",
        "8FBC8F",
        "8B7D6B",
        "B22222",
        "FA8072",
        "00FF00",
        "3CB371",
        "00BFFF",
        "32CD32",
        "87CEEB",
        "5F9EA0",
        "4682B4",
        "B0C4DE",
        "E6E6FA",
        "F4A460",
        "BA55D3",
        "6A5ACD",
        "00FF7F",
        "EED5B7",
        "7FFFD4",
        "98FB98",
        "7CFC00",
        "FF69B4",
        "BC8F8F",
        "1E90FF",
        "6B8E23",
        "F5AAAA",
        "006400",
        "483D8B",
        "2E8B57",
        "CDB79E",
        "FFE4E1",
        "708090",
        "0000CD",
        "FF4500",
        "6495ED",
        "4169E1",
        "FFFF00",
        "E30741",
        "C896A1",
        "8575DB",
        "D16155",
        "154B61",
        "5556D9",
        "89220D",
        "392BF0",
        "6D1DE7",
        "30C8B3",
        "918E86",
        "80FB20",
        "86AB19",
        "B86D55",
        "485111",
        "4A2D9B",
        "31B3DE",
        "354D06",
        "7CEE93",
        "3DC9ED",
        "A38D01",
        "833460",
        "3A6887",
        "EF3CEC",
        "F1ACA9",
        "A4C32C",
        "4B08F6",
        "931FB9",
        "699957",
        "659023",
        "AC86FA",
        "2452D5",
        "968A64",
        "4CDD62",
        "4D8DEA",
        "187AE7",
        "51BB49",
        "0DF985",
        "EC2BA9",
        "EF66D4",
        "0ED88B",
        "FEDB91",
        "4AF437",
        "A14CDE",
        "6BDC2A",
        "139EB2",
        "AA0769",
        "8A38F7",
        "099466",
        "3C2094",
        "BA7592",
        "73D7B4",
        "04F4CE",
        "BC751E",
        "B4AE53",
        "21EA68",
        "DDCB57",
        "F6CEA9",
        "C664B7",
        "27CD52",
        "18402B",
        "8F85BE",
        "DA498E",
        "2548AF",
        "0D6DAC",
        "FC44C6",
        "F568A1",
        "67CA15",
        "93AEC5",
        "ED25AD",
        "1A95E5",
        "CEA365",
        "5CC17D",
        "6111FE",
        "6DB926",
        "641F9F",
        "56E0A4",
        "5F1109",
        "F7A18A",
        "0F7C8A",
        "2EE3E8",
        "33F139",
        "6987B9",
        "0A0BC8",
        "5C7D8F",
        "7AE6EC",
        "E10E33",
        "79DF08",
        "8128DF",
        "13B804",
        "88E6ED",
        "3DF3B2",
        "73B42C",
        "CBEF4C",
        "E6FAFF",
        "E77DE6",
        "A24A5F",
        "CD2815",
        "5E14E6",
        "0DCF7B",
        "F53731",
        "EE4289",
        "1474D8",
        "A27B75",
        "273E7A",
        "970CE3",
        "ED12F9",
        "C1E35B",
        "CFE4B5",
        "ADDDC4",
        "75C82B",
        "B18D47",
        "71854E",
        "11E059",
        "5F72D3",
        "7593DC",
        "F9E763",
        "EE4749",
        "55A350",
        "DB04ED",
        "8622AF",
        "F98E0F",
        "1FD561",
        "FB79ED",
        "9B9907",
        "79D9C8",
        "9C12A1",
        "1C0F26",
        "1129A1",
        "64C0ED",
        "7575F4",
        "D81FAC",
        "0C81CA",
        "8DCA77",
        "BEC8EA",
        "660EB0",
        "398493",
        "0908BC",
        "34A0F2",
        "7B033E",
        "EA4F90",
        "FCA803",
        "B0DC98",
        "9CC4DB",
        "64668A",
        "56596E",
        "95B3DB",
        "69C365",
        "CF294F",
        "4A4B1C",
        "663BF9",
        "A9F5DC",
        "136D7C",
        "24C4D0",
        "32A7DB",
        "4327F1",
        "19B0F8",
        "D0B3D3",
        "0F7C45",
        "C87704",
        "3485C8",
        "7D12E1",
        "AB16FF",
        "9FF1B3",
        "77CEFC",
        "321C7D",
        "4FB61A",
        "7B5814",
        "8B47DF",
        "A47626",
        "369421",
        "260EC1",
        "83CECE",
        "3597C6",
        "77BEED",
        "514E66",
        "F8DF69",
        "1FDDDA",
        "C1F58B",
        "CF27E1",
        "532918",
        "011D07",
        "7174F4",
        "FB6E1E",
        "ADED4C",
        "EAF131",
        "942A13",
        "284AD4",
        "ECF5B0",
        "35E233",
        "E1DE21",
        "FC5277",
        "5AFA4D",
        "E39E84",
        "FBADDD",
        "1CEEA1",
        "09D6B5",
        "D1FDB3",
        "A9637E",
        "879247",
        "053F4E",
        "058EB4",
        "485360",
        "609C41",
        "BD850D",
        "C03007",
        "E1C6F8",
        "B41077",
        "0E8AAC",
        "C6A4BA",
        "27B58B",
        "D7CAEC",
        "290497",
        "BA5440",
        "116B52",
        "68A1D2",
        "CB9858",
        "4814CB",
        "C852DA",
        "2EB991",
        "BF9517",
        "8D2258",
        "AA0CED",
        "7B6CD3",
        "70129B",
        "35BDBC",
        "43A76F",
        "0091C8",
        "E34501",
        "871AAB",
        "6D12BC",
        "F00976",
        "986393",
        "C870D8",
        "16F319",
        "E87FA3",
        "C93C3B",
        "2C39FC",
        "CC44C2",
        "CE8C1A",
        "502D0C",
        "0C649A",
        "FB6256",
        "F2246E",
        "62CFFE",
        "95EB2E",
        "83BF84",
        "9700A6",
        "6A89EF",
        "852541",
        "3E62A9",
        "13DC25",
        "1CC2C7",
        "8311DF",
        "0543A9",
        "4E7B02",
        "4151D7",
        "6F4310",
        "AA4BC1",
        "BD7002",
        "9401F0",
        "342850",
        "0BF4E1",
        "59CA48",
        "C05305",
        "59A6BA",
        "7EE974",
        "9709CF",
        "A287CD",
        "F9D5CD",
        "B27593",
        "001F99",
        "3213BE",
        "260BDD",
        "8D6523",
        "3D6B3F",
        "E3F029",
        "95CB98",
        "9BE97C",
        "7F9D5B",
        "19974C",
        "62F631",
        "FD7B80",
        "31C2B3",
        "E33809",
        "322D97",
        "90A87D",
        "A6A223",
        "264F80",
        "3736F4",
        "036300",
        "A91428",
        "2DEDF1",
        "027420",
        "5578C7",
        "CCA3FB",
        "3A55E8",
        "D15CE5",
        "DE853A",
        "58FD1C",
        "4E9E18",
        "A53FA2",
        "773C31",
        "21FA63",
        "5BB59C",
        "1DAACC",
        "36165C",
        "8C4C98",
        "DC9D60",
        "0CBB15",
        "8222DE",
        "F0407A",
        "DF61B0",
        "99C363",
        "37FF20",
        "4B36E0",
        "5D0AE8",
        "4B7BD3",
        "B6D8A4",
        "BDBBCE",
        "C09077",
        "0C4163",
        "9AE16B",
        "5122AC",
        "659116",
        "0E69EE",
        "1EA6F1",
        "99C7A2",
        "30462E",
        "294CB5",
        "2B3951",
        "7602C0",
        "3690D4",
        "214777",
        "5A096C",
        "F8731C",
        "5825AF",
        "6E5FE3",
        "40598C",
        "0D617D",
        "D755A6",
        "1FF45A",
        "4B89B6",
        "D0729F",
        "FAD6B4",
        "39B8E6",
        "F06F4C",
        "987123",
        "8F3F2D",
        "F17C83",
        "1BDC4B",
        "24B930",
        "5D8DEA",
        "07A46C",
        "26EA26",
        "D32B06",
        "63A2CE",
        "21BBFA",
        "6F1148",
        "D6EC01",
        "3E4595",
        "B08625",
        "457F16",
        "976A8B",
        "261132",
        "2617BA",
        "C7A5DD",
        "B13214",
        "9ACF55",
        "A8CC9F",
        "FC5031",
        "A08565",
        "317748",
        "CD38D8",
        "D8194A",
        "947E4A",
        "0FB851",
        "D93407",
        "DD4052",
        "93AADF",
        "563C58",
        "7573ED",
        "5B6807",
        "FD44EA",
        "67E12B",
        "072448",
        "CCE4FC",
        "2479C8",
        "0C6504",
        "07CE8E",
        "A86CDA",
        "4962E5",
        "E0A696",
        "FA2503",
        "A0A6F2",
        "49BB58",
        "5A1CD0",
        "2C0C2A",
        "225575",
        "816285",
        "5DE084",
        "8EFAAC",
        "AC8B8B",
        "5BDA05",
        "0976CF",
        "C2CB24",
        "FB3E5D",
        "B094C2",
        "13328E",
        "3D8A44",
        "9066C9",
        "BC4EAA",
        "B6B5A7",
        "7A9487",
        "3B4B59",
        "FFA656",
        "F024FD",
        "EA490E",
        "178BC0",
        "2FC7A1",
        "190BF6",
        "2F7536",
        "2216B1",
        "5D9E85",
        "FB4B2E",
        "C47DF7",
        "327B7B",
        "1AD319",
        "566E4F",
        "33A8FD",
        "6B1E91",
        "6C3D8A",
        "8956D6",
        "F2C611",
        "5550D4",
        "E30029",
        "18656E",
        "0F8555",
        "B488AA",
        "90FE0C",
        "3F03F2",
        "C0B361",
        "1609C5",
        "F7A805",
        "296286",
        "EB6FF5",
        "2B6DEC",
        "E03F9F",
        "497F17",
        "541B69",
        "255844",
        "D7044E",
        "13F429",
        "472C64",
        "3B946F",
        "E8531A",
        "8F1835",
        "74868A",
        "FD1198",
        "6D4F1B",
        "F04445",
        "EC4F47",
        "5BCE25",
        "912B3B",
        "39889A",
        "38B7DF",
        "DCB1B0",
        "91C5FE",
        "A9FC43",
        "88D106",
        "C3F7BD",
        "6892A5",
        "336F86",
        "D30D04",
        "18CEAD",
        "5615EC",
        "255B7F",
        "0A37AB",
        "E7FE5F",
        "368052",
        "DA9E07",
        "B2C0E4",
        "0EF369",
        "F51E37",
        "E7E673",
        "84E23E",
        "9E16FF",
        "B0EA34",
        "43952D",
        "D04B6B",
        "FF0E13",
        "CB1E21",
        "DD1B74",
        "0C8A2A",
        "7FACA1",
        "8A0882",
        "B5DD3F",
        "F0C0C4",
        "5C1D63",
        "8E22AD",
        "3374B0",
        "675459",
        "449156",
        "5B2688",
        "A06C31",
        "9741BF",
        "12776D",
        "0A29B7",
        "F1228B",
        "A2C1FF",
        "2876A2",
        "6B4E2B",
        "B35DD1",
        "5D27FB",
        "2ADFBC",
        "ED564F",
        "8BBD9E",
        "851E2E",
        "F7B1FB",
        "D25A10",
        "70EC62",
        "CEE8C7",
        "64D82F",
        "727346",
        "E183BA",
        "43A2F1",
        "5C034C",
        "BB1844",
        "8C6FFA",
        "6DBF17",
        "95B47B",
        "5D750C",
        "1C824C",
        "6C8DC7",
        "725327",
        "BBC6F4",
        "1429A3",
        "5BFDE4",
        "A5122D",
        "AA00E2",
        "8AE51D",
        "A22CCD",
        "F28FF7",
        "3AC4DF",
        "28A388",
        "512463",
        "1064C2",
        "1C5AB5",
        "2EFF3C",
        "E5489D",
        "1EE325",
        "745E92",
        "1BE669",
        "B88A7B",
        "761CFA",
        "90984C",
        "DB12AB",
        "4B631D",
        "CD657E",
        "1F42B3",
        "D447D8",
        "4B45EE",
        "13986B",
        "538B80",
        "99FECA",
        "2AF61D",
        "F683C6",
        "1D9B50",
        "7A306B",
        "0050F1",
        "A1BA8D",
        "7740A0",
        "6CD082",
        "00D403",
        "F03402",
        "6B426C",
        "0E44EF",
        "45C164",
        "3740B5",
        "4A58F6",
        "B62F88",
        "C870C5",
        "00BC21",
        "168573",
        "ABE04E",
        "7F49FC",
        "2C49D1",
        "FD2A94",
        "CAA501",
        "8BD7B1",
        "5319C0",
        "5FCA8A",
        "B87E30",
        "2FBD4B",
        "FD7C43",
        "D96F33",
        "F82C3B",
        "6F3DD6",
        "E06ADA",
        "6C8D9C",
        "076669",
        "A62C26",
        "785B63",
        "253801",
        "36EB47",
        "84FEB5",
        "85BB2D",
        "19675D",
        "A73DF3",
        "E2ADEE",
        "46235E",
        "9E4496",
        "2B0925",
        "7CDBAC",
        "E9F86D",
        "7B49F9",
        "888CD2",
        "30D3AF",
        "92C6D6",
        "2CF256",
        "0C1450",
        "EE96B6",
        "8E7611",
        "6B4211",
        "94D872",
        "F7E0B4",
        "0A3A1E",
        "09C80E",
        "A69E8B",
        "01FDA6",
        "09EFAA",
        "4B4755",
        "56F2EF",
        "085A7E",
        "57055B",
        "B5595F",
        "39A80F",
        "E65D83",
        "D8C324",
        "18B2D0",
        "D8622B",
        "264CF5",
        "CDB1A3",
        "58C2BE",
        "6D61F4",
        "2DC80F",
        "4268F5",
        "DB28DD",
        "C25850",
        "6BDDDD",
        "10AE9A",
        "EDD46C",
        "A37DC5",
        "A87F1D",
        "088E56",
        "B76560",
        "05DDA3",
        "947114",
        "6CDECE",
        "BC64BB",
        "B632CA",
        "2DFFA9",
        "34EB60",
        "FDCCB8",
        "A750C0",
        "C77094",
        "AB1ABC",
        "3F12A7",
        "294E50",
        "708C04",
        "DCB4C5",
        "87191D",
        "65C776",
        "E90386",
        "4F6CC7",
        "194DD1",
        "2584FA",
        "15FDD6",
        "4C05F9",
        "B48204",
        "92DDFB",
        "E11760",
        "176054",
        "7908F0",
        "1A4AD5",
        "E67C46",
        "72899E",
        "9A50BA",
        "4245A3",
        "5CE96B",
        "E52616",
        "C99422",
        "2CD8D8",
        "32B876",
        "CD3A69",
        "65E9B0",
        "08A9CD",
        "CFA988",
        "2BAE42",
        "50F8B6",
        "12C0B7",
        "1B0B4D",
        "91C3A5",
        "BD16B5",
        "915891",
        "FA3BBF",
        "3CA38F",
        "010D4B",
        "209475",
        "906F9F",
        "08A436",
        "362EAA",
        "EABF80",
        "BB14F8",
        "998082",
        "09AAEE",
        "11430F",
        "EEAAE2",
        "A9DCEC",
        "585E8E",
        "088A36",
        "848D88",
        "C67705",
        "9BE67C",
        "3D49BD",
        "8B5169",
        "7EE0C6",
        "89DF0D",
        "499301",
        "04E5E9",
        "27588B",
        "1FA0F6",
        "78F48F",
        "2D9B0A",
        "C0EB5D",
        "584A0C",
        "52CF2C",
        "5A45ED",
        "40AECA",
        "89B741",
        "49983A",
        "59C19F",
        "EF9348",
        "099A75",
        "50E073",
        "2CDC51",
        "6AA3C4",
        "3A3CD7",
        "5D1E79",
        "3C92D1",
        "60D3C2",
        "43CF79",
        "4A3770",
        "FCD1A5",
        "AE2410",
        "5702BD",
        "5F12F8",
        "B43EBA",
        "FB6DC1",
        "37F5B0",
        "508633",
        "4835B3",
        "E77152",
        "B5E22B",
        "4524BD",
        "41DD70",
        "0C9315",
        "60CD12",
        "0D7E0A",
        "94FC9B",
        "9DC6B4",
        "7B01E2",
        "642323",
        "521D11",
        "7B677F",
        "20DF78",
        "3F3412",
        "6879B9",
        "D0BEEC",
        "0587CF",
        "7F04E7",
        "D26168",
        "4D0B6B",
        "43C02A",
        "C3F5AC",
        "41C46B",
        "C4D364",
        "BA2B59",
        "69D2AF",
        "D62CBD",
        "90E545",
        "109F3F",
        "3FA6AF",
        "F09C33",
        "C0AED6",
        "B67ACB",
        "FDC9D0",
        "91F47A",
        "36BD3E",
        "1FFCEC",
        "2A3A40",
        "64E2EB",
        "37C3B4",
        "DFB8DE",
        "7EE7BC",
        "3E678B",
        "7EF61D",
        "245E81",
        "261DFE",
        "C6DAE8",
        "616D9F",
        "81D77E",
        "593A8B",
        "CB2D81",
        "B589F6",
        "268931",
        "8C254A",
        "49474C",
        "3085E1",
        "7A6F36",
        "65CEE0",
        "06C3C0",
        "E0A28E",
        "FCF72D",
        "897F9A",
        "5F01EF",
        "2E6F22",
        "F03A2C",
        "82889A",
        "524C1D",
        "76D88B",
        "7AAD9C",
        "F9C34F",
        "FC184B",
        "2AE67F",
        "4E616E",
        "DD97B3",
        "3BD0E1",
        "0EE163",
        "D9DB04",
        "B4316A",
        "038AA3",
        "DEEBFC",
        "CFBA11",
        "DFBBBB",
        "060386",
        "D9A535",
        "9147C3",
        "483F35",
        "014BCF",
        "7C670F",
        "DE884C",
        "DDE14B",
        "484877",
        "D88235",
        "2B2922",
        "801185",
        "E52C77",
        "7B0B47",
        "32FC43",
        "17F401",
        "7828AA",
        "D80047",
        "8C3877",
        "FBAF7F",
        "3862C7",
        "44F6CA",
        "1A21B7",
        "933CBB",
        "4B6FBD",
        "EF6523",
        "C67CD4",
        "6EE80A",
        "FAD379",
        "FC55B1",
        "3909E3",
        "DA9467",
        "9D5756",
        "250097",
        "983FEE",
        "0181B7",
        "482ED9",
        "566BEB",
        "10110A",
        "9A3C91",
        "BA23CE",
        "B16DF3",
        "659C08",
        "828948",
        "4D38AC",
        "957C94",
        "A45025",
        "48AE4B",
        "6DDE71",
        "7CFA49",
        "7EFFA9",
        "35E960",
        "FA999D",
        "5FB3E2",
        "55E402",
        "E70E7B",
        "7B0546",
        "631FDA",
        "D39867",
        "BBD9FD",
        "CE5DCD",
        "8488AD",
        "F0000E",
        "AD1468",
        "B139B3",
        "771D4E",
        "AD225C",
        "F5D05D",
        "F0B141",
        "9F3C9E",
        "0051DA",
        "0872AD",
        "FA2CB7",
        "AA85CC",
        "75CA25",
        "826E44",
        "84CF77",
        "C71F3D",
        "7E8F44",
        "BB975C",
        "DEE3D2",
        "75735F",
        "A26C1A",
        "A9828C",
        "6380BD",
        "C8CBB9",
        "E3F564",
        "517BE9",
        "582DAA",
        "A1E22A",
        "0F2DBE",
        "6926F9",
        "B4A2F9",
        "B41E2C",
        "9DE7F0",
        "2004DB",
        "3446A4",
        "F58988",
        "23D420",
        "0BDE3D",
        "F5D0AB",
        "BDF039",
        "43FDC7",
        "5FB34D",
        "34803B",
        "E31C3B",
        "7F96FD",
        "04001D",
        "77C2A0",
        "0D59E9",
        "4CC680",
        "1FFA6F",
        "773775",
        "4FC117",
        "2258B3",
        "100E69",
        "F79E1F",
        "D9711E",
        "65E370",
        "B9201D",
        "43E414",
        "D0C6FE",
        "6D7DE8",
        "C5EA95",
        "A4FD50",
        "A949D5",
        "DB6916",
        "883F62",
        "8286D2",
        "C87B5C",
        "C05093",
        "57FC11",
        "39968F",
        "912270",
        "438BFE",
        "8BEEB8",
        "1100D1",
        "10BB74",
        "A15D3D",
        "D80640",
        "4CB3A6",
        "BC8CD6",
        "DE78AE",
        "C50223",
        "FFC050",
        "0ACBD7",
        "293A50",
        "03F7C9",
        "69E6B1",
        "AA16A7",
        "7B146E",
        "B98F3D",
        "041FBD",
        "927882",
        "93DAA8",
        "21436B",
        "224A18",
        "81C918",
        "7ABF23",
        "2C7F71",
        "893CDA",
        "7FCC9D",
        "42F1C0",
        "A4B53D",
        "95A051",
        "2EB6B8",
        "027CF1",
        "A34A50",
        "AF4548",
        "3DEDE4",
        "F12A7D",
        "280A50",
        "BF3FA9",
        "0485AD",
        "EDACB9",
        "0BA352",
        "18A22F",
        "2EF6E9",
        "FFE748",
        "5360F2",
        "90D432",
        "65B07E",
        "09D00C",
        "AFB870",
        "1C38C3",
        "A637A7",
        "A1C523",
        "42D13E",
        "DDD965",
        "972DFE",
        "0A531F",
        "AC0722",
        "B65979",
        "7564EC",
        "A84C54",
        "B6E090",
        "04C1CE",
        "475A0D",
        "3729C1",
        "67AB30",
        "FE6EF0",
        "E05B12",
        "A69F0A",
        "C42FEF",
        "146CF9",
        "CF83D8",
        "4C898A",
        "B21512",
        "0E62E4",
        "1F98B9",
        "289BB7",
        "3F3C9B",
        "75E8BF",
        "BBE1DC",
        "6FB087",
        "AAF35B",
        "A9AE53",
        "AC9854",
        "80F62D",
        "39DF95",
        "63F675",
        "11EB04",
        "FA1936",
        "DC7D39",
        "A6375C",
        "DC0D27",
        "2491FA",
        "5F5788",
        "D64537",
        "FEE263",
        "F30F02",
        "736156",
        "BB602F",
        "906E69",
        "55748D",
        "771872",
        "AF610B",
        "8C7FC9",
        "E6A440",
        "EA56EE",
        "4655ED",
        "79CDBC",
        "938035",
        "A1C460",
        "45BAB9",
        "8FFE5E",
        "BC77A2",
        "446D49",
        "2EBE32",
        "F87A23",
        "3B23A7",
        "2549DF",
        "C133F8",
        "D1790A",
        "B023A5",
        "6E192C",
        "1415EF",
        "5A18E0",
        "1B2853",
        "31364D",
        "BBCD4E",
        "952BB0",
        "B0BC99",
        "DA5F3A",
        "26B6C0",
        "38BF60",
        "EF50B0",
        "161C3B",
        "505B09",
        "63F19C",
        "2D4DDA",
        "DBA3B6",
        "4DD590",
        "0F16A1",
        "F04F2D",
        "B4A028",
        "A0353F",
        "C7C9D5",
        "9E5B5F",
        "C40033",
        "EF79FA",
        "1AA40E",
        "4C6154",
        "6F2BA7",
        "B7CC70",
        "F607FF",
        "109C5A",
        "BA61BC",
        "62C9E7",
        "09ED56",
        "E5CECC",
        "DED7A2",
        "16D878",
        "4EA078",
        "882758",
        "D3DA19",
        "6F7372",
        "688400",
        "C5E766",
        "FEE253",
        "A377D9",
        "149980",
        "CF8539",
        "6FE564",
        "B63988",
        "D2B5A9",
        "FCD865",
        "825178",
        "BD793E",
        "EE518D",
        "A506AA",
        "F97C2D",
        "2AF7C7",
        "075818",
        "6F7B1F",
        "9B491F",
        "419BEC",
        "906983",
        "09B61C",
        "F7C63D",
        "6C9B6B",
        "BAC46B",
        "0FC784",
        "B9E6FF",
        "2F7F6A",
        "DC778D",
        "238F8E",
        "A9E716",
        "CC0A20",
        "95F056",
        "B2339B",
        "0CE9C6",
        "87F6E1",
        "DADD40",
        "ED6DEB",
        "49E7C7",
        "2D4070",
        "708776",
        "841625",
        "603CE2",
        "82C6A9",
        "EC62DE",
        "34EBC5",
        "25A3BD",
        "91EDEC",
        "F7FBDA",
        "4C6BE3",
        "9288D5",
        "DFA735",
        "5C7396",
        "09D04B",
        "A97056",
        "4F8D76",
        "356DD9",
        "326A50",
        "059E5E",
        "AF820D",
        "85C134",
        "769E36",
        "768E1E",
        "E24709",
        "6B9EDA",
        "B5F872",
        "CF95DC",
        "C43534",
        "316797",
        "1F2BDF",
        "59551C",
        "8DB138",
        "D0D150",
        "592C1B",
        "32A6D8",
        "531B82",
        "810324",
        "C04A19",
        "B73D34",
        "8763D4",
        "B38CF1",
        "F720B4",
        "485926",
        "3EE6B1",
        "A49177",
        "63BE0A",
        "FF110C",
        "654BE7",
        "215081",
        "235B4D",
        "2A0D90",
        "8809A1",
        "606BB5",
        "3E68EF",
        "902FC7",
        "CF1DDA",
        "E53FFD",
        "06E71A",
        "C583D6",
        "277473",
        "B43D10",
        "805CF5",
        "90B87D",
    ]
    l = len(color_list)
    if i < l:
        return "#" + color_list[i]
    else:
        return "#%02x%02x%02x" % (r(), r(), r())


def get_module_parent_path():
    return str(Path(get_module_path()).parent)


def get_last_run_log_fp():
    mpp = get_module_parent_path()
    log_fn = "azenqos_qgis_plugin_last_run_log.txt"
    log_fp = os.path.join(mpp, log_fn)
    return log_fp


class tee_stdout(object):
    def __init__(self, name, mode):
        self.file = open(name, mode)
        self.stdout = sys.stdout
        sys.stdout = self
    def __del__(self):
        self.close()
    def close(self):
        if self.file is not None:
            sys.stdout = self.stdout
            self.file.close()
        self.file = None
    def write(self, data):
        if data is None:
            return
        ori_data = data
        data = data.strip()
        if self.file is not None:
            if data.strip():
                self.file.write(time.strftime('%Y-%m-%d-%H:%M:%S')+": ")
                self.file.write(data)
                self.file.write("\n")
        self.stdout.write(ori_data)
    def flush(self):
        if self.file is not None:
            self.file.flush()
        self.stdout.flush()


g_tee_stdout_obj = None
def close_last_run_log():
    global g_tee_stdout_obj
    if g_tee_stdout_obj is not None:
        g_tee_stdout_obj.close()


def open_and_redirect_stdout_to_last_run_log():
    global g_tee_stdout_obj
    try:
        close_last_run_log()
        g_tee_stdout_obj = tee_stdout(get_last_run_log_fp(), 'w')

        import version
        print("--- new stdout log start version: {} ---".format(("%.03f" % version.VERSION)))
    except:
        type_, value_, traceback_ = sys.exc_info()
        exstr = str(traceback.format_exception(type_, value_, traceback_))
        print("WARNING: open_and_redirect_stdout_to_last_run_log exception:", exstr)


def tmp_gen_path_parent():
    dp = os.path.join(get_module_path(), TMP_FOLDER_NAME)
    if is_container_mode():
        assert os.path.isdir(CONTAINER_MODE_TMP_GEN_PATH)
        dp = os.path.join(CONTAINER_MODE_TMP_GEN_PATH, get_container_name())
    if not os.path.isdir(dp):
        os.makedirs(dp)
    return dp


g_tmp_gen_instance_uuid = str(uuid.uuid4())
def tmp_gen_new_instance():
    global g_tmp_gen_instance_uuid
    g_tmp_gen_instance_uuid = str(uuid.uuid4())


def tmp_gen_path():
    global g_tmp_gen_instance_uuid
    dp = os.path.join(tmp_gen_path_parent(), str(os.getpid()), g_tmp_gen_instance_uuid)
    if not os.path.isdir(dp):
        os.makedirs(dp)
    return dp

def tmp_gen_new_subdir():
    dp = tmp_gen_fp("tmp_subdir_{}".format(uuid.uuid4()))
    assert not os.path.isdir(dp)
    os.mkdir(dp)
    assert os.path.isdir(dp)
    return dp

def tmp_gen_fp(fn):
    return os.path.join(tmp_gen_path(), fn)

def cleanup_died_processes_tmp_folders():
    import psutil

    print("cleanup_died_processes_tmp_folders() START")
    tgp = tmp_gen_path_parent()
    dirlist = os.listdir(tgp)
    print("dirlist:", dirlist)
    dirlist_no_pid = []
    for folder_name in dirlist:
        int_folder_name = None
        print("conv folder_name:", folder_name)
        try:
            int_folder_name = int(folder_name)
        except Exception as ex:
            print("conv folder_name exception so skip:", folder_name, ex)
            continue
        if psutil.pid_exists(int_folder_name):
            print("conv folder_name pid exists so skip", folder_name)
            continue
        else:
            dirlist_no_pid.append(str(int_folder_name))
    print("dirlist_no_pid:", dirlist_no_pid)
    dp_list = [os.path.join(tgp, x) for x in dirlist_no_pid]
    dp_list_dirs = [x for x in dp_list if os.path.isdir(x)]
    print("dp_list_dirs:", dp_list)
    for dp in dp_list_dirs:
        try:
            print("rmtree dir:", dp)
            shutil.rmtree(dp)
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print(
                "WARNING: cleanup_died_processes_tmp_folders rmtree - exception: {}".format(
                    exstr
                )
            )
    print("cleanup_died_processes_tmp_folders() DONE")



def calc_sha(src):
    if src is None:
        return None
    if isinstance(src, str):
        src = src.encode("ascii")
    hasho = hashlib.sha1()
    hasho.update(src)
    return hasho.hexdigest()


def download_file(url, local_fp, auth_token=""):
    # NOTE the stream=True parameter below
    headers = {"Authorization": "Bearer {}".format(auth_token), }
    with requests.get(url, stream=True, verify=False, headers=headers) as r:
        r.raise_for_status()
        with open(local_fp, "wb") as f:
            for chunk in r.iter_content(chunk_size=2048 * 1000):
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                # if chunk:
                f.write(chunk)
    return local_fp


# helper func that wont emit if signal is None
def signal_emit(signal_obj, emit_obj):
    print("signal_emit: {}: {}".format(signal_obj, emit_obj))
    if signal_obj is not None:
        signal_obj.emit(emit_obj)


def datetime_now():
    return datetime.datetime.now()


def datetimeStringtoTimestamp(datetimeString):
    if isinstance(datetimeString, QtCore.QDateTime):
        datetimeString = float(datetimeString.toSecsSinceEpoch())
    try:
        element = None
        if isinstance(datetimeString, float):
            element = datetime.datetime.fromtimestamp(datetimeString)
        elif isinstance(datetimeString, str):
            try:
                element = datetime.datetime.strptime(datetimeString, "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                element = datetime.datetime.strptime(datetimeString, "%Y-%m-%d %H:%M:%S")  # some ts str comes without millis like: "2021-04-22 15:22:18"
        timestamp = datetime.datetime.timestamp(element)
        return timestamp
    except:
        type_, value_, traceback_ = sys.exc_info()
        exstr = str(traceback.format_exception(type_, value_, traceback_))
        print("datetimestringtotimestamp exception: %s" % exstr)
    return None



def get_qgis_layers_dict():
    ret = {}
    try:
        from qgis._core import QgsProject
        layers = QgsProject.instance().mapLayers().values()
        for layer in layers:
            ret[layer.name()] = layer
    except Exception as e:
        print("WARNING: layer_name_to_layer_dict exception:", e)
    return ret


def write_dict_to_ini(d, fpath):
    try:
        import configparser
        with open(fpath, "w") as f:
            config = configparser.ConfigParser()
            config.add_section('main')
            for key in d:
                config.set('main', key, str(d[key]))
            config.write(f)
    except:
        type_, value_, traceback_ = sys.exc_info()
        exstr = str(traceback.format_exception(type_, value_, traceback_))
        print(("WARNING: write ini {} exception {}".format(fpath, exstr)))


def load_ini_to_dict_keys(fpath, d):
    if not os.path.isfile(fpath):
        return False
    try:
        import configparser
        config = configparser.ConfigParser()
        with open(fpath,"r") as f:
            config.read_file(f)
        for key in d:
            try:
                d[key] = config.get('main', key)
                d[key] = str(d[key])
            except Exception as pe:
                print(("WARNING: load config for key: {} failed with exception: {}".format(key, pe)))
            print(('load key {} final val {} type {}'.format(key, d[key], type(d[key]))))
        return True
    except:
        type_, value_, traceback_ = sys.exc_info()
        exstr = str(traceback.format_exception(type_, value_, traceback_))
        print(("WARNING: load ini {} exception {}".format(fpath, exstr)))
    return False


def launch_file(fp):
    if not os.path.isfile(fp):
        return
    if os.name == "nt":
        os.startfile(fp)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        import subprocess
        subprocess.call([opener, fp])


def ask_custom_sql_or_py_expression(parent, title="Custom SQL/Python expression", existing_content="", table_view_mode=False, msg="Enter SQL select or Python expression"):
    import qt_utils
    import sql_utils
    is_list_or_dict = False
    if isinstance(existing_content, (list, dict)):
        is_list_or_dict = True
        existing_content = json.dumps(existing_content, indent = 4)
    expression = qt_utils.ask_text(parent, title=title, msg=msg, existing_content=existing_content, multiline=True)
    if expression is not None and is_list_or_dict == True:
        expression = json.loads(expression)
    if expression is not None and table_view_mode and sql_utils.is_sql_select(expression):
        expression = "pd.read_sql('''{}''',dbcon)".format(expression)
    return expression


def get_adb_command():
    return os.path.join(get_module_path(), "scrcpy_nt", "adb.exe") if os.name == "nt" else "adb"


def get_scrcpy_command():
    return  os.path.join(get_module_path(),
    "scrcpy_nt", "scrcpy.exe") if os.name == "nt" else "scrcpy"


def get_failed_scrcpy_cmd():
    scrcpy_cmd = get_scrcpy_command()
    adb_cmd = get_adb_command()
    # test scrcpy
    test_cmds = [(scrcpy_cmd,"--version"), (adb_cmd, "--version")]
    for test_cmd in test_cmds:
        sret = call_no_shell(test_cmd)
        if sret != 0:
            return test_cmd
    return ""


def check_and_recover_db(dbfp, tmp_path, write_debug_sql_file=False):
    needs_recover_db = False
    sqlite_bin = get_sqlite_bin()
    assert os.path.isfile(sqlite_bin)
    with contextlib.closing(sqlite3.connect(dbfp)) as dbcon:
        try:
            integ_check_df = pd.read_sql("PRAGMA integrity_check;", dbcon)
            print("azq_report_gen: sqlite db integ_check_df first row:", integ_check_df.integrity_check[0])
            if integ_check_df.integrity_check.iloc[0] != "ok":
                print("WARNING: read_sql pragma integrity_check not ok - flag needs_recover_db")
                needs_recover_db = True
        except Exception as integcheck_ex:
            print("WARNING: read_sql pragma integrity_check failed exception:", integcheck_ex)
            needs_recover_db = True
    if needs_recover_db:
        sql_script = dump_sqlite(dbfp)
        assert sql_script
        out_db_fp = os.path.join(tmp_path, "adb_log_snapshot_dump_recov_{}.db".format(uuid.uuid4()))
        with contextlib.closing(sqlite3.connect(out_db_fp)) as out_dbcon:
            print("... merging to target db file:", out_db_fp)
            if write_debug_sql_file:
                sqlfpfordebug = out_db_fp+".sql"
                with open(sqlfpfordebug, 'w') as f:
                    f.write(sql_script)
            out_dbcon.executescript(sql_script)
            out_dbcon.commit()
        dbfp = out_db_fp
    return dbfp

def current_milli_time():
    return round(time.time() * 1000)

def live_mode(gc, device_dict, db_queue):
    def temp():
        gc.live_mode_update_time = True
        device_key = device_dict["key"]
        process = popen_no_shell((get_adb_command(), "-s", device_key, "shell", "busybox", "tail", "-f",  "/sdcard/diag_logs/azqdata.db.sql"))
        gc.live_process_list.append(process)
        for line in iter(process.stdout.readline, b''):
            line = line.decode("utf-8")
            sql_script = line[len("SQLiteProgram: "):]
            db_queue.put(sql_script)
            match_table = re.search(r"^INSERT INTO \"(\S*)\"",sql_script).group(1)
            if match_table in gc.params_to_gen.keys():
                for param in gc.params_to_gen[match_table]:
                    view = param
                    if match_table == view:
                        view = match_table+"_1"
                    sql_script_view = sql_script.replace('INTO "{}"'.format(match_table), 'INTO "{}"'.format(view))
                    db_queue.put(sql_script_view)
    return temp

def live_mode_db_insert(gc, refresh_signal, db_queue):
    def temp():
        dbfp = gc.databasePath
        start_time_ms = current_milli_time()
        with contextlib.closing(sqlite3.connect(dbfp)) as dbcon:
            dbcon.execute('PRAGMA journal_mode=WAL;')
            dbcon.execute('BEGIN;')
            while gc.live_mode:
                item = None 
                try:
                    item = db_queue.get(block=True, timeout=1)
                except:
                    pass
                if item is None:
                    continue
                try:
                    dbcon.execute(item)
                except:
                    pass
                current_time_ms  = current_milli_time()
                if (current_time_ms - start_time_ms) > 1*1000:
                    start_time_ms = current_time_ms
                    gc.maxTimeValue = current_time_ms / 1000
                    gc.sliderLength = gc.maxTimeValue - gc.minTimeValue
                    gc.sliderLength = round(gc.sliderLength, 3)
                    dbcon.commit()
                    dbcon.execute('BEGIN;')
                    refresh_signal.emit()
    return temp

def pull_latest_log_db_from_phone(parent=None, gc = None):
    close_scrcpy_proc()  # if left open we somehow see adb pull fail cases in windows
    gc.device_configs = []
    adb_devices = list(set([device.split('\t')[0] for device in check_output_no_shell((get_adb_command(), "devices")).splitlines() if device.endswith('\tdevice')]))
    logs = []
    for adb_device in adb_devices:
        adb_device_name = check_output_no_shell((get_adb_command(), "-s", adb_device, "shell", "dumpsys bluetooth_manager | \grep 'name:' | cut -c9-")).strip()
        
        db_journal_fp = os.path.join(tmp_gen_path(), "adb_log_snapshot_{}.db-journal".format(adb_device))
        call_no_shell((get_adb_command(), "-s", adb_device, "pull", "/sdcard/diag_logs/azqdata.db-journal", db_journal_fp))
        dbfp = os.path.join(tmp_gen_path(), "adb_log_snapshot_{}.db".format(adb_device))
        if os.path.exists(db_journal_fp):
            os.remove(db_journal_fp)
        if os.path.exists(dbfp):
            os.remove(dbfp)
        
        cmd = (get_adb_command(), "-s", adb_device, "pull", "/sdcard/diag_logs/azqdata.db", dbfp)
        ret = 1
        try_n = 0
        while ret != 0 and try_n < 10:
            ret = call_no_shell(cmd)
            try_n += 1
        print("total pull: ", try_n, "ret: ", ret)
        if ret != 0:
            QtWidgets.QMessageBox.critical(
                parent,
                "Failed to pull data from {}".format(adb_device_name),
                "- Please make sure that you have a phone with AZENQOS netmon/script running connected via USB.\n- Please make sure phone has 'USB Debugging' enabled in phone settings >> 'Developer options'.",
                QtWidgets.QMessageBox.Cancel,
            )
            return None
        dbfp = check_and_recover_db(dbfp, tmp_gen_path())
        assert os.path.isfile(dbfp)
        logs.append(dbfp)
        log_hash = None
        with contextlib.closing(sqlite3.connect(dbfp)) as dbcon:
            log_hash = str(pd.read_sql("select log_hash from logs limit 1", dbcon)["log_hash"][0])
            gc.device_configs.append({"key":adb_device, "name":adb_device_name, "log_hash":[log_hash]})
    start_scrcpy_proc(adb_devices)
    return logs


CREATE_NO_WINDOW = 0x08000000


def call_no_shell(cmd_list):
    assert isinstance(cmd_list, list) or isinstance(cmd_list, tuple)
    cmdret = -99
    if os.name == "nt":
        cmdret = subprocess.call(cmd_list, shell=False, creationflags=CREATE_NO_WINDOW)
    else:
        cmdret = subprocess.call(cmd_list, shell=False)
    return cmdret


def check_output_no_shell(cmd_list):
    assert isinstance(cmd_list, list) or isinstance(cmd_list, tuple)
    if os.name == "nt":
        return subprocess.check_output(cmd_list, shell=False, encoding='utf-8', creationflags=CREATE_NO_WINDOW)
    else:
        return subprocess.check_output(cmd_list, shell=False, encoding='utf-8')
    return None


g_scrcpy_proc_list = []
def start_scrcpy_proc(adb_devices = None):
    global g_scrcpy_proc_list
    close_scrcpy_proc()
    assert len(g_scrcpy_proc_list) == 0
    for adb_device in adb_devices:
        g_scrcpy_proc_list.append(scrcpy_popen(adb_device))


def is_scrcpy_proc_running():
    global g_scrcpy_proc_list
    for g_scrcpy_proc in g_scrcpy_proc_list:
        if g_scrcpy_proc.poll() is None:
            return True
    return False


def close_scrcpy_proc():
    global g_scrcpy_proc_list
    if is_scrcpy_proc_running():
        for g_scrcpy_proc in g_scrcpy_proc_list:
            try:
                g_scrcpy_proc.terminate()
            except Exception as e:
                print("WARNING: terminate prev scrcpy process failed with exception: {}".format(e))
            if is_scrcpy_proc_running():
                try:
                    g_scrcpy_proc.kill()
                except Exception as e:
                    print("WARNING: kill prev scrcpy process failed with exception: {}".format(e))
            if is_scrcpy_proc_running():
                print("WARNING: still g_scrcpy_proc_list.poll() is None (still running) after kill() and terminate()")
    g_scrcpy_proc_list = []


def adb_kill_server_threaded():
    t = threading.Thread(target=adb_kill_server, daemon=False)
    t.start()
    t.join()


def adb_kill_server():
    try:
        ret = call_no_shell((get_adb_command(), 'kill-server'))
        print("adb_kill_server() ret", ret)
    except Exception as e:
        print("WARNING: adb_kill_server exception:", e)



def scrcpy_popen(adb_device):
    cmd = (get_scrcpy_command(), "-s", adb_device)
    return popen_no_shell(cmd)


def popen_no_shell(cmd):
    proc = None
    if os.name == "nt":
        proc = subprocess.Popen(
            cmd,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            creationflags=CREATE_NO_WINDOW
        )
    else:
        proc = subprocess.Popen(
            cmd,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
    return proc


def dump_sqlite(dbfp):
    sqlite_bin = get_sqlite_bin()
    dump_fp = tmp_gen_fp("tmp_sqlite_dump_{}.sql".format(uuid.uuid4()))
    if os.path.isfile(dump_fp):
        os.remove(dump_fp)
    assert not os.path.isfile(dump_fp)
    cmd = [sqlite_bin, dbfp, "-cmd", ".out '{}'".format(dump_fp), ".dump"]
    print("... dumping db file to sql:", dbfp, "cmd:", cmd)
    ret = call_no_shell(cmd)
    assert ret == 0
    assert os.path.isfile(dump_fp)
    return dump_fp

def get_sqlite_bin():
    return os.path.join(
        get_module_path(),
        os.path.join(
            "sqlite_" + os.name,
            "sqlite3" + ("" if os.name == "posix" else ".exe"),
        ),
    )

def get_spatialite_bin():
    return os.path.join(
        get_module_path(),
        os.path.join(
            "sqlite_" + os.name,
            "spatialite" + ("" if os.name == "posix" else ".exe"),
        ),
    )

def get_create_cellfile_spatialite_header(rat):
    sql_str = """PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
INSERT INTO "geometry_columns" VALUES('{}','geometry',3,2,4326,0);\n""".format(rat)

    return sql_str

def get_create_cellfile_spatialite_create_table(rat, columns):
    start_str = """CREATE TABLE '{}' ( "ogc_fid" INTEGER PRIMARY KEY AUTOINCREMENT,""".format(rat)
    for col in columns:
        if col == "index":
            pass
        elif col != "sector_polygon_wkt":
            start_str += " '{}' VARCHAR, ".format(col)
        else:
            start_str += ''' "GEOMETRY" POLYGON '''
    start_str += ");"
    return start_str

def get_create_cellfile_spatialite_insert_cell(rat, df):
    df_col = list(df.columns)
    df["spatial"] = '''INSERT INTO "{}" VALUES('''.format(rat)

    for col in df_col:
        df[col] = df[col].astype(str)
        if col == "index":
            df["spatial"] = df["spatial"] + " " + df[col] + ","
        elif col != "sector_polygon_wkt":
            df["spatial"] = df["spatial"] + " '" + df[col].astype(str).str.replace("'","''") + "',"
        else:
            df["spatial"] = df["spatial"] + " ST_GeomFromText('" + df[col] + "')"

    df["spatial"] += ");"
    return "\n".join(list(df["spatial"]))

def get_create_cellfile_spatialite_footer():
    ret = """\nPRAGMA writable_schema=OFF;
COMMIT;"""
    return ret

def set_none_to_repetetive_rows(df, cols):
    # set None to repetetive rows - https://stackoverflow.com/questions/19463985/pandas-drop-consecutive-duplicates
    try:
        df.loc[((df[cols].shift() == df[cols]).all
                (axis=1)), cols] = None
    except Exception:
        type_, value_, traceback_ = sys.exc_info()
        exstr = str(traceback.format_exception(type_, value_, traceback_))
        print("WARNING: set_none_to_repetetive_rows exception:", exstr)


def resample_per_log_hash_time(param_df, resample_param, use_last=False):
    assert len(param_df)
    ori_cols = param_df.columns
    assert "log_hash" in ori_cols
    assert "time" in ori_cols
    #print("resample_per_log_hash_time param_df0:\n", param_df.head())
    param_df = param_df.groupby('log_hash', as_index=True).apply(
        lambda df: df.drop_duplicates('time').set_index('time').resample(resample_param).pad() if not use_last else df.drop_duplicates('time').set_index('time').resample(resample_param).last().ffill()
    )
    #print("resample_per_log_hash_time param_df1:\n", param_df.head())
    del param_df["log_hash"]  # drop  the resampled log_hash col as can have nulls
    assert "log_hash" not in param_df.columns
    param_df = param_df.reset_index()  # pop-out log_hash
    assert "log_hash" in param_df.columns
    #print("resample_per_log_hash_time param_df2:\n", param_df.head())
    end_cols = param_df.columns
    #print("resample_per_log_hash_time: ori_cols:", ori_cols)
    #print("resample_per_log_hash_time: end_cols:", end_cols)
    assert len(ori_cols) == len(end_cols)
    assert set(ori_cols) == set(end_cols)
    return param_df


def create_layer_in_qgis(databasePath, df, layer_name, is_indoor=False, theme_param=None, add_to_qgis=True, new_db=True, svg_icon_fp=None, icon_fp=None, pp_voice_table=None, data_df=None):
    try:
        import preprocess_azm
        import qgis_layers_gen
        tmpdbfp = tmp_gen_fp("tmp_{}.db".format(uuid.uuid4()))
        if not new_db:
            assert databasePath
            assert os.path.isfile(databasePath)
            tmpdbfp = databasePath
        assert not os.path.isfile(tmpdbfp)

        table = "layer_dump" if theme_param is None else preprocess_azm.get_table_for_column(theme_param)
        if pp_voice_table is not None:
            table = pp_voice_table
        elif theme_param == "rat":
            table = "technology"
        elif theme_param == "pilot_pollution":
            table = "pilot_pollution"
        
        within_millis_of_gps=30 * 1000
        asof_lat_lon_direction="backward"
        if table == "logs" or table == "log_info":
            within_millis_of_gps=30 * 10000
            asof_lat_lon_direction="forward"

        if ((("lat" not in df.columns) and ("lon" not in df.columns)) and (("positioning_lat" not in df.columns) and ("positioning_lon" not in df.columns))) and databasePath is not None:
            print("need to merge lat and lon")
            with contextlib.closing(sqlite3.connect(databasePath)) as dbcon:
                df = preprocess_azm.merge_lat_lon_into_df(dbcon, df, within_millis_of_gps=within_millis_of_gps, asof_lat_lon_direction=asof_lat_lon_direction).rename(
                    columns={"positioning_lat": "lat", "positioning_lon": "lon"}
                )
        qgis_layers_gen.dump_df_to_spatialite_db(
            df, tmpdbfp, table, is_indoor=is_indoor
        )

        assert os.path.isfile(tmpdbfp)
        with contextlib.closing(sqlite3.connect(tmpdbfp)) as dbcon:
            return qgis_layers_gen.create_qgis_layer_from_spatialite_db(
            tmpdbfp, table, label_col="name" if "name" in df.columns else None, theme_param=theme_param, display_name=layer_name, dbcon_for_theme_legend_counts=dbcon, add_to_qgis=add_to_qgis
            , svg_icon_fp=svg_icon_fp, icon_fp=icon_fp, data_df=data_df)
    except:
        type_, value_, traceback_ = sys.exc_info()
        exstr = str(traceback.format_exception(type_, value_, traceback_))
        print(
            "WARNING: create_layer_in_qgis failed exception: {}".format(
                exstr
            )
        )


def get_theme_qml_tmp_file_for_param(table, col, dbfp, gen_theme_bucket_counts=True):
    print("get_theme_qml_tmp_file_for_param START")
    qml_fp = None
    try:
        assert os.path.isfile(dbfp)
        import db_preprocess
        dbcon = None
        try:
            if gen_theme_bucket_counts:
                dbcon = sqlite3.connect(dbfp)
            qml_fp = db_preprocess.gen_style_qml_for_theme(
                None, table, None, col,
                dbcon,
                to_tmp_file=True
            )
        finally:
            if dbcon:
                dbcon.close()
    except:
        type_, value_, traceback_ = sys.exc_info()
        exstr = str(traceback.format_exception(type_, value_, traceback_))
        print(
            "WARNING: gen_style_qml_for_theme col {} failed exception: {}".format(
                col, exstr
            )
        )
    print("get_theme_qml_tmp_file_for_param DONE")
    return qml_fp

g_timer_start_ts_dict = {}

def timer_start(tname=None):
    global g_timer_start_ts_dict
    if not tname:
        tname = str(sys._getframe().f_back.f_code.co_name)
    g_timer_start_ts_dict[tname] = datetime.datetime.now()

def timer_print(tname=None, extra="now"):
    if not tname:
        tname = sys._getframe().f_back.f_code.co_name
    dur = timer_get_dur(tname)
    msg = "timer: {} to {}: {} seconds".format(tname, extra, dur)
    print(msg)
    return dur

def timer_get_dur(tname):
    global g_timer_start_ts_dict
    if tname in g_timer_start_ts_dict:
        return (datetime.datetime.now()-g_timer_start_ts_dict[tname]).total_seconds()
    else:
        timer_start(tname)
        return 0
    return 0


def get_env_azq_lang():
    key = "AZQ_LANG"
    if key in os.environ:
        return os.environ[key]
    return "en"

def is_lang_th():
    return get_env_azq_lang() == "th"

th_translate_replace_dict = {
    "combined model": "ชุดทำนายร่วม",
    "model per grid": "ชุดทำนายแยกตาราง",
    "whole_year": "ทั้งปี",
    "lte_inst_rsrp": "ความแรงสัญญาณ_4G",
    "wcdma_aset_rscp": "ความแรงสัญญาณ_3G",
    "nr_servingbeam_ss_rsrp": "ความแรงสัญญาณ_5G",
    "gsm_rxlev_sub_dbm": "ความแรงสัญญาณ_2G",
    "prediction_from": "ผลทำนายจาก",
    "overview":"ภาพรวม",
    "gsm_rxqual_sub":"คุณภาพสัญญาณ 2G",
    "wcdma_aset_ecio":"คุณภาพสัญญาณ 3G",
    "lte_inst_rsrq":"คุณภาพสัญญาณ 4G",
    "lte_sinr":"คุณภาพสัญญาณเทียบสัญญาณอื่น 4G",
    "data_hsupa_total_e_dpdch_throughput":"ความเร็วในการส่งข้อมูล 3G",
    "lte_l1_dl_throughput_all_carriers_mbps": "ความเร็วในการรับข้อมูล 4G",
    "lte_l1_ul_throughput_all_carriers_mbps": "ความเร็วในการส่งข้อมูล 4G",
    "data_hsdpa_thoughput": "เร็วในการรับข้อมูล 3G",
}

def th_translate(msg):
    if msg is None:
        return None
    assert isinstance(msg, str)
    for key in th_translate_replace_dict:
        val = th_translate_replace_dict[key]
        msg = msg.replace(key, val)
    return msg


def take_screenshot_pil_obj(bbox=None):
    return ImageGrab.grab(bbox=bbox)