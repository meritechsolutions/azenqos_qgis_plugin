import pandas as pd
import os
import re

def get_voice_call_setup_df(pre_wav_file_list):
    pre_wav_file_df = pd.DataFrame(columns=["log_hash", "time", "name", "info", "detail", "wave_file"])
    for pre_wav_file in pre_wav_file_list:
        name = "voice call setup"
        log_hash  = os.path.basename(os.path.dirname(pre_wav_file))
        wave_file_name = os.path.basename(pre_wav_file)
        time_str = get_time_from_pre_wave_name(wave_file_name)
        pre_wav_file_dict = {"log_hash":log_hash, "time":time_str, "name":name, "info":None, "detail":None, "wave_file":wave_file_name}
        pre_wav_file_df = pre_wav_file_df.append(pre_wav_file_dict, ignore_index = True)
        
    pre_wav_file_df["time"] = pd.to_datetime(pre_wav_file_df["time"], format='%Y%m%d_%H%M%S%f')
    return pre_wav_file_df

def get_time_from_pre_wave_name(pre_wave_name):
    time_str = re.findall("(\d+_\d+)_pre.wav", pre_wave_name)[0]+"100"
    print("sss", time_str)
    return time_str

pre_wav_file_list = ['C:\\Users\\vuttichai\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\Azenqos\\tmp_gen\\24620\\0a70c7bb-76e1-4bb1-8deb-1ea517d3914d\\1080373697536914164\\rxvoc_103_20220418_121122_20220418_121125_pre.wav', 'C:\\Users\\vuttichai\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\Azenqos\\tmp_gen\\24620\\0a70c7bb-76e1-4bb1-8deb-1ea517d3914d\\1080373697536914164\\rxvoc_103_20220418_121219_20220418_121222_pre.wav', 'C:\\Users\\vuttichai\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\Azenqos\\tmp_gen\\24620\\0a70c7bb-76e1-4bb1-8deb-1ea517d3914d\\1080373697536914164\\rxvoc_103_20220418_121316_20220418_121319_pre.wav', 'C:\\Users\\vuttichai\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\Azenqos\\tmp_gen\\24620\\0a70c7bb-76e1-4bb1-8deb-1ea517d3914d\\1080373697536914164\\rxvoc_103_20220418_121413_20220418_121417_pre.wav', 'C:\\Users\\vuttichai\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\Azenqos\\tmp_gen\\24620\\0a70c7bb-76e1-4bb1-8deb-1ea517d3914d\\1080373697536914164\\rxvoc_103_20220418_121510_20220418_121514_pre.wav']
test = get_voice_call_setup_df(pre_wav_file_list)
print("test", test)