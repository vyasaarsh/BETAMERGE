#Libraries
import streamlit as st
import pandas as pd 
import paramiko
from time import sleep
from collections import defaultdict, deque

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
            _, timestamp = line.split(',')
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
            table_data.append({
                'Symbol': symbol,
                'Price': float(last_price),
                'Change': change,
                '% Change': (change / float(last_price)) * 100,
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
    data = channel.recv(1024).decode('ascii')
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

#Retrieve Historic(hist1s) data
def get_real_time_data_hist1s(channel, hist1s_data):
    data = channel.recv(1024).decode('ascii')
    table_data = parse_hist1s_data(data, hist1s_data)
    
    for symbol in hist1s_data.keys():
        if symbol not in [item['Symbol'] for item in table_data]:
            last_known_price = hist1s_data[symbol][-1]
            table_data.append({
                'Symbol': symbol,
                'Price': last_known_price,
                'Change': 0,
                '% Change': 0,
                'Trend': list(hist1s_data[symbol]),
            })

    return table_data

#Retrieve Historic(hist1m) data
def get_real_time_data_hist1m(channel, hist1m_data):
    data = channel.recv(1024).decode('ascii')
    table_data = parse_hist1m_data(data, hist1m_data)
    
    for symbol in hist1m_data.keys():
        if symbol not in [item['Symbol'] for item in table_data]:
            last_known_price = hist1m_data[symbol][-1]
            table_data.append({
                'Symbol': symbol,
                'Price': last_known_price,
                'Change': 0,
                '% Change': 0,
                'Trend': list(hist1m_data[symbol]),
            })

    return table_data

#Retrieve Historic(hist1h) data
def get_real_time_data_hist1h(channel, hist1h_data):
    data = channel.recv(1024).decode('ascii')
    table_data = parse_hist1h_data(data, hist1h_data)
    
    for symbol in hist1h_data.keys():
        if symbol not in [item['Symbol'] for item in table_data]:
            last_known_price = hist1h_data[symbol][-1]
            table_data.append({
                'Symbol': symbol,
                'Price': last_known_price,
                'Change': 0,
                '% Change': 0,
                'Trend': list(hist1h_data[symbol]),
            })

    return table_data

#Main function to monitor and fetch data

def main():
    st.set_page_config(layout="wide")

    historic_data = defaultdict(deque)
    hist_data_1s = defaultdict(deque)
    hist_data_1m = defaultdict(deque)
    hist_data_1h = defaultdict(deque)

    channel_rt = connect_ssh_agent("rt")
    channel_hist1s = connect_ssh_agent("hist1s")
    channel_hist1m = connect_ssh_agent("hist1m")    
    channel_hist1h = connect_ssh_agent("hist1h")

    st.title("Real Time and Historical Prices")
    st.divider()
    st.subheader("Prices, Trends, and Changes for each symbol")
    
    # Container for real-time data
    container_rt = st.empty()
    container_hist1s = st.empty()
    container_hist1m = st.empty()   
    container_hist1h = st.empty()

    # Display real-time data continuously
    counter_rt = 0
    counter_hist1s = 0
    counter_hist1m = 0
    counter_hist1h = 0
    
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

        # Fetch and display hist1s data
        new_data_hist1s = get_real_time_data_hist1s(channel_hist1s, hist_data_1s)
        if new_data_hist1s:
            table_data_hist1s = pd.DataFrame(new_data_hist1s)
            container_hist1s.data_editor(
                table_data_hist1s,
                column_config={
                    "Symbol": st.column_config.TextColumn("Symbol"),
                    "Trend": st.column_config.LineChartColumn("Trend", width="medium"),
                    "Price": st.column_config.NumberColumn("Price"),
                    "Change": st.column_config.NumberColumn("Change"),
                    "% Change": st.column_config.NumberColumn("% Change"),
                },
                key=f"hist1s_data_{counter_hist1s}",
                hide_index=True,
                use_container_width=True
            )

        # Fetch and display hist1m data
        new_data_hist1m = get_real_time_data_hist1m(channel_hist1m, hist_data_1m)
        if new_data_hist1m:
            table_data_hist1m = pd.DataFrame(new_data_hist1m)
            container_hist1m.data_editor(
                table_data_hist1m,
                column_config={
                    "Symbol": st.column_config.TextColumn("Symbol"),
                    "Trend": st.column_config.LineChartColumn("Trend", width="medium"),
                    "Price": st.column_config.NumberColumn("Price"),
                    "Change": st.column_config.NumberColumn("Change"),
                    "% Change": st.column_config.NumberColumn("% Change"),
                },
                key=f"hist1m_data_{counter_hist1m}",
                hide_index=True,
                use_container_width=True
            )

        # Fetch and display hist1h data
        new_data_hist1h = get_real_time_data_hist1h(channel_hist1h, hist_data_1h)
        if new_data_hist1h:
            table_data_hist1h = pd.DataFrame(new_data_hist1h)
            container_hist1h.data_editor(
                table_data_hist1h,
                column_config={
                    "Symbol": st.column_config.TextColumn("Symbol"),
                    "Trend": st.column_config.LineChartColumn("Trend", width="medium"),
                    "Price": st.column_config.NumberColumn("Price"),
                    "Change": st.column_config.NumberColumn("Change"),
                    "% Change": st.column_config.NumberColumn("% Change"),
                },
                key=f"hist1h_data_{counter_hist1h}",
                hide_index=True,
                use_container_width=True
            )

        sleep(1)

if __name__ == "__main__":
    main()