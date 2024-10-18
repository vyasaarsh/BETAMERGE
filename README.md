# BETAMERGE

example currentDate -> 18 / 10 / 2024

# 1s

StartDate -> Yesterday 12 AM (i.e. 17/10/2024 12AM)
EndDate -> Current time (i.e. 18/10/2024 -> currentTime)
Aggregation -> Every second

# 1m

StartDate -> start of last month (i.e. 1/9/2024 12AM)
EndDate -> currentDate - 1 completed day (till 11:59PM) (i.e. 16/10/2024 11:59PM)
Aggregation -> Every minute

# 1h

StartDate -> 1st Jan of last year (i.e. 1/1/2023)
EndDate -> 1 completed month earlier (i.e. 31 / 8 / 2024)
Aggregation -> hourly data

Removed ->
| This month | minute | 1m |
| Last 30 days | minute | 1m |
| This week | minute | 1m |

| TimeRange | Aggregation | Id |
| Last year | hourly | 1h |
| Current year | hourly | 1h |
| Current year -> Q1,2,3,4 | hourly | 1h |
| Last 6 months | hourly | 1h |
| Last month | minute | 1m |
| Last week | minute | 1m |
| Yesterday | second | 1s |
| Today | second | 1s |
| Last 12hr | second | 1s |
| Last 24hr | second | 1s |

Challenge -> where to store data?

-> Each code run will fetch data for 1s, 1m, 1h historical data
-> These historical data would be stored in local variables

Challenge -> How will you get updated data everyday?

-> Restart your server everyday in downtime -> (10min) (Is it okay with clients?)

**Pros:**
-> Use-case is solved

**Cons:**
-> Initial load time would be steap
-> Memory usage could be higher

## What is the deployment procedure?

Not in place

**No specific requirements for deploymenys**
