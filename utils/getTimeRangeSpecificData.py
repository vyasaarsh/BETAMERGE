from constants.timeRange import TimeRange

def get_time_specific_data(time_range, parsed1s_data, parsed1m_data, parsed1h_data):
  match time_range:
    case TimeRange.LAST_YEAR_HOURLY | TimeRange.CURRENT_YEAR_HOURLY | TimeRange.CURRENT_YEAR_Q1_HOURLY | TimeRange.CURRENT_YEAR_Q2_HOURLY | TimeRange.CURRENT_YEAR_Q3_HOURLY | TimeRange.CURRENT_YEAR_Q4_HOURLY | TimeRange.LAST_6_MONTHS_HOURLY:
      return parsed1h_data
    case TimeRange.LAST_MONTH_MINUTE | TimeRange.LAST_WEEK_MINUTE:
      return parsed1m_data
    case TimeRange.YESTERDAY_SECOND | TimeRange.TODAY_SECOND | TimeRange.LAST_12HR_SECOND | TimeRange.LAST_24HR_SECOND:
      return parsed1s_data
    case _:
      return []

__all__ = ['get_time_specific_data']