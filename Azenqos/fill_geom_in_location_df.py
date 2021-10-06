import numpy as np
import pandas as pd
import calc_spatialite_geom


def fill_geom_in_location_df(dat_location_df, per_row_calc_mode=False):

    dat_location_df = dat_location_df.copy()
    if per_row_calc_mode:
        #dat_location_df.to_csv("dat_location_df_pre_geom.csv")
        aret = dat_location_df.apply(calc_spatialite_geom.calc_spatialite_geom_for_lat_lon, axis=1)
        dat_location_df["geom"] = aret
        return dat_location_df
    else:
        nrows = len(dat_location_df)
        dat_location_df["lat"] = dat_location_df["lat"].astype(np.double)
        dat_location_df["lon"] = dat_location_df["lon"].astype(np.double)

        if nrows > 0:
            lat_bytes = dat_location_df.lat.values.tobytes()
            lon_bytes = dat_location_df.lon.values.tobytes()
            #print "lon_bytes len:", len(lon_bytes)
            lat_barray = np.frombuffer(lat_bytes, dtype=np.uint8)
            lon_barray = np.frombuffer(lon_bytes, dtype=np.uint8)
            #print "lon_barray len:", len(lon_barray)
            lat_array = np.split(lat_barray, nrows)
            lon_array = np.split(lon_barray, nrows)

            geom_header = np.array(calc_spatialite_geom.spatialite_blob_template_blob[0:6], dtype=np.uint8)
            geom_middle = np.array(calc_spatialite_geom.spatialite_blob_template_blob[38:43], dtype=np.uint8)
            geom_footer = np.array(calc_spatialite_geom.spatialite_blob_template_blob[59:60], dtype=np.uint8)  # 0xfe end flag
            #print "geom_middle", geom_middle
            #print "geom_footer", geom_footer

            geom_header_len = len(geom_header)
            geom_middle_len = len(geom_middle)
            geom_footer_len = len(geom_footer)
            ##print "geom_header_len:", geom_header_len
            #print "geom_footer_len:", geom_footer_len

            geom_header_array = np.broadcast_to(geom_header, (nrows, geom_header_len))
            geom_middle_array = np.broadcast_to(geom_middle, (nrows, geom_middle_len))     
            geom_footer_array = np.broadcast_to(geom_footer, (nrows, geom_footer_len))    

            #print "lat_array:", lat_array
            #print "lon_array:", lon_array[0:5]
            #print "geom_header_array:", geom_header_array
            #print "geom_footer_array:", geom_footer_array

            geom_array = np.concatenate([geom_header_array, lon_array, lat_array, lon_array, lat_array, geom_middle_array, lon_array, lat_array, geom_footer_array], axis=1)
            #print "len geom_array:", len(geom_array)
            #print "len dat_location_df:", len(dat_location_df)

            gseries = pd.Series(geom_array.tolist())
            #print "gseries:", gseries
            #print "len gseries:", len(gseries)
            #print "len dat_location_df:", len(dat_location_df)
            dat_location_df["geom"] = gseries.apply(to_bytes_buffer)
        else:
            dat_location_df["geom"] = None

        #print "len dat_location_df post:", len(dat_location_df)


        #print 'dat_location_df.head()', dat_location_df.geom.head()
        #print 'dat_location_df.tail()', dat_location_df.geom.tail()
        #print "gseries[-1]:", gseries.iloc[-1]
        #print "len dat_location_df post2:", len(dat_location_df)
        return dat_location_df


def to_bytes_buffer(val):
    #print "val:", val
    #print "type:", type(val)
    ret = np.array(val, dtype=np.uint8).tobytes()
    #print "tb ret:", ret
    return memoryview(ret)

