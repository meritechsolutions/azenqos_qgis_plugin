import tshark_util


def test():
    hexdump = "06 2b a7 56 13 e2 56 63 00 63 41 91 03 06 20 1d 17 37 12 04 "
    ret = tshark_util.tshark_decode_hex("recv", "", "RR", "msg_raw_hex: "+hexdump)
    print("dec gsm ho ret:", ret)
    assert "Handover Command" in ret

    # call again, must not re-extract so from tar gz
    ret = tshark_util.tshark_decode_hex("recv", "", "RR", "msg_raw_hex: "+hexdump)
    print("dec gsm ho ret2:", ret)
    assert "Handover Command" in ret


if __name__ == "__main__":
    test()
