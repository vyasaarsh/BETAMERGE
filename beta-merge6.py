#Libraries
import streamlit as st
import pandas as pd 
import paramiko
from time import sleep
from collections import defaultdict, deque

from constants.timeRange import TimeRange
from utils.getTimeRangeSpecificData import get_time_specific_data

#Function to establish  SSH connection
def connect_ssh_agent(username): 
    hostname = "rt1.olsendata.com"
    port = 22103
    password = "aar5hvya5"
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, port, username, password)
    return ssh.invoke_shell()

#Parse Real-Time(rt) data from SSH connection
def parse_real_time_data(data, historic_data):
    lines = data.strip().split('\n')
    table_data = []
    for line in lines:
        if line.startswith('!'):
            _, timestamp = line.split(',')
        else:
            try:
                symbol, last_price, _ = line.split(',')
            except ValueError:
                continue
            change = 0
            if symbol in historic_data:
                trend = historic_data[symbol]
                change = float(last_price) - trend[-1]
                trend.append(float(last_price))
                if len(trend) > 100:
                    trend.popleft()
                historic_data[symbol] = trend
            else: 
                historic_data[symbol] = deque([float(last_price)])
            table_data.append({
                'Symbol': symbol,
                'Price': float(last_price),
                'Change': change,
                '% Change': (change / float(last_price)) * 100,
                'Trend': list(historic_data[symbol]),
            })
    return table_data

#Parse Historcal(hist1s) data from SSH connection
def parse_hist1s_data(data, hist1s_data):
    lines = data.strip().split('\n')
    table_data = []
    for line in lines:
        if line.startswith('!'):
            parts = line.split(',')
            if len(parts) >= 2:
                _, timestamp = parts[:2]
                # You can process the timestamp here if needed
            else:
                # Skip the line or handle it accordingly
                continue
        else:
            try:
                symbol, last_price, _ = line.split(',')
            except ValueError:
                continue
            change = 0
            if symbol in hist1s_data:
                trend = hist1s_data[symbol]
                change = float(last_price) - trend[-1]
                trend.append(float(last_price))
                if len(trend) > 100:
                    trend.popleft()  # Keep deque size manageable
                hist1s_data[symbol] = trend
            else:
                hist1s_data[symbol] = deque([float(last_price)])
            price = float(last_price)
            percent_change = (change / price) * 100 if price != 0 else 0
            table_data.append({
                'Symbol': symbol,
                'Price': price,
                'Change': change,
                '% Change': percent_change,
                'Trend': list(hist1s_data[symbol]),
            })
    return table_data

#Parse Historical(hist1m) data from SSH connection
def parse_hist1m_data(data, hist1m_data):
    lines = data.strip().split('\n')
    table_data = []
    for line in lines:
        if line.startswith('!'):
            parts = line.split(',')
            if len(parts) == 2:
                _, timestamp = parts
                # Assuming we can ignore the seconds, or treat them as '00'
                timestamp = f"{timestamp}:00"
            else:
                continue
        else:
            try:
                symbol, last_price, _ = line.split(',')
            except ValueError:
                continue
            change = 0
            if symbol in hist1m_data:
                trend = hist1m_data[symbol]
                change = float(last_price) - trend[-1]
                trend.append(float(last_price))
                if len(trend) > 100:
                    trend.popleft()  # Keep deque size manageable
                hist1m_data[symbol] = trend
            else:
                hist1m_data[symbol] = deque([float(last_price)])
            table_data.append({
                'Symbol': symbol,
                'Price': float(last_price),
                'Change': change,
                '% Change': (change / float(last_price)) * 100,
                'Trend': list(hist1m_data[symbol]),
            })
    return table_data

