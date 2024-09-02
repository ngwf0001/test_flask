import requests
import datetime as dt
import re
from tabulate import tabulate
import airportsdata
import art

re_date = re.compile(r'^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$')


today = dt.datetime.now().strftime('%Y-%m-%d')
params = {'date': today,
        'arrival': 'false',
        'lang': 'en' ,
        'cargo': 'false'}



url = "https://www.hongkongairport.com/flightinfo-rest/rest/flights/past"
airports = airportsdata.load('IATA')  # key is the IATA location code


def display_by_airport_code(date, airport_code):
    table_format = 'heavy_grid'
    print(f"Airport {airport_code} : {airports[airport_code]['name']}, {airports[airport_code]['country']}, Date: {date}")
    table_headers = ['Time', 'Flight', 'Destination', 'Terminal', 'Aisle', 'Gate']
    table_rows = []
    params['date'] = date

    response = requests.get(url, params=params)
    data = response.json()
    for flight_date in data:
        if flight_date['date'] == date:
            flight_list = flight_date['list']
            break

    for flight in flight_list:
        if airport_code in flight['destination']:
            table_rows.append([flight['time'], ", ".join([ flight_no['no'] for flight_no in flight['flight']]), ", ".join(flight['destination']), flight['terminal'], flight['aisle'], flight['gate']])
    print(tabulate( table_rows, headers=table_headers, tablefmt=table_format))


def get_date():
    today = dt.datetime.now().strftime('%Y-%m-%d')

    msg = 'Enter the date (YYYY-MM-DD) Enter for today: '
    while True:
        date = input(msg).strip()
        if not date:
            return today
        elif not re_date.match(date):
            msg = "Wrong format! Please enter the correct date format (YYYY-MM-DD). Enter for today:"
        else:
            return date



print(art.text2art(f"Flights -> {today}", font="standard"))
date = get_date()

input_airport = input("Enter the airport code (e.g., LAX, SFO) or City name:").strip().upper()
input_airport = 'TPE' if not input_airport else input_airport
if input_airport in airports.keys():
    display_by_airport_code(date, input_airport, )
else:
    cityname = input_airport.lower()
    for airport, port_info in airports.items():
        if cityname in port_info['city'].lower():
            airport_code = port_info['iata']
            display_by_airport_code(date, airport_code,)


