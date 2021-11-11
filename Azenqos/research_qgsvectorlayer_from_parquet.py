import pandas as pd
from qgis.PyQt.QtCore import QVariant
from qgis._core import QgsProject
from qgis.core import QgsVectorLayer, QgsFeature, QgsField

import azq_utils
import qgis_layers_gen


def test():
    return # all methods too slow or too much ram, stick to existing spatialite method
    azq_utils.timer_start("read pq df")
    cols = ["geom", "lat", "lon", "lte_inst_rsrp_1"]
    df = pd.read_parquet("/home/kasidit/data/overview_db_optimize/tmp_overview_2021_00_bin_1_logs_26706.db_table_lte_cell_meas.parquet_dump", columns=cols)
    azq_utils.timer_print("read pq df")

    azq_utils.timer_start("dump to spatialite")
    qgis_layers_gen.dump_df_to_spatialite_db(df, "o.db", "lte_cell_meas")
    azq_utils.timer_print("dump to spatialite")

    return # too slow
    azq_utils.timer_start("conv to geopd")
    df.to_csv("tmp.csv")
    azq_utils.timer_print("conv to geopd")

    return # too slow, too much ram
    # Creation of my QgsVectorLayer with no geometry
    temp = QgsVectorLayer("none", "result", "memory")
    #temp_data = temp.dataProvider()
    # Start of the edition
    temp.startEditing()

    # Creation of my fields
    for col in cols:
        f = QgsField(col, QVariant.Double) if col.endswith("rsrp_1") else QgsField(col, QVariant.Int)
        temp.addAttribute(f)
    # Update
    temp.updateFields()

    # Addition of features
    # [1] because i don't want the indexes
    azq_utils.timer_start("add attribs")
    for row in df.itertuples():
        f = QgsFeature()
        f.setAttributes([row[1], row[2], row[3]])
        temp.addFeature(f)
    azq_utils.timer_print("add attribs")
    # saving changes and adding the layer
    azq_utils.timer_start("commit")
    temp.commitChanges()
    azq_utils.timer_print("commit")
    QgsProject.instance().addMapLayer(temp)


if __name__ == "__main__":
    test()
