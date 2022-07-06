import azq_utils
import analyzer_vars
import os


def test():    
    vv = analyzer_vars.analyzer_vars()
    vv.delete_preferences()
    assert False == os.path.isfile(azq_utils.get_settings_fp("preferences.ini"))
    vv.load_preferences()
    assert "15000" == vv.pref["spider_match_max_distance_meters"]
    vv.pref["spider_match_max_distance_meters"] = "500"
    vv.save_preferences()
    assert True == os.path.isfile(azq_utils.get_settings_fp("preferences.ini"))
    assert "500" == analyzer_vars.analyzer_vars().pref["spider_match_max_distance_meters"]
    vv.load_preferences()
    assert "500" == analyzer_vars.analyzer_vars().pref["spider_match_max_distance_meters"]
    vv.delete_preferences()
    assert False == os.path.isfile(azq_utils.get_settings_fp("preferences.ini"))
    vv.load_preferences()
    print("post del:", vv.pref["spider_match_max_distance_meters"])
    assert "15000" == vv.pref["spider_match_max_distance_meters"]
    assert "15000" == analyzer_vars.analyzer_vars().pref["spider_match_max_distance_meters"]
    vv.save_preferences()


if __name__ == "__main__":
    test()
