from datetime import datetime, timedelta
from constants.timeRange import TimeRange

def get_time_specific_data(time_range, parsed1s_data, parsed1m_data, parsed1h_data):
    current_date = datetime.now()

    match time_range:
        # Hourly aggregations
        case TimeRange.LAST_YEAR_HOURLY.value:
            start_date = datetime(current_date.year - 1, 1, 1)  # 1st Jan of last year
            end_date = datetime(current_date.year, 8, 31, 23, 59, 59)  # End of August this year
            filtered_data = [data for data in parsed1h_data if start_date <= datetime.strptime(data['Time'], '%d.%m.%Y %H:%M:%S') <= end_date]
            return filtered_data
        
        case TimeRange.CURRENT_YEAR_HOURLY.value:
            start_date = datetime(current_date.year, 1, 1)  # 1st Jan of current year
            end_date = current_date.replace(hour=23, minute=59, second=59)
            filtered_data = [data for data in parsed1h_data if start_date <= datetime.strptime(data['Time'], '%d.%m.%Y %H:%M:%S') <= end_date]
            return filtered_data

        case TimeRange.CURRENT_YEAR_Q1_HOURLY.value:
            start_date = datetime(current_date.year, 1, 1)  # Q1 start
            end_date = datetime(current_date.year, 3, 31, 23, 59, 59)  # Q1 end
            filtered_data = [data for data in parsed1h_data if start_date <= datetime.strptime(data['Time'], '%d.%m.%Y %H:%M:%S') <= end_date]
            return filtered_data

        case TimeRange.CURRENT_YEAR_Q2_HOURLY.value:
            start_date = datetime(current_date.year, 4, 1)  # Q2 start
            end_date = datetime(current_date.year, 6, 30, 23, 59, 59)  # Q2 end
            filtered_data = [data for data in parsed1h_data if start_date <= datetime.strptime(data['Time'], '%d.%m.%Y %H:%M:%S') <= end_date]
            return filtered_data

        case TimeRange.CURRENT_YEAR_Q3_HOURLY.value:
            start_date = datetime(current_date.year, 7, 1)  # Q3 start
            end_date = datetime(current_date.year, 9, 30, 23, 59, 59)  # Q3 end
            filtered_data = [data for data in parsed1h_data if start_date <= datetime.strptime(data['Time'], '%d.%m.%Y %H:%M:%S') <= end_date]
            return filtered_data

        case TimeRange.CURRENT_YEAR_Q4_HOURLY.value:
            start_date = datetime(current_date.year, 10, 1)  # Q4 start
            end_date = current_date  # Current time
            filtered_data = [data for data in parsed1h_data if start_date <= datetime.strptime(data['Time'], '%d.%m.%Y %H:%M:%S') <= end_date]
            return filtered_data

        case TimeRange.LAST_6_MONTHS_HOURLY.value:
            start_date = current_date - timedelta(days=6*30)  # Approximation of 6 months
            end_date = current_date
            filtered_data = [data for data in parsed1h_data if start_date <= datetime.strptime(data['Time'], '%d.%m.%Y %H:%M:%S') <= end_date]
            return filtered_data

        # Minute aggregations
        case TimeRange.LAST_MONTH_MINUTE.value:
            start_date = datetime(current_date.year, current_date.month - 1, 1)  # Start of last month
            end_date = current_date.replace(day=1) - timedelta(days=1)  # Last day of last month
            filtered_data = [data for data in parsed1m_data if start_date <= datetime.strptime(data['Time'].strip(), '%Y%m%d %H:%M:%S') <= end_date]
            return filtered_data

        case TimeRange.LAST_WEEK_MINUTE.value:
            start_date = current_date - timedelta(days=7)  # 7 days ago
            end_date = current_date
            filtered_data = [data for data in parsed1m_data if start_date <= datetime.strptime(data['Time'], '%Y%m%d %H:%M:%S') <= end_date]
            return filtered_data

        # Second aggregations
        case TimeRange.YESTERDAY_SECOND.value:
            start_date = (current_date - timedelta(days=1)).replace(hour=0, minute=0, second=0)  # Yesterday 12 AM
            end_date = start_date.replace(hour=23, minute=59, second=59)  # Yesterday 11:59 PM
            filtered_data = [data for data in parsed1s_data if start_date <= datetime.strptime(data['Time'], '%Y%m%d %H:%M:%S') <= end_date]
            return filtered_data

        case TimeRange.TODAY_SECOND.value:
            start_date = current_date.replace(hour=0, minute=0, second=0)  # Today 12 AM
            end_date = current_date  # Current time today
            filtered_data = [data for data in parsed1s_data if start_date <= datetime.strptime(data['Time'], '%Y%m%d %H:%M:%S') <= end_date]
            return filtered_data

        case TimeRange.LAST_12HR_SECOND.value:
            start_date = current_date - timedelta(hours=12)  # 12 hours ago
            end_date = current_date  # Current time
            filtered_data = [data for data in parsed1s_data if start_date <= datetime.strptime(data['Time'], '%Y%m%d %H:%M:%S') <= end_date]
            return filtered_data

        case TimeRange.LAST_24HR_SECOND.value:
            start_date = current_date - timedelta(hours=24)  # 24 hours ago
            end_date = current_date  # Current time
            filtered_data = [data for data in parsed1s_data if start_date <= datetime.strptime(data['Time'], '%Y%m%d %H:%M:%S') <= end_date]
            return filtered_data

        case _:
            return []  # No data for the time range

__all__ = ['get_time_specific_data']
