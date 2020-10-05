from matplotlib.path import Path
import matplotlib.patches as patches

from dprint import dprint
import math
import pandas as pd
import json
import numpy as np
from pandas.io.json import json_normalize
import sys
import traceback
import os

import azq_utils as utils
import plot_param_zorders


CELL_FILE_RATS = ["nr", "lte", "wcdma", "gsm"]

g_cell_fp_dict = dict.fromkeys(CELL_FILE_RATS)
g_theme_dict = dict.fromkeys(CELL_FILE_RATS)

CELL_FILE_REQUIRED_COLUMNS = ["dir", "lat", "lon", "ant_bw"]
CELL_FILE_NUMERIC_COLUMNS = ["dir", "lat", "lon", "ant_bw", "pci", "psc", "bcch"]

# extra main/required cell column in cellfile for each rat, used to draw/match cell too
g_main_cell_col = dict.fromkeys(CELL_FILE_RATS)
g_main_cell_col["nr"] = "pci"
g_main_cell_col["lte"] = "pci"
g_main_cell_col["wcdma"] = "psc"
g_main_cell_col["gsm"] = "bcch"

g_detail_label_format_dict = dict.fromkeys(CELL_FILE_RATS)
for rat in CELL_FILE_RATS:
    g_detail_label_format_dict[rat] = "#" + g_main_cell_col[rat].upper()

LOG_PARAMS_FOR_CELL_THEME_POPULATE = {
    "nr": ["nr_servingbeam_pci"],
    "lte": ["lte_physical_cell_id", "scan_lte_ch_topn_result_cell_pci"],
    "wcdma": ["wcdma_sc", "wcdma_aset_sc", "scan_wcdma_ch_topn_result_cell_sc"],
    "gsm": ["gsm_arfcn_bcch", "scan_gsm_blind_result_ch_arfcn"],
}


def prepopulate_cell_themes_for_rats_that_have_cellfiles(dbcon):
    global g_cell_fp_dict
    import azq_theme_manager

    for rat in CELL_FILE_RATS:
        try:
            # do all - in case of in-azm cell file - if g_cell_fp_dict[rat] is not None:
            params = LOG_PARAMS_FOR_CELL_THEME_POPULATE[rat]
            for param in params:
                print("prepopulate_cell_themes: got theme for param:", param, "start")
                theme = azq_theme_manager.get_theme_df_for_column(param, dbcon=dbcon)
                if theme is None:
                    print(
                        "prepopulate_cell_themes: got theme for param:",
                        param,
                        "got None theme so skip",
                    )
                    continue
                if "match_value" not in theme.columns and "Lower" in theme.columns:
                    theme["match_value"] = theme["Lower"]
                try:
                    theme["match_value"] = pd.to_numeric(theme["match_value"])
                except:
                    pass
                print(
                    "prepopulate_cell_themes: got theme for param:", param
                )  # , "theme:", theme
                set_theme(rat, theme)
                print(
                    "prepopulate_cell_themes_for_rats_that_have_cellfiles: set_theme done for param:",
                    param,
                )
        except Exception:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print(
                "WARNING: exception in prepopulate_cell_themes_for_rats_that_have_cellfiles(dbcon):"
                + exstr
            )


def get_cell_fp(rat):
    global g_cell_fp_dict
    return g_cell_fp_dict[rat]


def set_cell_fp(rat, cfp, raise_exception_if_check_failed=False):
    global g_cell_fp_dict

    print(
        "set_cell_fp: raise_exception_if_check_failed: {}".format(
            raise_exception_if_check_failed
        )
    )

    # test parse if cellfile is valid or not - raise exception here
    get_cell_file_df(
        cfp,
        [g_main_cell_col[rat]],
        raise_exception_if_check_failed=raise_exception_if_check_failed,
    )

    g_cell_fp_dict[rat] = cfp


def set_detail_label_format(rat, format_str):
    global g_detail_label_format_dict
    g_detail_label_format_dict[rat] = format_str


def get_detail_label_format(rat):
    global g_detail_label_format_dict
    return g_detail_label_format_dict[rat]


