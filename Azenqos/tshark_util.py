import os
import re
import uuid
import subprocess
import azq_utils

CREATE_NO_WINDOW = 0x08000000
g_extract_so_tar_gz_done = False
# call this only once at start of program! otherwise will be very slow extracting .so in gnu/linux everytime...
def prepare_env_and_libs():
    global g_extract_so_tar_gz_done

    env = os.environ.copy()
    ws_bin_dir = azq_utils.get_module_fp("wireshark_" + os.name)
    env["LD_LIBRARY_PATH"] = ws_bin_dir
    if os.name == "posix" and not g_extract_so_tar_gz_done:
        extract_so_ret = os.system(
        "tar -xzf {}/libwireshark.so.0.tar.gz -C {}".format(ws_bin_dir, ws_bin_dir)
        )
        print("extract_so_ret:", extract_so_ret)
        g_extract_so_tar_gz_done = True
    return env


def tshark_decode_hex(side, name, protocol, detail):
    env = prepare_env_and_libs()
    tsharkPath = os.path.join(
        azq_utils.get_module_path(),
        os.path.join(
            "wireshark_" + os.name,
            "tshark" + ("" if os.name == "posix" else ".exe"),
        ),
    )
    text2pcapPath = os.path.join(
        azq_utils.get_module_path(),
        os.path.join(
            "wireshark_" + os.name,
            "text2pcap" + ("" if os.name == "posix" else ".exe"),
        ),
    )
    print("tsharkPath", tsharkPath)
    print("text2pcapPath", text2pcapPath)
    if side == "recv":
        hexStr = "i "
    else:
        hexStr = "o "
    hexStr = hexStr + "000000 "
    msg = "msg_raw_hex: "
    msg_raw_hex = detail[detail.rindex(msg) + len(msg):]
    if protocol == "5GSM":
        hexStr += "2e " if not msg_raw_hex.startswith("2e") else ""
    if protocol == "5GMM":
        hexStr += "7e " if not msg_raw_hex.startswith("7e") else ""
    hexStr += msg_raw_hex
    hexStr = hexStr.split("\n")[0]
    print("text2pcap input content:", hexStr)

    tempName = uuid.uuid4().hex
    tempHexPath = os.path.join(azq_utils.tmp_gen_path(), tempName + ".txt")
    tempPcapPath = os.path.join(azq_utils.tmp_gen_path(), tempName + ".pcap")
    print("tempHexPath", tempHexPath)
    print("tempPcapPath", tempPcapPath)

    tempHexFile = open(tempHexPath, "w")
    tempHexFile.write(hexStr)
    tempHexFile.close()

    cmd = (text2pcapPath, '-l', '161', tempHexPath, tempPcapPath)
    print("text2pcap cmd:", cmd)

    cmdret = None
    if os.name == "nt":
        cmdret = subprocess.call(cmd, shell=False, env=env, creationflags=CREATE_NO_WINDOW)
    else:
        cmdret = subprocess.call(cmd, shell=False, env=env)
    print("text2pcap ret:", cmdret)

    if cmdret != 0:
        raise Exception("text2pcap failed - abort")

    channelType = None
    print("name %s type %s" % (name, type(name)))
    chan_type_regexs = [
    r"\((.*)\)",
    ]
    for ctr in chan_type_regexs:
        match = re.search(ctr, name)
        if match is not None:
            channelType = match.group(1)
            break
    if name.startswith("NR "):
        name_parts = name.split(" ")
        channelType = " ".join(name_parts[1:-1])
        #print("nr channeltype:", channelType)

    print("channelType", channelType)

    dissector = protocolToDissector(protocol, channelType)
    cmd = (
            tsharkPath,
            '-o',
            'uat:user_dlts:"User 14 (DLT=161)","{}","0","","0",""'.format(dissector),
            '-r',
            tempPcapPath,
            '-V'
    )
    print("tshark cmd:", cmd)
    decodeResult = None
    try:
        if os.name == "nt":
            decodeResult = subprocess.check_output(cmd, shell=False, env=env, creationflags=CREATE_NO_WINDOW)
        else:
            decodeResult = subprocess.check_output(cmd, shell=False, env=env)
        decodeResult = decodeResult.decode("utf-8")
    except subprocess.CalledProcessError as cpe:
        decodeResult = cpe.output.decode()

    # print("decodeResult", decodeResult)
    result = decodeResult
    if "DLT: 161," in result:
        result = result[result.index("DLT: 161,"):]
        result = result[result.index("\n"):]
    return result


