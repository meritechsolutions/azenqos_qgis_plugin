import azq_utils

def test():
    ts0 = azq_utils.datetimeStringtoTimestamp("2021-04-22 15:22:18.000")
    print("ts: {}".format(ts0))
    ts1 = azq_utils.datetimeStringtoTimestamp("2021-04-22 15:22:18")
    print("ts: {}".format(ts1))
    assert ts0 is not None
    assert abs(ts0 - ts1) < 0.1

if __name__ == "__main__":
    test()
