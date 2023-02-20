import tshark_util


def test():
    ret = tshark_util.tshark_decode_hex("recv", "PDU Session Modification Command", "5GSM", '''
                msg_raw_hex: 02 00 CB 7A 00 04 02 00 01 40 

                ''')
    print("5gsm ret:", ret)
    assert "QoS rule identifier: 2" in ret

    ret = tshark_util.tshark_decode_hex("recv", "DL NAS Transport", "5GMM", '''
                    msg_raw_hex: 00 68 01 00 0B 2E 02 00 CB 7A 00 04 02 00 01 40 12 02
                    ''')
    print("5gsm ret:", ret)
    assert "QoS rule identifier: 2" in ret

    ret = tshark_util.tshark_decode_hex("send", "NR UL DCCH MeasurementReport", "NR-RRC", '''
    msg_raw_hex: 00 01 00 05 2B 5D 9C A7 E0
    ''')
    print("ret:", ret)
    assert "measurementReport" in ret

    ret = tshark_util.tshark_decode_hex("recv", "NR DL DCCH RrcReconfiguration", "NR-RRC", '''
        msg_raw_hex: 00 21 52 04 58 00 50 40 5A AA 78 01 A0 01 41 03 90 91 E0 01 1E 00 1C 90 CC 3A 14 07 E6 00 82 00 37 0A 02 38 04 48 A3 94 30 E5 80 44 02 06 C0 16 80
        ''')
    print("ret:", ret)
    assert "rrcReconfiguration" in ret

    ret = tshark_util.tshark_decode_hex("recv", "NR BCCH BCH Mib", "NR-RRC", '''
            msg_raw_hex: 2D 25 25 E0
            ''')
    print("ret:", ret)
    assert " mib " in ret

    ret = tshark_util.tshark_decode_hex("recv", "NR BCCH DL SCH SystemInformationBlockType1", "NR-RRC", '''
                msg_raw_hex: 7C 80 0C 02 0A 90 00 D7 80 46 05 A5 E3 4F BB 00 80 48 10 00 60 86 05 58 41 40 62 00 00 15 0B 19 69 9A FE 91 DC 10 08 00 00 88 A0 FC 80 85 40 02 00 00 22 28 00 20 10 6D 0A 06 C4 42 91 80 C6 55 23 8E 45 61 D0 C7 20 08 10 00 01 50 F0 E3 2D 33 28 08 80 3A 66 6A EB C0 06 62 7F 83 37 0A 6E 1C DC 49 B8 B3 71 E6 E4 4D C2 A9 85 A7 0E A6 1E 9C 4A 98 9A 71 6A 62 E9 C9 9B B0 17 C1 45 66 EB FD 05 80 EC 02 49 EA 6E 62 80 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
                ''')
    print("ret:", ret)
    assert " systemInformationBlockType1 " in ret

    ret = tshark_util.tshark_decode_hex("send", "NR UL CCCH RrcSetupRequest", "NR-RRC", '''
                    msg_raw_hex: 00 25 09 AC EC 08
                    ''')
    print("ret:", ret)
    assert " rrcSetupRequest " in ret

    ret = tshark_util.tshark_decode_hex("recv", "NR DL CCCH RrcSetup", "NR-RRC", '''
                        msg_raw_hex: 20 40 20 C7 01 18 B8 01 60 02 1E F5 F9 00 20 CB D8 00 F8 44 60 82 0F 38 08 41 AC 59 70 24 98 19 50 01 1F FF F8 00 00 00 17 57 78 EE 10 04 00 00 44 50 6E 28 84 00 02 48 AC 84 08 09 64 04 AC 04 AD D0 A0 6C 44 29 18 0C 65 52 38 E4 56 1D 00 99 A8 82 48 0C 81 9C 04 42 80 0C 0A 20 86 45 67 8B C1 84 67 3C 8E 92 68 29 34 10 80 0C 10 AC E2 4D C5 9B 8D 37 1E 6F 1F FA 8C 65 29 4A 25 03 80 00 43 60 00 00 08 00 00 00 CA 11 73 52 B1 08 AC 00 04 C0
                        ''')
    print("ret:", ret)
    assert " rrcSetup " in ret
    
    ret = tshark_util.tshark_decode_hex("recv", "RRCConnectionReconfigurationComplete (UL-DCCH)", "ERRC", '''
    msg_raw_hex: 12 00
    ''')
    print("ret:", ret)
    assert "LTE Radio Resource Control (RRC) protocol" in ret

    ret = tshark_util.tshark_decode_hex("recv", "Security Mode Complete", "5GMM", '''
        msg_raw_hex: 7e 00 5d 22 01 02 f0 70 e1 36 01 02
        ''')
    print("5gmm ret:", ret)




if __name__ == "__main__":
    test()
