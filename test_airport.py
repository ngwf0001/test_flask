import requests
import datetime as dt
import re
from tabulate import tabulate
import airportsdata

re_date = re.compile('^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$')

url = "https://www.hongkongairport.com/flightinfo-rest/rest/flights/past"

today = dt.datetime.now().strftime('%Y-%m-%d')
params = {'date': today,
          'arrival': 'false',
          'lang': 'en' ,
          'cargo': 'false'}


today = dt.datetime.now().strftime('%Y-%m-%d')

msg = 'Enter the date (YYYY-MM-DD) Enter for today: '
while True:
    date = input(msg).strip()
    params['date'] = params['date'] if not date else ( date if re_date.match(date) else '')
    if params['date']:
        break
    else:
        msg = "Wrong format! Please enter the correct date format (YYYY-MM-DD). Enter for today:"

input_airport = input("Enter the airport code (e.g., LAX, SFO) or City name:").strip().upper()
input_airport = 'TPE' if not input_airport else input_airport

table_headers = ['Time', 'Flight', 'Destination', 'Terminal', 'Aisle', 'Gate']
table_rows = []

flight_list = requests.get(url, params=params).json()[1]['list']
for flight in flight_list:
    if input_airport in flight['destination']:
        table_rows.append([flight['time'], ", ".join([ flight_no['no'] for flight_no in flight['flight']]), ", ".join(flight['destination']), flight['terminal'], flight['aisle'], flight['gate']])
print(tabulate( table_rows, headers=table_headers, tablefmt='grid'))




