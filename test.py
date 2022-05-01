import time
import pandas as pd
import datetime

ticker = 'MSFT'
START = int(time.mktime(datetime.datetime(2016, 1, 5, 23, 59).timetuple()))
START = datetime.datetime(2021, 6, 28)
#START = datetime.date.today()
START = int(time.mktime(START.timetuple()))
print(START)

# END = int(time.mktime(datetime.datetime(2021, 6, 25, 23, 59).timetuple()))

# query_string = f'https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={START}&period2={END}&interval=1d&events=history&includeAdjustedClose=true'
# df = pd.read_csv(query_string)
# df.set_index('Date', inplace=True)
# print(df.tail())

exit()
