import datetime
import MySQLdb as mdb
import yfinance as yf
import pandas as pd
from urllib.request import urlopen

# Obtain a database connection to the MySQL instance
db_host = 'localhost'
db_user = 'xiao'
db_pass = 'Wx3921786!'
db_name = 'securities_master'
connect = mdb.connect(db_host, db_user, db_pass, db_name)

def obtain_list_of_db_tickers():
    """
    obtain a list of the ticker symbols in the database
    """
    mysql_cursor = connect.cursor()
    mysql_cursor.execute("SELECT id, ticker FROM symbol")
    data = mysql_cursor.fetchall()
    return [(d[0], d[1]) for d in data]


def get_daily_historic_data_yahoo(ticker,
                                  start_date='2000-01-01',
                                  end_date=datetime.date.today()):
    """
    The Yahoo! Finance decommissioned their historical data API in 2017
    The library yfinance is developed to fix this problem
    :param ticker: ticker
    :param start_date: historic data start date
    :param end_date: historic data end date
    :return: ticker historic DataFrame
    """
    yf_symbol = yf.Ticker(ticker)
    try:
        hist = yf_symbol.history(start=start_date, end=end_date) # the default is the all OHLC are adjusted
        hist = hist.dropna()
    except ValueError as e:
        print(e)
    return hist

def insert_daily_data_into_db(data_vendor_id, symbol_id, hist_data: pd.DataFrame):
    """
    add the hist data into MYSQL database.
    append the vendor id and symbol id to the data
    :param data_vendor_id:
    :param symbol_id:
    :param hist_data: historic DataFrame
    """
    # create the time now (utc time)
    now = datetime.datetime.utcnow()

    # change the column name
    hist_data.reset_index(inplace=True)
    hist_data = hist_data.rename(columns={'Date': 'price_date', 'Open': 'open_price', 'High': 'high_price',
                                          'Low': 'low_price', 'Close': 'close_price', 'Volume': 'volume',
                                          'Dividends': 'dividends', 'Stock Splits': 'stock_splits'})
    # amend the DataFrame to include the vendor ID and symbol ID
    hist_data['data_vendor_id'] = data_vendor_id
    hist_data['symbol_id'] = symbol_id
    # add created_date and last_updated_date
    hist_data['created_date'] = now
    hist_data['last_updated_date'] = now


    # create req strings
    table_name = 'daily_price'
    columns = ','.join(hist_data.columns.values)
    values = ("%s, " * 12)[:-2]
    req = """INSERT INTO %s (%s) VALUES (%s)""" % (table_name, columns, values)

    mysql_cursor = connect.cursor()
    chunk_size = 1000
    for i in range(0, len(hist_data.index), chunk_size):
        chunk_df = hist_data.iloc[i: i + chunk_size]
        data = [tuple(x) for x in chunk_df.values.tolist()]
        mysql_cursor.executemany(req, data)
        connect.commit()

    mysql_cursor.close()

# temp test
#t = obtain_list_of_db_tickers()[16]
#yf_data = get_daily_historic_data_yahoo((t[1]))
#insert_daily_data_into_db('1', t[0], yf_data)

if __name__ == '__main__':
    # loop over the tickers and insert the daily historical data into database
    tickers = obtain_list_of_db_tickers()
    for t in tickers:
        print("Adding data for %s" % t[1])
        try:
            yf_data = get_daily_historic_data_yahoo((t[1]))
            insert_daily_data_into_db('1', t[0], yf_data)
        except UnboundLocalError:
            pass

a = 1