from collections import deque
from datetime import datetime

# Parse Real-Time (rt) data from SSH connection
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

# Parse Historical (hist1s) data from SSH connection
def parse_hist1s_data(data):
    lines = data.strip().split('\n')
    parsed_data = []
    current_date = None
    current_timestamp = None
    
    for line in lines:
        if line.startswith('!'):
            # Parse timestamp line
            date, time = line[1:].split(',')  # Remove '!' and split
            current_date = date.strip()
            time = time.strip().replace('\r', '').replace('\n', '')
            if len(time.split(':')) == 2:
                time += ':00'
            current_timestamp = f"{current_date} {time}"  # Time already includes seconds
        else:
            try:
                # Parse data line (symbol, price, ignored)
                symbol, last_price, _ = line.split(',')
                if not current_date:
                    continue
                parsed_data.append({
                    'Symbol': symbol,
                    'Last Price': float(last_price),
                    'Date': current_date,
                    'Time': current_timestamp
                })
            except ValueError:
                continue
    
    return parsed_data

# Parse Historical (hist1m) data from SSH connection
def parse_hist1m_data(data):
    lines = data.strip().split('\n')
    parsed_data = []
    current_date = None
    current_timestamp = None
    
    for line in lines:
        if line.startswith('!'):
            # Parse timestamp line
            date, time = line[1:].split(',')  # Remove '!' and split
            current_date = date.strip()
            time = time.strip().replace('\r', '').replace('\n', '')
            if len(time.split(':')) == 2:
                time += ':00'
            current_timestamp = f"{current_date} {time}"
        else:
            try:
                # Parse data line (symbol, price, ignored)
                symbol, last_price, _ = line.split(',')
                if not current_date:
                    continue
                parsed_data.append({
                    'Symbol': symbol,
                    'Last Price': float(last_price),
                    'Date': current_date,
                    'Time': current_timestamp
                })
            except ValueError:
                continue
    
    return parsed_data


# Parse Historical (hist1h) data from SSH connection
def parse_hist1h_data(data):
    lines = data.strip().split('\n')
    parsed_data = []
    current_symbol = None
    
    for line in lines:
        if line.startswith('#'):
            current_symbol = line[1:].strip()
        else:
            try:
                date, timestamp, last_price, _ = line.split(',')
                timestamp = f"{date} {timestamp}:00:00"
                parsed_data.append({
                    'Symbol': current_symbol,
                    'Last Price': float(last_price),
                    'Date': date,
                    'Time': timestamp
                })
            except ValueError:
                continue
    
    return parsed_data

__all__ = ['parse_hist1h_data', 'parse_hist1m_data', 'parse_hist1s_data', 'parse_real_time_data']
