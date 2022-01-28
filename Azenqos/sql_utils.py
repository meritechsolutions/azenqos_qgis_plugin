import pandas as pd
import traceback
import sys


LOG_HASH_TIME_MATCH_EVAL_STR_EXAMPLE_PREFIX = '''pd.read_sql(
'''

LOG_HASH_TIME_MATCH_EVAL_STR_EXAMPLE_SELECT_FROM_PART = '''
select log_hash, time,
exynos_basic_info_nr_mode_sa as 'SA Status',
exynos_basic_info_nr_endc_status as 'NSA ENDC Status',
exynos_basic_info_nr_band as 'NR Band',
exynos_basic_info_nr_arfcn as 'NR ARFCN',
exynos_basic_info_nr_pci as 'NR PCI',
exynos_basic_info_nr_ch_bw as 'NR Bandwidth (MHz)'
from exynos_basic_info_nr
'''

LOG_HASH_TIME_MATCH_DEFAULT_WHERE_PART = '''
where {log_hash_filt_part} time between DATETIME('{time}','-5 seconds') and '{time}'
'''

LOG_HASH_TIME_MATCH_EVAL_STR_EXAMPLE_SUFFIX = '''.format(
log_hash_filt_part='log_hash = {} and '.format(log_hash) if log_hash is not None else '',
time=time),
dbcon).transpose().reset_index()
'''

def add_first_where_filt(sqlstr, where):
    if where is not None and len(where) > 0:
        where = where.replace("==","=")
        order_by_suffix = None
        group_by_suffix = None
        limit_suffix = None
        try:
            obp = sqlstr.split("group by")
            group_by_suffix = obp[1]            
            sqlstr = obp[0]
            try:
                obp = group_by_suffix.split("order by")
                order_by_suffix = obp[1]            
                group_by_suffix = obp[0]
                try:
                    obp = order_by_suffix.split("limit")
                    limit_suffix = obp[1]            
                    order_by_suffix = obp[0]
                except:
                    pass
            except:
                pass
        except:
            pass
        
        try:
            obp = sqlstr.split("order by")
            order_by_suffix = obp[1]            
            sqlstr = obp[0]
            try:
                obp = order_by_suffix.split("limit")
                limit_suffix = obp[1]            
                order_by_suffix = obp[0]
            except:
                pass
        except:
            pass

        try:
            obp = sqlstr.split("limit")
            limit_suffix = obp[1]            
            sqlstr = obp[0]
        except:
            pass

        filt_part = where
        if "where " in filt_part:
            filt_part = " " + where.replace("where ", "( ", 1) + " )"

        if "where " in sqlstr:
            sqlstr = sqlstr.replace("where", "where " + filt_part + " and ", 1)
        else:
            sqlstr += " where " + filt_part

        if order_by_suffix is not None:
            sqlstr += " order by "+order_by_suffix

        if group_by_suffix is not None:
            sqlstr += " group by "+group_by_suffix

        if limit_suffix is not None:
            sqlstr += " limit "+limit_suffix
    return sqlstr

def get_ex_eval_str_for_select_from_part(select_from_part):
    return LOG_HASH_TIME_MATCH_EVAL_STR_EXAMPLE_PREFIX+'"""'+\
    select_from_part+\
    LOG_HASH_TIME_MATCH_DEFAULT_WHERE_PART+'"""'+\
    LOG_HASH_TIME_MATCH_EVAL_STR_EXAMPLE_SUFFIX


def sql_lh_time_match_for_select_from_part(select_from_part, log_hash, time):
    return select_from_part+LOG_HASH_TIME_MATCH_DEFAULT_WHERE_PART.format(
        log_hash_filt_part='log_hash = {} and '.format(log_hash) if log_hash is not None else '',
        time=time
    )


def get_lh_time_match_df(dbcon, sql, col_name=None, trasposed=True):
    print(sql)
    try:
        df = pd.read_sql(sql, dbcon)
        if len(df) > 0:
            if df.last_valid_index() is not None:
                last_valid_each_col = df.apply(pd.Series.last_valid_index)
                valid_df_dict = {}
                for index, value in last_valid_each_col.items():
                    value_index = 0
                    if not pd.isna(value):
                        value_index = int(value)
                    valid_df_dict[index] = df[index][value_index]
                df = pd.DataFrame.from_dict(valid_df_dict, orient='index').T
            else:
                df = df.iloc[[0]].reset_index(drop=True)

        if trasposed:
            if len(df) == 0:
                df.loc[0] = None  # add new row so wont be empty df when transpose (otherwise datatable.py show would be different n columns and wont get refreshed when n columns increased)
            df = df.T.reset_index()  # pop out as column
            if col_name is not None:
                df = df.rename(columns={df.columns[1]: col_name})
        return df
    except Exception:
        type_, value_, traceback_ = sys.exc_info()
        exstr = str(traceback.format_exception(type_, value_, traceback_))
        print(
            "WARNING: exception invalid sql:"
            + exstr
        )
        return


def get_lh_time_match_df_for_select_from_part(dbcon, select_from_part, log_hash, time, col_name=None, trasposed=True, selected_log=None):
    if selected_log:
        log_hash = selected_log
    sql = sql_lh_time_match_for_select_from_part(select_from_part, log_hash, time)
    return get_lh_time_match_df(dbcon, sql, col_name=col_name, trasposed=trasposed)


def is_sql_select(eval_str):
    return eval_str.strip().lower().strip().startswith("select")