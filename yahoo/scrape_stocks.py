import requests
import pandas as pd
import json

# goto url and check number of results before start script : actually 600
url = "https://finance.yahoo.com/screener/unsaved/48590216-0d79-442b-b1ed-456c968d738f?count=100&offset="
output_file = 'stocks.json'
stocks = []
session = requests.session()

for i in range(0, 700, 100):
    u = url + str(i)
    print(f'Fetching {u}...')
    req = session.get(u)
    if req.status_code == 200:
        tables = pd.read_html(req.content)
        table = tables[0]
        stocks += list(table.Symbol)
        print(f'\t{len(table)} stocks')
    else:
        print(req.status_code)

# Write
with open(output_file, 'w') as file:
    json.dump(stocks, file)

print(f'{len(stocks)} stocks extracted to {output_file} file')

# Read
# with open(output_file) as file:
#    json.load(file)
