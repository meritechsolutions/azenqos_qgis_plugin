import azq_theme_manager
import sys
import traceback


def prepare_spatialite_views(dbcon):
    assert dbcon is not None

    ### we will make views one per param so drop all existing tables from geom_columns
    dbcon.execute(''' delete from geometry_columns where f_table_name not in ('events','signalling'); ''')

    ### create views one per param as specified in default_theme.xml file
    # get list of params in azenqos theme xml
    params_to_gen = azq_theme_manager.get_matching_col_names_list_from_theme_rgs_elm()
    print("params_to_gen:", params_to_gen)
    import preprocess_azm

    for param in params_to_gen:
        try:
            print("create view for param %s" % param)
            table = preprocess_azm.get_table_for_column(param)
            assert table
            view = param
            sqlstr = "create table {col} as select log_hash, time, modem_time, posid, seqid, netid, geom, {col} from {table} ;".format(col=view, table=table)
            print("create view sqlstr: %s" % sqlstr)
            dbcon.execute(sqlstr)
            sqlstr = '''insert into geometry_columns values ('{}', 'geom', 'POINT', '2', 4326, 0);'''.format(view)
            dbcon.execute(sqlstr)
            dbcon.commit()
            print("create view success")
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print("WARNING: prepare_spatialte_views exception:", exstr)

    # create layer_styles table (drop existing first)

    ## for each param
    # create view for param
    # put param view into geometry_columns to register for display
    # create param QML theme based on default_style.qml
    # put qml entry into 'layer_styles' table
    
    '''
drop view lte_inst_rsrp_1;
create view lte_inst_rsrp_1 as select log_hash, time, geom, lte_inst_rsrp_1 from lte_cell_meas;
delete from geometry_columns where f_table_name not in ('events','signalling');
insert into geometry_columns values ('lte_inst_rsrp_1', 'geom', 'POINT', '2', 4326, 0);
    '''
