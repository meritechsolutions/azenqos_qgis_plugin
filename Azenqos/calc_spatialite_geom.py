import numpy as np
import os


"""
spatialite_blob_header_len = 43;
spatialite_blob_point_payload_len = 16;
spatialite_blob_point_blob_len = spatialite_blob_header_len + spatialite_blob_point_payload_len + 1  # end flag 0xfe
"""
spatialite_blob_template_fp = os.path.join(
    os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__))
    ),
    "test_spatialite_geom_target0"
)
spatialite_blob_template_blob = None

try:
    spatialite_blob_template_blob = np.fromfile(spatialite_blob_template_fp, dtype=np.uint8)
except Exception as e:
    print("WARNING: spatialite_blob_template_blob read exception:", e)
    
def calc_spatialite_geom_for_lat_lon(row, lat_bytes=None, lon_bytes=None):

    if row is not None:
        lat_bytes = np.frombuffer(np.array([row.lat], dtype=np.double).tobytes(),dtype=np.uint8)
        #lat_bytes = np.frombuffer(struct.pack('d',row.positioning_lat), dtype=np.uint8)
        lon_bytes = np.frombuffer(np.array([row.lon], dtype=np.double).tobytes(),dtype=np.uint8)
        #lon_bytes = np.frombuffer(struct.pack('d',row.positioning_lon), dtype=np.uint8)

    buf = np.copy(spatialite_blob_template_blob).astype(dtype=np.uint8)
    buf[6:14] = lon_bytes  # min x
    buf[14:22] = lat_bytes  # min y
    buf[22:30] = lon_bytes  # max x
    buf[30:38] = lat_bytes  # max y

    buf[43:51] = lon_bytes  # x
    buf[51:59] = lat_bytes  # y

    
    return buf.tobytes()


    """
    my previous java code in UpdateCenter.java:

    public byte[] get_geom_from_lat_lon()
    {

        //see spatialite 'world.7z' example - Cities > Geometry column blob

        if (!UpdateCenter.prev_loc_valid)
            return null;

        double lat = UpdateCenter.prev_lat;
        double lon = UpdateCenter.prev_lon;

        byte[] ret = new byte[spatialite_blob_point_blob_len];

        //start
        ret[0] = 0;

        //endian: 1 = little
        ret[1] = 1;

        //srid: WGS84 ; SRID 4326 = hex 0x10E6
        ret[2] = (byte) 0xe6;
        ret[3] = (byte) 0x10;
        ret[4] = 0;
        ret[5] = 0;

        byte[] bx = toByteArray(lon);
        byte[] by = toByteArray(lat);

        //mbr min x

        System.arraycopy(bx,0,ret,6,8);

        //mbr min y
        System.arraycopy(by,0,ret,14,8);

        //mbr max x
        System.arraycopy(bx,0,ret,22,8);

        //mbr max y
        System.arraycopy(by,0,ret,30,8);

        //mbr end flag
        ret[38] = 0x7c;

        //class
        ret[39] = 1; //point
        ret[40] = 0;
        ret[41] = 0;
        ret[42] = 0;

        //payload

        //point

        //point - x double 8 byte >> lon [43 - 50]
        System.arraycopy(bx,0,ret,43,8);

        //point - y double 8 byte >> lat [51 - 58]
        System.arraycopy(by,0,ret,51,8);

        //end flag
        ret[59] = (byte) 0xfe;

        return ret;
    }
    """
