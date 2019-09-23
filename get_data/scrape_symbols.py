import MySQLdb as mdb
from datetime import datetime
from src.web_scraping.HTMLTableParser import HTMLTableParser
# S&P 500 URL

def obtain_parse_wiki_snp500():
    """
    Download and parse the Wiki list of S&P500 constituents using requests and libxml
    return: a list of symbols for to add to MySQL
    """

    # stores the current time, for the created_at record
    now = datetime.now()

    # get the symbols from website
    url = 'http://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    hp = HTMLTableParser()
    stock_table = hp.parse_url(url)[0] # select the first table
    stock_table = stock_table.replace('\n', '', regex=True) # delete '\n'
    stock_table.columns = ['Symbol', 'Security', 'SEC filings', 'GICS Sector', 'GICS Sub Industry',
                           'Headquarters location', 'Date first added', 'CIK', 'Founded']
    df_symbol = stock_table[['Symbol', 'Security', 'GICS Sector']]
    df_symbol = df_symbol.rename(columns={'Symbol': 'ticker', 'Security': 'name', 'GICS Sector': 'sector'})
    df_symbol['instrument'] = 'stock'
    df_symbol['currency'] = 'USD'
    df_symbol['created_date'] = now
    df_symbol['last_updated_date'] = now
    return df_symbol

def insert_snp500_symbols(df_symbol):
    """Insert the S&P500 symbols into the MySQL database"""

    # connect to the MySQL instance
    db_host = 'localhost'
    db_user = 'xiao'
    db_pass = 'Wx3921786!'
    db_name = 'securities_master'
    connect = mdb.connect(host=db_host, user=db_user, password=db_pass, db=db_name)
    mysql_cursor = connect.cursor()

    # create req strings
    table_name = 'symbol'
    columns = ','.join(df_symbol.columns.values)
    values = ("%s, " * 7)[:-2]
    req = """INSERT INTO %s (%s) VALUES (%s)""" % (table_name, columns, values)

    # insert to MySQL with max chunk_size = 1000
    chunk_size = 1000
    for i in range(0, len(df_symbol.index), chunk_size):
        chunk_df = df_symbol.iloc[i: i+chunk_size]
        data = [tuple(x) for x in chunk_df.values.tolist()]
        mysql_cursor.executemany(req, data)
        connect.commit()

    mysql_cursor.close()


if __name__ == "__main__":
    df_symbol = obtain_parse_wiki_snp500()
    insert_snp500_symbols(df_symbol)