def protocolToDissector(protocol, channelType):
    if protocol in ["RR", "MM", "CC", "GMM", "SM"]:
        return "gsm_a_dtap"
    elif protocol in ["EMM", "ESM"]:
        return "nas-eps_plain"
    elif protocol in ["RRC"]:
        assert channelType
        return "rrc." + str(getWcdmaSubdissector(channelType))
    elif protocol in ["ERRC"]:
        assert channelType
        return "lte_rrc." + str(getLteSubdissector(channelType))
    elif protocol in ["NR-RRC"]:
        assert channelType
        return "nr-rrc." + str(getNrSubdissector(channelType))
    elif protocol in ["5GMM", "5GSM"]:
        return "nas-5gs"  # https://www.wireshark.org/docs/dfref/#section_n >> nas-5gs
    raise Exception("unhandled/unknown protocl: {} chan: {}".format(protocol, channelType))


def getWcdmaSubdissector(channelType):
    if channelType in ["UL-CCCH"]:
        return "ul.ccch"
    elif channelType in ["UL-DCCH"]:
        return "ul.dcch"
    elif channelType in ["DL-CCCH"]:
        return "dl.ccch"
    elif channelType in ["DL-DCCH"]:
        return "dl.dcch"
    elif channelType in ["BCCH-BCH"]:
        return "bcch.bch"
    elif channelType in ["BCCH-FACH"]:
        return "bcch.fach"
    elif channelType in ["PCCH"]:
        return "pcch"
    elif channelType in ["MCCH"]:
        return "mcch"
    elif channelType in ["MSCH"]:
        return "msch"
    elif channelType in ["SysInfoType19"]:
        return "si.sib19"
    elif channelType in ["SysInfoType11bis"]:
        return "si.sib11bis"
    elif channelType in ["SysInfoType3", "SysInfoType5bis", "SysInfoType11"]:
        return "bcch.bch"
    return None


def getLteSubdissector(channelType):
    if channelType in ["BCCH-DL-SCH"]:
        return "bcch_dl_sch"
    elif channelType in ["PCCH"]:
        return "pcch"
    elif channelType in ["DL-CCCH"]:
        return "dl_ccch"
    elif channelType in ["DL-DCCH", "DL_DCCH"]:
        return "dl_dcch"
    elif channelType in ["UL-CCCH"]:
        return "ul_ccch"
    elif channelType in ["UL-DCCH"]:
        return "ul_dcch"
    elif channelType in ["V15_PDU_NUMBER_BCCH_DL_SCH_NB"]:
        return "bcch_dl_sch.nb"
    elif channelType in ["DL-CCCH-Message-NB"]:
        return "dl_ccch.nb"
    elif channelType in ["DL-DCCH-Message-NB"]:
        return "dl_dcch.nb"
    elif channelType in ["UL-CCCH-Message-NB"]:
        return "ul_ccch.nb"
    elif channelType in ["UL-DCCH-Message-NB"]:
        return "ul_dcch.nb"
    return None


NR_CHANTYPE_TO_SUBDISSECTOR_DICT = {
"BCCH BCH":"bcch.bch",
"BCCH DL SCH":"bcch.dl.sch",
"DL CCCH":"dl.ccch",
"DL DCCH":"dl.dcch",
"PCCH":"pcch",
"SBCCH SL BCH":"sbcch.sl.bch",
"SCCH":"scch",
"UL CCCH1":"ul.ccch1",
"UL CCCH":"ul.ccch",
"UL DCCH":"ul.dcch"
}


def getNrSubdissector(channelType):
    if channelType not in NR_CHANTYPE_TO_SUBDISSECTOR_DICT.keys():
        raise Exception("unhandled/unknown channeltype: {}".format(channelType))
    return NR_CHANTYPE_TO_SUBDISSECTOR_DICT[channelType]