def set_theme(rat, df):
    global g_theme_dict

    if df is None:
        return

    if "Lower" in df.columns:
        if "match_value" not in df.columns:
            print("azq_cell_file set_theme create match_value col from Lower col")
            df["match_value"] = df["Lower"]
            try:
                df["match_value"] = pd.to_numeric(df["match_value"])
            except:
                pass

    if g_theme_dict[rat] is None:
        g_theme_dict[rat] = df
    else:
        print("azq_cell_file.set_theme: prev not none so pd.concat - prev df\n:", df)
        print("match_value type pre concat:", df.match_value.dtype)
        cdf = pd.concat([g_theme_dict[rat], df], ignore_index=True)
        try:
            print("match_value type after concat:", cdf.match_value.dtype)
            df["match_value"] = pd.to_numeric(df["match_value"])
        except Exception as ex:
            print(
                "WARNING: azq_cell_file.set_theme convert match_value to numer failed exception:",
                ex,
            )
        cdf.drop_duplicates(subset="match_value", inplace=True, keep="last")
        print("azq_cell_file.set_theme: prev not none - new combined df\n:", cdf)
        print("match_value type final:", cdf.match_value.dtype)
        g_theme_dict[rat] = cdf


def get_theme(rat):
    global g_theme_dict
    return g_theme_dict[rat]


def clear_site_location():
    pass
    # site_location = []


def calculate_point_with_degree_from_y_axis(
    x_origin, y_origin, degree, cell_arm_length=70
):
    factor = 200
    if 90 < degree <= 270:
        factor = factor * -1
        utils.warn("factor * -1")
    x_target = x_origin + (math.tan(math.radians(float(degree))) * factor)
    y_target = y_origin - factor
    # utils.warn("cal target before resize:"+ str(x_target)+","+str(y_target))
    return resize_line_length(
        x_origin, y_origin, x_target, y_target, new_length=cell_arm_length
    )


def resize_line_length(x_origin, y_origin, x_target, y_target, new_length=70):
    # utils.debug("origin :"+str(x_origin) +", "+str(y_origin))
    # utils.debug("target :" + str(x_target) + ", " + str(y_target))
    delta_y = y_target - y_origin
    delta_x = x_target - x_origin
    if delta_y == 0:
        if x_origin < x_target:
            return (x_origin + new_length, y_origin)
        else:
            return (x_origin - new_length, y_origin)
    if delta_x == 0:
        if y_origin < y_target:
            return (x_origin, y_origin + new_length)
        else:
            return (x_origin, y_origin - new_length)
    slove = delta_y / delta_x
    # line_length = math.sqrt((delta_x*delta_x)+(delta_y*delta_y))
    # utils.debug("slove :"+str(slove)+"   line length:"+str(line_length))
    new_delta_x = math.sqrt((new_length * new_length) / ((slove * slove) + 1))
    new_delta_y = slove * new_delta_x
    # utils.debug("new slove :" + str(new_delta_y/new_delta_x))

    if delta_x < 0:
        new_delta_x = math.fabs(new_delta_x) * -1
    else:
        new_delta_x = math.fabs(new_delta_x)
    if delta_y < 0:
        new_delta_y = math.fabs(new_delta_y) * -1
    else:
        new_delta_y = math.fabs(new_delta_y)

    # utils.warn("old delta x , y:" + str(delta_x) + ' , ' + str(delta_y))
    # utils.warn("new delta x , y:" + str(new_delta_x) + ' , ' + str(new_delta_y))
    x_new = x_origin + new_delta_x
    y_new = y_origin + new_delta_y

    # utils.warn("new position:"+str(x_origin+new_delta_x)+", "+str(y_origin+new_delta_y))
    return (x_new, y_new)
    # return (x_target,y_target)


g_prev_plot_xy_check = np.array([])


