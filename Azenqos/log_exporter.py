from collections import OrderedDict
import pandas as pd

import preprocess_azm
import azq_theme_manager

def gen_distance_bin_agg_dict(df_all):
    distance_bin_agg_dict = OrderedDict()
    for col in df_all.columns:
        if col != "distance_bin_id" and col != "log_hash":
            if preprocess_azm.get_elm_info(col, filter_number_param=True) is not None and (not azq_theme_manager.is_param_col_an_id(col)) and df_all[col].dtype.kind in 'iufc':
                print("prepare col for mean agg distance bin:", col)
                df_all[col] = pd.to_numeric(df_all[col])
                distance_bin_agg_dict[
                    col] = "mean"  # do mean() for this known parameter column which is not an id parameter
            else:
                distance_bin_agg_dict[col] = "last"  # get last val for this column
    return distance_bin_agg_dict