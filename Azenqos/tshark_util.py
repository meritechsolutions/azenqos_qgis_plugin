import os
import uuid
import subprocess
import azq_utils


def tshark_decode_gsm_l3_ota_hexdump(hexdump):

    """

LTE Example
===========

Original azqdata.db > signalling.detail_hex:
46 0e f4 6c 80 c8

Original azqdata.db > signalling.detail_str:
LTE L3RRC SENT,"RRCConnectionRequest (UL-CCCH) (UL-CCCH-Message)
== extra_info: ==
rrc_ver: 0x720a
rb_id: 0
pci: 216
earfcn: 1275
sfn_info: 0x0000
pdu_type_number: 0x7
sib_mask: 0x0000
pdu_len: 6
=================
UL-CCCH-Message ::= {
    message: c1: rrcConnectionRequest: RRCConnectionRequest ::= {
        criticalExtensions: rrcConnectionRequest-r8: RRCConnectionRequest-r8-IEs ::= {
            ue-Identity: s-TMSI: S-TMSI ::= {
                mmec: 60
                m-TMSI: EF 46 C8 0C
            }
            establishmentCause: 4 (mo-Data)
            spare: '0'
        }
    }
}
HexDump: 46 0e f4 6c 80 c8 
"

msg_raw_hex: 46 0e f4 6c 80 c8 

Example decode detail_hex with tshark
-------------------------------------

kasidit@kasidit-thinkpad:~/tmp$ echo -n "000000 " > assign.txt
kasidit@kasidit-thinkpad:~/tmp$ echo "46 0e f4 6c 80 c8" >> assign.txt
kasidit@kasidit-thinkpad:~/tmp$ cat assign.txt 
000000 46 0e f4 6c 80 c8

kasidit@kasidit-thinkpad:~/tmp$ text2pcap -l 161 assign.txt assgn.pcap
Input from: assign.txt
Output to: assgn.pcap
Output format: pcap
Wrote packet of 6 bytes.
Read 1 potential packet, wrote 1 packet (46 bytes).

kasidit@kasidit-thinkpad:~/tmp$ tshark -o "uat:user_dlts:\"User 14 (DLT=161)\",\"lte_rrc.UL_CCCH\",\"0\",\"\",\"0\",\"\"" -r assgn.pcap -V
Frame 1: 6 bytes on wire (48 bits), 6 bytes captured (48 bits)
    Encapsulation type: USER 14 (59)
    Arrival Time: Jan 21, 2020 13:44:51.000000000 +07
    [Time shift for this packet: 0.000000000 seconds]
    Epoch Time: 1579589091.000000000 seconds
    [Time delta from previous captured frame: 0.000000000 seconds]
    [Time delta from previous displayed frame: 0.000000000 seconds]
    [Time since reference or first frame: 0.000000000 seconds]
    Frame Number: 1
    Frame Length: 6 bytes (48 bits)
    Capture Length: 6 bytes (48 bits)
    [Frame is marked: False]
    [Frame is ignored: False]
    [Protocols in frame: user_dlt:lte_rrc]
DLT: 161, Payload: lte_rrc.ul_ccch (LTE Radio Resource Control (RRC) protocol)
LTE Radio Resource Control (RRC) protocol
    UL-CCCH-Message
        message: c1 (0)
            c1: rrcConnectionRequest (1)
                rrcConnectionRequest
                    criticalExtensions: rrcConnectionRequest-r8 (0)
                        rrcConnectionRequest-r8
                            ue-Identity: s-TMSI (0)
                                s-TMSI
                                    mmec: 60 [bit length 8, 0110 0000 decimal value 96]
                                    m-TMSI: ef46c80c [bit length 32, 1110 1111  0100 0110  1100 1000  0000 1100 decimal value 4014393356]
                            establishmentCause: mo-Data (4)
                            spare: 00 [bit length 1, 7 LSB pad bits, 0... .... decimal value 0]

kasidit@kasidit-thinkpad:~/tmp$ 


---

GSM example
-----------

- create assgn.txt with format: 000000 <hex string with space in between>

text2pcap -l 161 assgn.txt assgn.pcap

tshark -o "uat:user_dlts:\"User 14 (DLT=161)\",\"gsm_a_dtap\",\"0\",\"\",\"0\",\"\"" -r assgn.pcap -V

text2pcap -l 161 tmp_prev.txt tmp_prev.pcap

tshark -o "uat:user_dlts:\"User 14 (DLT=161)\",\"gsm_a_dtap\",\"0\",\"\",\"0\",\"\"" -r tmp_prev.pcap -V
    """

    tmp_proc_dir = azq_utils.get_local_fp("tmp_tshark")
    if os.path.isdir(tmp_proc_dir):
        pass
    else:
        os.makedirs(tmp_proc_dir)
    tmpfn = os.path.join(tmp_proc_dir, "tmp_tshark_dec_" + str(uuid.uuid4()))
    tmp_txt_fp = tmpfn + ".txt"
    tmp_pcap_fp = tmpfn + ".pcap"

    with open(tmp_txt_fp, "wb") as tf:
        print("create tshark txt tmpfp: ", tmp_txt_fp)
        tf.write(("000000 " + hexdump).encode("ascii"))

    env = (
        prepare_env_and_libs()
    )  # call this only once at start of program! otherwise will be very slow extracting .so in gnu/linux everytime...

    # call text2pcap -l 161 assgn.txt assgn.pcap
    cmd = azq_utils.get_local_fp(
        os.path.join(
            "wireshark_" + os.name, "text2pcap" + ("" if os.name == "posix" else ".exe")
        )
    ) + ' -l 161 "{}" "{}"'.format(tmp_txt_fp, tmp_pcap_fp)
    print("text2pcap cmd:", cmd)
    cmdret = subprocess.call(cmd, shell=True, env=env)
    print("text2pcap ret:", cmdret)

    if cmdret != 0:
        print("text2pcap failed - abort")
    else:
        # tshark -o "uat:user_dlts:\"User 14 (DLT=161)\",\"gsm_a_dtap\",\"0\",\"\",\"0\",\"\"" -r assgn.pcap -V
        cmd = azq_utils.get_local_fp(
            os.path.join(
                "wireshark_" + os.name,
                "tshark" + ("" if os.name == "posix" else ".exe"),
            )
        ) + ' -o "uat:user_dlts:\\"User 14 (DLT=161)\\",\\"gsm_a_dtap\\",\\"0\\",\\"\\",\\"0\\",\\"\\"" -r {} -V'.format(
            tmp_pcap_fp
        )
        print("tshark cmd:", cmd)
        # cmdret = os.system(cmd)
        print("tshark cmd ret:", cmdret)
        ret = subprocess.check_output(cmd, shell=True, env=env)
        ret = ret.decode("ascii")
        return ret

    return None


g_extract_so_tar_gz_done = False
# call this only once at start of program! otherwise will be very slow extracting .so in gnu/linux everytime...
def prepare_env_and_libs():
    global g_extract_so_tar_gz_done

    env = os.environ.copy()
    ws_bin_dir = azq_utils.get_local_fp("wireshark_" + os.name)
    env["LD_LIBRARY_PATH"] = ws_bin_dir
    if os.name == "posix" and not g_extract_so_tar_gz_done:
        extract_so_ret = os.system(
            "tar -xzf {}/libwireshark.so.0.tar.gz -C {}".format(ws_bin_dir, ws_bin_dir)
        )
        print("extract_so_ret:", extract_so_ret)
        g_extract_so_tar_gz_done = True
    return env