def plot_cell(
    ax,
    x,
    y,
    start_degree,
    degree,
    color="grey",
    cell_label="",
    cell_arm_length=70,
    used=False,
    site_label="",
    cellfile_layer=plot_param_zorders.ZORDER_PLOT_CELL,
    site_label_offset=0,
    site_font_size=None,
    cell_font_size=None,
):
    global g_prev_plot_xy_check

    """
    check_array = np.array([x, y, start_degree, degree])
    #print "check_array:", check_array
    #print "g_prev_plot_xy_check:", g_prev_plot_xy_check
    if check_array in g_prev_plot_xy_check:
        print "plot_cell - omit duplicate cell data"
        return # omit - dont draw over same x/y

    g_prev_plot_xy_check = np.append(g_prev_plot_xy_check, check_array)
    """

    # print("plot_cell: color", color)
    if site_font_size is None:
        site_font_size = "medium"
    if cell_font_size is None:
        cell_font_size = "medium"

    start_degree = start_degree - (degree / 2)
    if start_degree < 0:
        start_degree += 360
    xy_pos_2 = calculate_point_with_degree_from_y_axis(
        x, y, start_degree, cell_arm_length=cell_arm_length
    )
    xy_pos_3 = calculate_point_with_degree_from_y_axis(
        x, y, float(start_degree) + float(degree), cell_arm_length=cell_arm_length
    )
    verts = [
        (x, y),  # left, bottom
        xy_pos_2,
        xy_pos_3,
        (x, y),  # ignored
    ]

    codes = [
        Path.MOVETO,
        Path.LINETO,
        Path.LINETO,
        Path.CLOSEPOLY,
    ]

    path = Path(verts, codes)

    alpha = 0.8
    if not used:
        alpha = 0.6

    patch = patches.PathPatch(path, facecolor=color, alpha=alpha, zorder=cellfile_layer)
    ax.add_patch(patch)
    """if xy_pos_2[1] > xy_pos_3[1]:
        ax.annotate(text,xy=xy_pos_3)
    else:
        ax.annotate(text, xy=xy_pos_2)
    """

    """
    if 0 <= start_degree <= 90:
        ax.annotate(text, xy=((xy_pos_2[0]+xy_pos_3[0])/2 + 0, (xy_pos_2[1]+xy_pos_3[1])/2 - 0))
    elif 90 < start_degree <= 180:
        ax.annotate(text, xy=((xy_pos_2[0]+xy_pos_3[0])/2 + 15, (xy_pos_2[1]+xy_pos_3[1])/2 + 15))
    elif 180 < start_degree <= 270:
        ax.annotate(text, xy=((xy_pos_2[0]+xy_pos_3[0])/2 - 15, (xy_pos_2[1]+xy_pos_3[1])/2 + 15))
    else:
        ax.annotate(text, xy=((xy_pos_2[0]+xy_pos_3[0])/2 - 15, (xy_pos_2[1]+xy_pos_3[1])/2 - 15))
    """
    ax.annotate(
        cell_label,
        xy=((xy_pos_2[0] + xy_pos_3[0]) / 2 + 0, (xy_pos_2[1] + xy_pos_3[1]) / 2 - 0),
        alpha=alpha,
        zorder=plot_param_zorders.ZORDER_PLOT_CELL_LABEL,
        fontsize=cell_font_size,
    )
    ax.annotate(
        site_label,
        xy=(x, y + site_label_offset),
        alpha=alpha,
        zorder=plot_param_zorders.ZORDER_PLOT_CELL_LABEL,
        fontsize=site_font_size,
    )
    # ax.annotate(cell_label, xy=((xy_pos_2[0] + xy_pos_3[0]) / 2 + 0, (xy_pos_2[1] + xy_pos_3[1]) / 2 - 0), alpha=alpha,
    # zorder=plot_param_zorders.ZORDER_PLOT_CELL_LABEL)
    # ax.annotate(site_label, xy=(x, y + site_label_offset), alpha=alpha,
    # zorder=plot_param_zorders.ZORDER_PLOT_CELL_LABEL)

    # utils.debug("Ploted Cell")


