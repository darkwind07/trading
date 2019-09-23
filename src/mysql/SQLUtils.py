from datetime import datetime
import pandas as pd
from typing import Union

class SQLUtils:
    @staticmethod
    def make_insert_req_from_dataframe_mysql(to_database: str, to_table: str, df: pd.DataFrame) -> str:
        if df.empty:
            raise ValueError('Data is empty')

        def to_str(val: Union[datetime, str, float, bool, int]):
            if isinstance(val, datetime):
                F_DATA_FMT = '%Y-%m-%d %H:%M:%S'
                return f"'{val.strftime(F_DATA_FMT)}'"
            elif isinstance(val, float):
                return f"{val:.6f}"[:19]
            elif isinstance(val, int) or isinstance(val, bool):
                return str(val)
            elif isinstance(val, str):
                return f"'{val}'"

        #df = df[['created_date', 'last_updated_date']]
        columns = ','.join(df.columns.values)
        #values = ','.join(df.apply(lambda row: '(' + ','.join([to_str(v) for v in row]) + ')', axis=1))
        #values = ','.join(df.apply(lambda row: '(' + ','.join([str(v) for v in row.values]) + ')', axis=1))

        values = ("%s, " * 7)[:-2]
        req = f"INSERT INTO {to_table} ({columns}) VALUES {values}"
        req = """INSERT INTO %s (%s) VALUES (%s)""" % (to_table, columns, values)
        return req

