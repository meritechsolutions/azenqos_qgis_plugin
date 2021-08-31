import sqlite3
import gsm_query
import integration_test_helpers
import tshark_util


def test():
    ret = tshark_util.tshark_decode_hex("recv", "RRCConnectionReconfigurationComplete (UL-DCCH)", "ERRC", '''HexDump: 12 00 
"

msg_raw_hex: 12 00 ''')
    print("ret:", ret)
    assert "LTE Radio Resource Control (RRC) protocol" in ret


if __name__ == "__main__":
    test()