def interval_plot(
    dbcon,
    rat,
    df,
    default_cell_color,
    detail_label_format,
    ax,
    map,
    force_ant_bw=None,
    cell_arm_length=70,
    site_detail_label_format="",
    cellfile_layer=3,
    site_label_offset=0,
    custom_cell_color=None,
    site_font_size=None,
    cell_font_size=None,
):
    import azq_theme_manager

    dprint(
        "azq_cell_file: interval_plot: df len {} columns {}".format(len(df), df.columns)
    )
    if custom_cell_color is not None:
        custom_cell_color_cellfile = custom_cell_color[0]
        custom_cell_color_db = custom_cell_color[1]

    for index, row in df.iterrows():

        degree_plot = row.dir
        degree_plot = int(degree_plot)

        lon = row.lon
        lon = float(lon)

        lat = row.lat
        lat = float(lat)

        if force_ant_bw is None:
            ant_bw = row.ant_bw
            ant_bw = int(float(ant_bw))
        else:
            ant_bw = int(float(force_ant_bw))

        cell_detail_label = detail_label_format
        site_detail_label = site_detail_label_format
        cell_and_site_detail_labels = [cell_detail_label, site_detail_label]

        # format cell_detail_label string
        matched = False
        for col in df.columns:
            col_upper = col.upper()
            match_str = "#" + col_upper
            for detail_label in cell_and_site_detail_labels:
                detail_format = detail_label
                if match_str in detail_label:
                    dprint("match_str in detail label matched", match_str)
                    newstr = None
                    if isinstance(row[col], float) or isinstance(row[col], int):
                        # most to plot are ints
                        if col_upper.strip() == "LON" or col_upper.strip() == "LAT":
                            newstr = str(row[col])
                        else:
                            ival = int(row[col])
                            newstr = str(ival)
                    else:
                        newstr = str(row[col])

                    detail_label = detail_label.replace(match_str, newstr)
                    matched = True
                    if detail_format == cell_and_site_detail_labels[0]:
                        cell_and_site_detail_labels[0] = detail_label
                    else:
                        cell_and_site_detail_labels[1] = detail_label

        dprint("matched:", matched)

        cell_detail_label = cell_and_site_detail_labels[0]
        site_detail_label = cell_and_site_detail_labels[1]

        xy_pixel = map.to_pixels(lat, lon)

        dprint(
            "azq_cell_file read row data: lat {}, lon {}, degree_plot {}, ant_bw {}, xy_pixel {}".format(
                lat, lon, degree_plot, ant_bw, xy_pixel
            )
        )
        dprint("detail_label_format:", detail_label_format)
        dprint("matched cell_detail_label:", cell_detail_label)

        cell_color = default_cell_color

        # if label is default label like #PCI - try match color too
        if (
            detail_label_format == g_detail_label_format_dict[rat]
            or custom_cell_color is not None
        ):
            if custom_cell_color is None:
                matching_color_column = g_main_cell_col[rat]
                theme_df = g_theme_dict[rat]
            else:
                matching_color_column = custom_cell_color_cellfile
                theme_df = azq_theme_manager.get_theme_df_for_column(
                    custom_cell_color_db, dbcon=dbcon
                )
            cell_match_value_color = row[matching_color_column]
            cell_match_value_color = int(cell_match_value_color)

            if theme_df is not None:

                if "match_value" in theme_df.columns.values:
                    dprint(
                        "azq_cell_file - macth_value in cols - cell_match_value_color: {} col vals: {}".format(
                            cell_match_value_color, theme_df.match_value.values
                        )
                    )
                    if cell_match_value_color in theme_df.match_value.values:
                        cell_color = theme_df[
                            theme_df.match_value == cell_match_value_color
                        ].ColorXml.values[0]
                        dprint(
                            "azq_cell_file - dyn gen theme: got maching color for cell:",
                            cell_color,
                        )
                    else:
                        dprint("azq_cell_file - cell_match_value_color not in values")
                else:
                    print(
                        "WARNING: now we use 'match_value' col for xml pci match too - code should not reach here - check xml theme mode - search in Lower:"
                    )
                    if str(cell_match_value_color) in theme_df.Lower.values:
                        cell_color = theme_df[
                            theme_df.Lower == str(cell_match_value_color)
                        ].ColorXml.values[0]
                        dprint(
                            "azq_cell_file - theme file: got matching color for cell:",
                            cell_color,
                        )
                    else:
                        dprint(
                            "azq_cell_file - theme file: failed to get matching color for cell"
                        )
            else:
                dprint("azq_cell_file, interval plot :theme_df is none")
        else:
            dprint("not detail_label_format == g_detail_label_format_dict[rat]")

        used = cell_color != default_cell_color
        clear_site_location()
        plot_cell(
            ax,
            xy_pixel[0],
            xy_pixel[1],
            degree_plot,
            ant_bw,
            color=cell_color,
            cell_label=cell_detail_label,
            cell_arm_length=cell_arm_length,
            used=used,
            site_label=site_detail_label,
            cellfile_layer=cellfile_layer,
            site_label_offset=site_label_offset,
            site_font_size=site_font_size,
            cell_font_size=cell_font_size,
        )


def get_csv_separator_for_file(fp):
    print("fp:", fp)
    with open(fp, "r") as f:
        first_line = f.readline()
        if "\t" in first_line:
            return "\t"
    return ","


