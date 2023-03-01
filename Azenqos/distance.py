
import numpy as np
import dprint
from collections import OrderedDict


# vectorized haversine function
# https://stackoverflow.com/questions/29545704/fast-haversine-approximation-python-pandas/29546836#29546836
def haversine_np(lat1, lon1, lat2, lon2, meters=True, earth_radius=6371):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)

    All args must be of equal length.    

    """
    lon1, lat1, lon2, lat2 = list(map(np.radians, [lon1, lat1, lon2, lat2]))

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2

    c = 2 * np.arcsin(np.sqrt(a))
    km = earth_radius * c
    if meters:
        return km*1000.0
    return km


def df_add_distance_meters(df, lat_col, lon_col):
    df = df.sort_values(["log_hash", "time"])
    df["prev_lat"] = df[lat_col].shift(1)
    df["prev_lon"] = df[lon_col].shift(1)
    df["distance"] = np.nan
    df = df.groupby("log_hash").apply(lambda lhdf: per_one_log_hash_only_add_distance(lhdf, lat_col, lon_col, "prev_lat", "prev_lon"))
    del df["prev_lat"]
    del df["prev_lon"]    
    return df


def per_one_log_hash_only_add_distance(df, lat_col, lon_col, prev_lat_col, prev_lon_col):
    df["distance"] = haversine_np(df[lat_col], df[lon_col], df[prev_lat_col], df[prev_lon_col])
    return df


def df_add_distance_bin_id(df, bin_meters):
    df["distance_cumsum"] = df.distance.cumsum()
    df["distance_bin_id"] = np.floor(df["distance_cumsum"] / bin_meters)
    return df


def df_distance_bin_meters(df, lat_col, lon_col, meters, agg_dict=None, keep_new_cols=True):

    # add distance from prev row
    if dprint.debug_file_flag:
        df.to_csv("tmp/dbdf0.csv")

    df = df_add_distance_meters(df, lat_col, lon_col)

    if dprint.debug_file_flag:
        df.to_csv("tmp/dbdf1.csv")
        
    #print("add distance meters df.head()\n", df.head(20))

    df = df_add_distance_bin_id(df, meters)

    if dprint.debug_file_flag:
        df.to_csv("tmp/dbdf2.csv")
        
    #print("add distance bin id df.head()\n", df.head(20))
    
    del df["distance"]  # rm distance col as "last" can be zero and cause confusion

    print("df_distance_bin_meters: agg_dict:", agg_dict)
    if agg_dict is None:
        agg_dict = OrderedDict()
        for col in df.columns:
            if col != "distance_bin_id" and col != "log_hash":
                agg_dict[col] = "last"
    agg_dict["distance_cumsum"] = "last"  # in case not provided in agg_dict
    agg_dict[lat_col] = "last"
    agg_dict[lon_col] = "last"
    agg_dict["time"] = "last"
    print("df distance agg_dict:", agg_dict)
    print("df distance bin pre gb cols:", df.columns)
    df = df.copy().groupby(["log_hash","distance_bin_id"]).agg(agg_dict).reset_index() # pop out groupby indices
    print("df distance bin post gb cols:", df.columns)
    
    if not keep_new_cols:
        del df["distance_bin_id"]
        del df["distance_cumsum"]

    if dprint.debug_file_flag:
        df.to_csv("tmp/dbdf3.csv")

    return df