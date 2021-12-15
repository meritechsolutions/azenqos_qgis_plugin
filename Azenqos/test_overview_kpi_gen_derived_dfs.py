import sqlite3
import contextlib
import os
import pandas as pd
import server_overview_widget

def test():
    dbfp = "../example_logs/overview_adbdd4d4-0322-4aa5-a642-5dabe735b898.db"
    if os.path.isfile(dbfp):        
        with contextlib.closing(sqlite3.connect(dbfp)) as dbcon:
            df_dict = server_overview_widget.gen_derived_dfs(dbcon)
            print("df_dict keys", df_dict.keys())
    

if __name__ == "__main__":
    test()