def read_cell_file(
    fp, extra_required_columns=[], raise_exception_if_check_failed=False
):

    print(
        "read_cell_file: raise_exception_if_check_failed:",
        raise_exception_if_check_failed,
    )

    df = None
    try:
        df = pd.read_csv(fp, sep=get_csv_separator_for_file(fp))
        df.columns = list(map(str.lower, df.columns))
        # df.columns = map(str.strip(), df.columns) # problem about str.strip()
        rcs = CELL_FILE_REQUIRED_COLUMNS + extra_required_columns
        dprint("read_cell_file: df cols:", df.columns)
        # check if cell file has all required columns:
        for rc in rcs:
            if not rc in df.columns:
                raise Exception(
                    "\n\nERROR: INVALID CELLFILE: can't find column: {} - file: {}\n\n\n".format(
                        rc, fp
                    )
                )

        for nc in CELL_FILE_NUMERIC_COLUMNS:
            try:
                if nc in df.columns:
                    df[nc] = pd.to_numeric(df[nc])
            except Exception as nne:
                raise Exception(
                    "\n\nERROR: INVALID CELLFILE: column: '{}' contains non-numbers. You must REMOVE ALL Non-numbers from this column then re-upload this cellfile. Exception: {} - file: {} (fullpath: {})\n\n\n".format(
                        nc, nne, os.path.basename(fp), fp
                    )
                )

        dprint("read_cell_file: df pre filt out nan len {}".format(len(df)))

        # filter only rows that required column is not null/empty
        for rc in rcs:
            df = df[pd.notnull(df[rc])]

        dprint("read_cell_file: df post filt out nan len {}".format(len(df)))

        df = df_cellfile_check_and_convert(df, fp_for_error_report=fp)
    except Exception as e:
        type_, value_, traceback_ = sys.exc_info()
        exstr = str(traceback.format_exception(type_, value_, traceback_))
        print("WARNING: exception cell file check:", exstr)

        if raise_exception_if_check_failed:
            raise e
        else:
            print(
                "WARNING: raise_exception_if_check_failed False so dont raise - df_cellfile_check_and_convert() exception:",
                e,
            )

    return df


g_cell_file_df_cache = {}


def get_cell_file_df(
    fp, extra_required_columns=[], raise_exception_if_check_failed=False
):
    global g_cell_file_df_cache
    print(
        "get_cell_file_df: raise_exception_if_check_failed:",
        raise_exception_if_check_failed,
    )
    cache_key = (fp, tuple(extra_required_columns), raise_exception_if_check_failed)
    if cache_key in list(g_cell_file_df_cache.keys()):
        return g_cell_file_df_cache[cache_key]
    df = read_cell_file(
        fp,
        extra_required_columns=extra_required_columns,
        raise_exception_if_check_failed=raise_exception_if_check_failed,
    )
    g_cell_file_df_cache[cache_key] = df
    return df


def filter_cell_file_df_for_bounds(df, map_bounds):
    fdf = df
    lats_diff = map_bounds["lats_max"] - map_bounds["lats_min"]
    longs_diff = map_bounds["longs_max"] - map_bounds["longs_min"]

    # fdf.to_csv("fdf.csv")
    # print("filter_cell_file_df_for_bounds lats_diff {} longs_diff {} map_bounds: {}".format(lats_diff, longs_diff, map_bounds))

    filtstr = "lat >= {}".format(map_bounds["lats_min"] - lats_diff)
    fdf = fdf.query(filtstr)
    # print("filter_cell_file_df_for_bounds0 post len ", len(fdf), "filtstr:", filtstr)

    filtstr = "lat <= {}".format(map_bounds["lats_max"] + lats_diff)
    fdf = fdf.query(filtstr)
    # print("filter_cell_file_df_for_bounds1 post len ", len(fdf), "filtstr:", filtstr)

    filtstr = "lon >= {}".format(map_bounds["longs_min"] - longs_diff)
    fdf = fdf.query(filtstr)
    # print("filter_cell_file_df_for_bounds2 post len ", len(fdf), "filtstr:", filtstr)

    filtstr = "lon <= {}".format(map_bounds["longs_max"] + longs_diff)
    fdf = fdf.query(filtstr)
    # print("filter_cell_file_df_for_bounds final  post len ", len(fdf), "filtstr:", filtstr)

    return fdf


