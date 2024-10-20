# Libraries
import streamlit as st
import pandas as pd 
from time import sleep
from collections import defaultdict, deque
import threading
import plotly.express as px

from constants.timeRange import TimeRange
from utils.getTimeRangeSpecificData import get_time_specific_data
from utils.connectionUtils import connect_ssh_agent
from utils.dataParser import parse_real_time_data, parse_hist1h_data, parse_hist1m_data, parse_hist1s_data

# Retrieve Real-Time (rt) data
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

# Retrieve Historical data
def get_historical_data(userName):
    print('connecting to ssh agent %s', userName)
    channel = connect_ssh_agent(userName)
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
    print('fetching data for ssh channel of is completed', userName)
    print('closing channel for ssh agent ', userName)
    channel.close()
    print('closed channel for ssh agent ', userName)
    return buffer

# Simulate multiple heavy data fetching functions
def fetch_resource_1h():
    historical_data_1h = get_historical_data("hist1h")
    parsed_hist1h_data = parse_hist1h_data(historical_data_1h)
    return parsed_hist1h_data


def fetch_resource_1m():
    historical_data_1m = get_historical_data("hist1m")
    parsed_hist1m_data = parse_hist1m_data(historical_data_1m)
    return parsed_hist1m_data

def fetch_resource_1s():
    historical_data_1s = get_historical_data("hist1s")
    parsed_hist1s_data = parse_hist1s_data(historical_data_1s)
    return parsed_hist1s_data

# Background fetching function to run in parallel
def fetch_all_historical_resources():
    parsed_hist1s_data = [None]
    parsed_hist1m_data = [None]
    parsed_hist1h_data = [None]
    
    def cached_fetch_resource_1h():
        parsed_hist1h_data[0] = fetch_resource_1h()

    def cached_fetch_resource_1m():
        parsed_hist1m_data[0] = fetch_resource_1m()

    def cached_fetch_resource_1s():
        parsed_hist1s_data[0] = fetch_resource_1h()

    
    thread1 = threading.Thread(target=cached_fetch_resource_1h)
    thread2 = threading.Thread(target=cached_fetch_resource_1m)
    thread3 = threading.Thread(target=cached_fetch_resource_1s)

    # Start threads
    thread1.start()
    thread2.start()
    thread3.start()

    # Wait for all threads to finish
    thread1.join()
    thread2.join()
    thread3.join()

    return parsed_hist1s_data[0], parsed_hist1m_data[0], parsed_hist1h_data[0]

@st.cache_resource
def fetch_all_historical_resource_once():
    return fetch_all_historical_resources()

# Main function to monitor and fetch data
def main():
    st.set_page_config(layout="wide")
    # Start the threads to fetch all resources in parallel
    parsed_hist1s_data, parsed_hist1m_data, parsed_hist1h_data= fetch_all_historical_resource_once()
    print(parsed_hist1m_data)

    historic_data = defaultdict(deque)
    
    # channel_rt = connect_ssh_agent("rt")

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

    # Use the selected option to determine the time range
    selected_time_range = next((time_range for time_range in TimeRange if time_range.value == option), None)

    time_range_data = []
    if parsed_hist1s_data is not None and parsed_hist1m_data is not None and parsed_hist1h_data is not None:
        time_range_data = get_time_specific_data(selected_time_range.value, parsed_hist1s_data, parsed_hist1m_data, parsed_hist1h_data)
    
    print(time_range_data)

    # Create a line chart for historical data
    st.subheader(f"Historical Data for {selected_time_range.value}")
    
    if time_range_data:
        df_time_range = pd.DataFrame(time_range_data)
        
        # Ensure that the dataframe contains 'Timestamp' and 'Last Price' for plotting
        if 'Time' in df_time_range.columns and 'Last Price' in df_time_range.columns:
            fig = px.line(
                df_time_range,
                x='Time',
                y='Last Price',
                title=f"{selected_time_range.value} Price Trends",
                labels={'Time': 'Date/Time', 'Last Price': 'Price'},
                line_shape='linear',
            )
            fig.update_layout(xaxis_title='Date/Time', yaxis_title='Price', template='plotly_white')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data available for the selected time range.")

    # while True:
    #     # Fetch and display real-time data
    #     new_data_rt = get_real_time_data_rt(channel_rt, historic_data)
    #     if new_data_rt:
    #         table_data   _rt = pd.DataFrame(new_data_rt)
    #         table_data_rt['% Change'] = table_data_rt['% Change'].apply(lambda x: f"{x:.2f}%")
    #         counter_rt += 1
    #         sorted_table_rt = table_data_rt[['Symbol', 'Trend', 'Price', 'Change', '% Change']].drop_duplicates(subset=['Symbol']).sort_values(by='Symbol')
    #         container_rt.data_editor(
    #             sorted_table_rt,
    #             column_config={
    #                 "Symbol": st.column_config.TextColumn("Symbol"),
    #                 "Trend": st.column_config.LineChartColumn("Trend", width="medium"),
    #                 "Price": st.column_config.NumberColumn("Price"),
    #                 "Change": st.column_config.NumberColumn("Change"),
    #                 "% Change": st.column_config.NumberColumn("% Change"),
    #             },
    #             key=f"rt_data_{counter_rt}",
    #             hide_index=True,
    #             use_container_width=True
    #         )

    #     sleep(1)

if __name__ == "__main__":
    main()
