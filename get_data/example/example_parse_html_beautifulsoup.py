import pandas as pd
import requests
from bs4 import BeautifulSoup

html_string = '''
    <table>
        <tr>
            <td> Hello </td>
            <td> Table </td>
        </tr?
    </table>
'''

soup = BeautifulSoup(html_string, 'lxml') # Parse the HTML as a string

table = soup.find_all('table')[0]
new_table = pd.DataFrame(columns=range(0,2), index=[0]) # I know the size

row_marker = 0
for row in table.find_all('tr'):
    column_marker = 0
    columns = row.find_all('td')
    for column in columns:
        new_table.iat[row_marker, column_marker] = column.get_text()
        column_marker += 1

new_table

# Using Requests to access a web content
url = "https://www.fantasypros.com/nfl/reports/leaders/qb.php?year=2015"
response = requests.get(url)
response.text[:100]

from src.web_scraping.HTMLTableParser import HTMLTableParser

hp = HTMLTableParser()
table = hp.parse_url(url)

a =1