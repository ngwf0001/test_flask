import requests
import datetime as dt
# import pickle
from tabulate import tabulate
import pandas as pd
import streamlit as st

url0 = 'https://data.etabus.gov.hk/'
urlstop0 = '/v1/transport/kmb/stop/'
def grab_stop_db():

    filename ='stop_db.pkl'
    url = 'https://data.etabus.gov.hk/v1/transport/kmb/route-stop'

#     def file_older_than(filename, days=7):
#         t = os.path.getmtime(filename)
#         file_datetime= dt.datetime.fromtimestamp(t)
#         return  dt.datetime.now() - file_datetime > dt.timedelta(0)

#     if not os.path.exists(filename) or file_older_than(filename, days= 0):
#         data = requests.get(url).json()['data']
#         with open(filename, 'wb') as f:
#             pickle.dump(data, f)
#         return data
#     else:
    # with open(filename, 'rb') as f:
    #     data = pickle.load(f)
    #     return data
    data = requests.get(url).json()['data']
    # with open(filename, 'wb') as f:
    #     pickle.dump(data, f)
    return data

def get_route_stops(route_number: str, in_out: str = 'O'):
    data = grab_stop_db()
    route_data = [stop for stop in data
                  if stop['route'] == route_number and stop['bound'] == in_out]
    return route_data


def get_stop_names(route_number: str, in_out: str = 'O'):
    url0 = 'https://data.etabus.gov.hk/'
    urlstop0 = '/v1/transport/kmb/stop/'
    stop_name_list = []
    # data = requests.get(url).json()['data']
    # route_data = [stop for stop in data if stop['route'] == route_number and stop['bound']== in_out]
    route_data = get_route_stops(route_number, in_out)
    for stop in route_data:
        stopid = stop['stop']
        urlstop = url0+urlstop0+stopid
        stopname = requests.get(urlstop).json().get('data').get('name_tc')
        stop_name_list.append(stopname)
    return stop_name_list


def get_stops_eta(route_number: str, in_out: str = 'O'):
    url0 = 'https://data.etabus.gov.hk/'
    url_eta = '/v1/transport/kmb/route-eta/{route}/{service_type}'
    url_eta2 = url0 + url_eta.format(route=route_number, service_type='1')
    data = requests.get(url_eta2).json()['data']
    stops = [stop for stop in data if stop['eta_seq']
             == 1 and stop['dir'] == in_out]
    return stops


def show_route(stop_name_list, stops_eta, route_number: str, in_out: str = 'O'):
    table = []
    # stop_name_list = get_stop_names(route_number, in_out)
    # stops_eta = get_stops_eta(route_number, in_out)
    headers = ['站號', '站名', '到站時間', '相差']
    for stop in stops_eta:
        stop_seq = stop['seq']
        if stop['eta'] != None:
            new_time = dt.datetime.fromisoformat(stop['eta']).replace(tzinfo=None)
            print(new_time)
            time_difference = new_time - dt.datetime.now()
            minutes, seconds  = time_difference.seconds // 60, time_difference.seconds % 60 if  time_difference > dt.datetime(0) else 0, 0
            print(minutes, '分', seconds, '秒'  )

            table.append([stop_seq, stop_name_list[stop_seq-1],
                         new_time.strftime('%H:%M:%S'),  f'{minutes}:{seconds}'
                         ])
        else:
            table.append([stop_seq, stop_name_list[stop_seq-1], 'NO TIMING',''])
    print(tabulate(table, headers, tablefmt="simple_grid"))

def show_route_st(stop_name_list, stops_eta, route_number: str, in_out: str = 'O'):

    # stop_name_list = get_stop_names(route_number, in_out)
    # stops_eta = get_stops_eta(route_number, in_out)
    table =[]
    df = None
    headers = ['站號', '站名', '到站時間', '相差']
    for stop in stops_eta:
        stop_seq = stop['seq']
        if stop['eta'] != None:
            new_time = dt.datetime.fromisoformat(stop['eta']).replace(tzinfo=None)
            time_difference = new_time - dt.datetime.now()

            # minutes = time_difference.seconds // 60
            # seconds = time_difference.seconds % 60
            minutes, seconds  =( time_difference.seconds // 60, time_difference.seconds % 60 ) if  time_difference > dt.timedelta(0) else (0, 0)
            table.append([stop_seq, stop_name_list[stop_seq-1],
                         new_time.strftime('%H:%M:%S'),  f'{minutes:02d}:{seconds:02d}'
                         ])
        else:
            table.append([stop_seq, stop_name_list[stop_seq-1], 'NO TIMING',''])
        df = pd.DataFrame(table, columns=headers)

    st.dataframe(df, height = 1000,  use_container_width=True, hide_index=True)


st.set_page_config(page_title='Frankie KMB page ', layout="wide")

route_number = st.text_input('What is the route? ').strip().upper()

if route_number:
    columns_dict = {}
    columns_dict['I'], columns_dict['O'] = st.columns(2)
    for in_out in ['I', 'O']:
        with columns_dict[in_out]:
            st.header(f"Route: {route_number} In/Out: {in_out}")
            stop_name_list = get_stop_names(route_number, in_out)
            stops_eta = get_stops_eta(route_number, in_out)
            # show_route(stop_name_list, stops_eta, route_number, in_out)
            show_route_st(stop_name_list, stops_eta, route_number, in_out)