def apply_cell_file(
    dbcon,
    ax,
    map,
    map_bounds,
    force_ant_bw=None,
    cell_arm_length=70,
    cellfile_rat_list=["lte", "wcdma", "gsm"],
    default_cell_color="#555555",
    cell_custom_label_format=None,
    site_detail_label_format="",
    sub_system=None,
    cellfile_layer=3,
    site_label_offset=0,
    custom_cell_color=None,
    site_font_size=None,
    cell_font_size=None,
):
    global g_cell_fp_dict
    global g_theme_dict
    global g_prev_plot_xy_check

    print(
        (
            "apply_cell_file start cellfile_rat_list:",
            cellfile_rat_list,
            "g_cell_fp_dict:",
            g_cell_fp_dict,
        )
    )

    g_prev_plot_xy_check = np.array([])  # make new empty one

    for rat in cellfile_rat_list:

        cell_label_format = g_detail_label_format_dict[rat]
        if cell_custom_label_format is not None:
            cell_label_format = cell_custom_label_format

        if g_cell_fp_dict[rat] is not None:
            print(("plotting cellfile for rat:", rat))
            df = get_cell_file_df(g_cell_fp_dict[rat], [g_main_cell_col[rat]])
            df = filter_cell_file_df_for_bounds(df, map_bounds)
            if sub_system is not None:
                if "sub_system" in df.columns:
                    print("pre filt sub_system df len:", len(df))
                    df = df.query("sub_system == '{}'".format(sub_system))
                    print("post filt sub_system df len:", len(df))
                else:
                    print("sub_system column not found")
            interval_plot(
                dbcon,
                rat,
                df,
                default_cell_color,
                cell_label_format,
                ax,
                map,
                force_ant_bw,
                cell_arm_length=cell_arm_length,
                site_detail_label_format=site_detail_label_format,
                cellfile_layer=cellfile_layer,
                site_label_offset=site_label_offset,
                custom_cell_color=custom_cell_color,
                site_font_size=site_font_size,
                cell_font_size=cell_font_size,
            )

            # only supported in LTE now
            if rat == "lte":
                # if custom cellfile was added inside phone log
                (
                    is_use_dynamic_cell_df,
                    dynamic_lte_cell_df,
                ) = get_dynamic_cell_info_flag(dbcon, rat)
                if is_use_dynamic_cell_df:
                    dprint("plotting is_use_dynamic_cell_df mode for rat:", rat)
                    df = dynamic_lte_cell_df
                    interval_plot(
                        dbcon,
                        rat,
                        dynamic_lte_cell_df,
                        default_cell_color,
                        cell_label_format,
                        ax,
                        map,
                        force_ant_bw,
                        cell_arm_length=cell_arm_length,
                        site_detail_label_format=site_detail_label_format,
                        cellfile_layer=cellfile_layer,
                        site_label_offset=site_label_offset,
                        custom_cell_color=custom_cell_color,
                        site_font_size=site_font_size,
                        cell_font_size=cell_font_size,
                    )

    dprint("apply_cell_file done")


def df_cellfile_check_and_convert(df, fp_for_error_report=None):

    rename_dicts = [
        # one dict in list per each required col
        {"tac": "lac"},
        {"cid": "cell_id", "eci": "cell_id", "cell_id": "cell_id"},
    ]

    for rename_dict in rename_dicts:
        required_cols = pd.Series(list(rename_dict.values())).unique()
        print("required_cols:", required_cols)
        for required_col in required_cols:
            print("check required_col:", required_col)
            if required_col not in df.columns:
                print(
                    "check required_col:",
                    required_col,
                    "not in df.columns:",
                    df.columns,
                )
                df = df.rename(columns=rename_dict)
            else:
                print("check required_col:", required_col, "already in df.columns - ok")

        # recheck again if now required cols exist or not
        for required_col in required_cols:
            if required_col not in df.columns:
                raise Exception(
                    "required column: {} not present in cellfile at path: {}".format(
                        required_col, fp_for_error_report
                    )
                )

    df = df.dropna(subset=["mcc", "mnc", "lac", "cell_id"])

    if "cgi" in df.columns:
        del df["cgi"]

    df["mcc"] = df["mcc"].astype(int).astype(str)
    df["mnc"] = df["mnc"].astype(int).astype(str)
    df["lac"] = df["lac"].astype(int).astype(str)
    df["cell_id"] = df["cell_id"].astype(int).astype(str)

    df["cgi"] = df["mcc"] + " " + df["mnc"] + " " + df["lac"] + " " + df["cell_id"]

    if len(df) == 0:
        raise Exception(
            "Invalid: empty cellfile dataframe for cellfile at path: {}".format(
                fp_for_error_report
            )
        )

    return df
