from enum import Enum

__all__ = ['TimeRange']

class TimeRange(Enum):
  LAST_YEAR_HOURLY = "Last year"
  CURRENT_YEAR_HOURLY = "Current year"
  CURRENT_YEAR_Q1_HOURLY = "Current year -> Q1"
  CURRENT_YEAR_Q2_HOURLY = "Current year -> Q2"
  CURRENT_YEAR_Q3_HOURLY = "Current year -> Q3"
  CURRENT_YEAR_Q4_HOURLY = "Current year -> Q4"
  LAST_6_MONTHS_HOURLY = "Last 6 months"
  LAST_MONTH_MINUTE = "Last month"
  LAST_WEEK_MINUTE = "Last week"
  YESTERDAY_SECOND = "Yesterday"
  TODAY_SECOND = "Today"
  LAST_12HR_SECOND = "Last 12hr"
  LAST_24HR_SECOND = "Last 24hr"