#Parse Historical(hist1h) data from SSH connection
def parse_hist1h_data(data, hist1h_data):
    lines = data.strip().split('\n')
    table_data = []
    current_symbol = None
    
    for line in lines:
        if line.startswith('#'):
            # This line indicates the start of a new symbol section
            current_symbol = line[1:].strip()  # Extract the symbol name after '#'
        else:
            try:
                date, timestamp, last_price, _ = line.split(',')
                # Construct a timestamp (we ignore minutes/seconds)
                timestamp = f"{date} {timestamp}:00:00"
            except ValueError:
                continue
            
            change = 0
            if current_symbol in hist1h_data:
                trend = hist1h_data[current_symbol]
                change = float(last_price) - trend[-1]
                trend.append(float(last_price))
                if len(trend) > 100:
                    trend.popleft()  # Keep deque size manageable
                hist1h_data[current_symbol] = trend
            else:
                hist1h_data[current_symbol] = deque([float(last_price)])
            
            table_data.append({
                'Symbol': current_symbol,
                'Price': float(last_price),
                'Change': change,
                '% Change': (change / float(last_price)) * 100,
                'Trend': list(hist1h_data[current_symbol]),
                'Timestamp': timestamp
            })
    
    return table_data

#Retrieve Real-Time(rt) data
def get_real_time_data_rt(channel, historic_data):
    if channel.recv_ready():
        data = channel.recv(4096).decode('ascii')
        table_data = parse_real_time_data(data, historic_data)
    
        for symbol in historic_data.keys():
            if symbol not in [item['Symbol'] for item in table_data]:
                last_known_price = historic_data[symbol][-1]
                table_data.append({
                'Symbol': symbol,
                'Price': last_known_price,
                'Change': 0,
                '% Change': 0,
                'Trend': list(historic_data[symbol]),
                })

        return table_data

#Retrieve Historic data
def get_historical_data(userName):
    print('connecting to ssh agent %s', userName)
    channel = connect_ssh_agent("hist1s")
    print('connected to channel of ssh agent %s', userName)
    print('fetching data for ssh channel of %s', userName)
    buffer = ''
    while True:
        if channel.recv_ready():
            data = channel.recv(16384).decode('ascii')
            buffer += data
            if channel.exit_status_ready():
                break
        sleep(0.1)
    print('fetching data for ssh channel of %s is completed', userName)
    print('closing channel for ssh agent %s', userName)
    channel.close()
    print('closed channel for ssh agent %s', userName)
    return buffer

#Main function to monitor and fetch data
def main():
    st.set_page_config(layout="wide")

    historic_data = defaultdict(deque)
    
    channel_rt = connect_ssh_agent("rt")
    
    # fetch historical data
    historical_data_1h = get_historical_data("hist1h")
    parse_hist1h_data = parse_hist1h_data(historical_data_1h)
    # historical_data_1s = get_historical_data("hist1s")
    # parse_hist1s_data = parse_hist1h_data(historical_data_1s)
    # historical_data_1m = get_historical_data("hist1m")
    # parse_hist1m_data = parse_hist1m_data(historical_data_1m)

    st.title("Real Time and Historical Prices")
    st.divider()
    
    # Container for real-time data
    container_rt = st.empty()
    
    # Display real-time data continuously
    counter_rt = 0
    
    option = st.selectbox(
        "Time range:",
        [time_range.value for time_range in TimeRange.__members__.values()],
    )

    # You can use the selected option to determine the time range
    selected_time_range = next((time_range for time_range in TimeRange if time_range.value == option), None)

    time_range_data = get_time_specific_data(selected_time_range.value, [], [], parse_hist1h_data)

    while True:
        # Fetch and display real-time data
        new_data_rt = get_real_time_data_rt(channel_rt, historic_data)
        if new_data_rt:
            table_data_rt = pd.DataFrame(new_data_rt)
            table_data_rt['% Change'] = table_data_rt['% Change'].apply(lambda x: f"{x:.2f}%")
            counter_rt += 1
            sorted_table_rt = table_data_rt[['Symbol', 'Trend', 'Price', 'Change', '% Change']].drop_duplicates(subset=['Symbol']).sort_values(by='Symbol')
            container_rt.data_editor(
                sorted_table_rt,
                column_config={
                    "Symbol": st.column_config.TextColumn("Symbol"),
                    "Trend": st.column_config.LineChartColumn("Trend", width="medium"),
                    "Price": st.column_config.NumberColumn("Price"),
                    "Change": st.column_config.NumberColumn("Change"),
                    "% Change": st.column_config.NumberColumn("% Change"),
                },
                key=f"rt_data_{counter_rt}",
                hide_index=True,
                use_container_width=True
            )

        sleep(1)

if __name__ == "__main__":
    main()
