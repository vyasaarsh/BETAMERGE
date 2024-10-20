from collections import deque

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
    date = None
    for line in lines:
        if line.startswith('!'):
            parts = line.split(',')
            if len(parts) >= 2:
                date, timestamp = parts[:2]
                parsed_data.append({'Type': 'timestamp', 'Date': date, 'Time': timestamp})
            else:
                continue
        else:
            try:
                symbol, last_price, _ = line.split(',')
                parsed_data.append({'Symbol': symbol, 'Last Price': float(last_price)})
            except ValueError:
                continue
    return parsed_data

# Parse Historical (hist1m) data from SSH connection
def parse_hist1m_data(data):
    lines = data.strip().split('\n')
    parsed_data = []
    date = None
    for line in lines:
        if line.startswith('!'):
            parts = line.split(',')
            if len(parts) == 2:
                date, timestamp = parts
                timestamp = f"{timestamp}:00"
                parsed_data.append({'Type': 'timestamp', 'Date': date, 'Time': timestamp})
            else:
                continue
        else:
            try:
                symbol, last_price, _ = line.split(',')
                parsed_data.append({'Symbol': symbol, 'Last Price': float(last_price)})
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