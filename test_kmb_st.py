import streamlit as st
st.set_page_config(page_title='BB 九巴到站時間查詢', layout="wide")

import requests
import datetime as dt
import pickle
import os
import pandas as pd



url0 = 'https://data.etabus.gov.hk/'

def file_older_than(filename, days=7):
    t = os.path.getmtime(filename)
    file_datetime= dt.datetime.fromtimestamp(t)
    return  dt.datetime.now() - file_datetime > dt.timedelta(days)

def grab_stop_db():

    filename ='routes_stop.pkl'
    url = 'https://data.etabus.gov.hk/v1/transport/kmb/route-stop'
    stop_keep_days = 7

    if (not os.path.exists(filename)) or file_older_than(filename, days= stop_keep_days):
        data = requests.get(url).json()['data']
        with open(filename, 'wb') as f:
            pickle.dump(data, f)
    else:
        with open(filename, 'rb') as f:
            data = pickle.load(f)
    return data

def get_route_stops(route_number: str, in_out: str = 'O'):
    data = grab_stop_db()
    route_data = [stop for stop in data
                  if stop['route'] == route_number and stop['bound'] == in_out]
    return route_data


def get_all_stops():

    all_stop_file = 'all_stops.pkl'
    url0 = 'https://data.etabus.gov.hk'
    endpoint_stops = '/v1/transport/kmb/stop/'
    stops_keep_days = 7

    if (not os.path.exists(all_stop_file)) or file_older_than(all_stop_file, days= stops_keep_days):
        data = requests.get(url0+endpoint_stops).json()['data']
        all_stop_dict = {stop['stop']: stop['name_tc'] for stop in data}
        with open(all_stop_file, 'wb') as f:
            pickle.dump(all_stop_dict, f)
    else:
        with open(all_stop_file, 'rb') as f:
            all_stop_dict = pickle.load(f)
    return all_stop_dict


def get_stop_names(route_number: str, in_out: str = 'O'):
    all_stop_dict = get_all_stops()
    stop_name_list = []
    route_data = get_route_stops(route_number, in_out)
    for stop in route_data:
        stopid = stop['stop']
        stopname = all_stop_dict.get(stopid, '無法查出站名')
        stop_name_list.append(stopname)
    return stop_name_list


def get_stops_eta(route_number: str):
    url0 = 'https://data.etabus.gov.hk/'
    url_eta = '/v1/transport/kmb/route-eta/{route}/{service_type}'
    url_eta2 = url0 + url_eta.format(route=route_number, service_type='1')
    data = requests.get(url_eta2).json()['data']
    stops_in = [stop for stop in data if stop['eta_seq'] == 1 and stop['dir'] == 'I']
    stops_out = [stop for stop in data if stop['eta_seq'] == 1 and stop['dir'] == 'O']
    return {'I': stops_in, 'O' : stops_out}


def show_route_st(stop_name_list, stops_eta, route_number: str, in_out: str = 'O'):

    headers = ['站號', '站名', '到站時間', '多久後到?']
    table =[headers]
    table = []
    time_now =dt.datetime.now(dt.timezone.utc).astimezone()
    for stop in stops_eta:
        stop_seq = stop['seq']
        if stop['eta'] != None:
            new_time = dt.datetime.fromisoformat(stop['eta'])
            time_difference = new_time - time_now
            minutes, seconds  =( time_difference.seconds // 60, time_difference.seconds % 60 ) if  time_difference > dt.timedelta(0) else (0, 0)
            table.append([stop_seq, stop_name_list[stop_seq-1], new_time.strftime('%H:%M:%S'),  f'{minutes:02d}:{seconds:02d}'])
        else:
            table.append([stop_seq, stop_name_list[stop_seq-1], 'NO TIMING',''])
    df = pd.DataFrame(table, columns=headers, )
    df.sort_values(by= ['站號'], inplace = True)
    st.dataframe(df, height=35*len(df)+38,  use_container_width=True, hide_index=True)




f"""
# Fan 九巴到站時間查詢

## 現在時間: {dt.datetime.now(dt.timezone.utc).astimezone().strftime('%H:%M:%S') }

"""

route_number = st.text_input('## 請輸入路線號碼').strip().upper()
if route_number: st.header(f'查詢路線: {route_number}')
columns_dict = {}
columns_dict['O'], columns_dict['I'] = st.columns(2)

if route_number:
    stops_eta_dict = get_stops_eta(route_number)
    for in_out in ['O', 'I']:
        with columns_dict[in_out]:
            st.header(f"{'回' if in_out=='I' else '去'}程")
            stop_name_list = get_stop_names(route_number, in_out)
            show_route_st(stop_name_list, stops_eta_dict[in_out], route_number, in_out)
