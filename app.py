import pandas as pd
import panel as pn
from datetime import datetime
from datetime import date, timedelta
pn.extension('bokeh', template='bootstrap')
import hvplot.pandas
import os
import yfinance as yf

@pn.cache
def getPolygonDF(ticker , startdate , enddate , intervalperiod , window, window2):
    import json
    import time
    import pandas as pd
    import requests

    #My Polygon API (need to define in huggingface env variable)
    # mypolgonAPI = os.environ.get('mypolgonAPI') 
    
    #to get key from json file
    with open('config.json') as config_file:
        config = json.load(config_file)
    mypolgonAPI  = config['mypolgonAPI']

    headers = {"Authorization": f"Bearer {mypolgonAPI}"}

    interval = "minute"
    period = intervalperiod #"5"
    limit = 50000

    dflst = [] 
    nexturl = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{period}/{interval}/{startdate}/{enddate}?adjusted=true&sort=asc&limit={limit}"
    while True:
        r1 = requests.get(nexturl , headers=headers)
        print(r1)
        df = pd.DataFrame(json.loads(r1.text)["results"])
        df['UNIXTIME'] = pd.to_datetime(df['t'], unit='ms', utc=True).map(lambda x: x.tz_convert('America/New_York'))
        dflst.append(df)
        print(df.shape)
        # time.sleep(15)
        try:
            nexturl = json.loads(r1.text)["next_url"] 
        except:
            break
    DF = pd.concat(dflst)
    DF['SMA'] = DF.c.rolling(window=window).mean()
    DF['SMA2'] = DF.c.rolling(window=window2).mean()
    return DF

def get_hvplot(ticker , startdate ,  interval,window,window2):
    date_end = date_start.value + timedelta(days=1) # date.today()
    DF = getPolygonDF(ticker , startdate=startdate , enddate=date_end , intervalperiod=interval,window=window,window2=window2)

    import hvplot.pandas  # Ensure hvplot is installed (pip install hvplot)

    import holoviews as hv
    hv.extension('bokeh')

    # Create a scatter plot using hvplot
    scatter_plot = DF.hvplot(x='UNIXTIME', y='c',  kind='scatter',title=f'{ticker} Close vs. Date')

    line_plot_SMA = DF.hvplot(x='UNIXTIME', y='SMA', kind='line',line_dash='dashed', color='orange')
    line_plot_SMA2 = DF.hvplot(x='UNIXTIME', y='SMA2', kind='line',line_dash='dashed', color='orange')

    return (scatter_plot *line_plot_SMA *line_plot_SMA2).opts(width=800, height=600, show_grid=True)


tickers = ['AAPL', 'META', 'GOOG', 'IBM', 'MSFT','NKE','DLTR','DG']
# ticker = pn.widgets.Select(name='Ticker', options=tickers)

# tickers = pd.read_csv('tickers2.csv').Ticker.to_list()
ticker = pn.widgets.AutocompleteInput(name='Ticker', options=tickers , placeholder='Write Ticker here همین جا')
ticker.value = "AAPL"
window = pn.widgets.IntSlider(name='Window Size', value=50, start=5, end=1000, step=5)
window2 = pn.widgets.IntSlider(name='Window Size2', value=150, start=5, end=1000, step=5)

# Create a DatePicker widget with a minimum date of 2000-01-01
date_start = pn.widgets.DatePicker(
    name ="Start Date",
    description='Select a Date',
    start= date.today() - timedelta(days=365 * 2)
)

# date_end = pn.widgets.DatePicker(
#     name ="End Date",# value=datetime(2000, 1, 1),
#     description='Select a Date',
#     end= date.today() - timedelta(days=365 * 2) + timedelta(days=1)  #date.today() #date(2023, 9, 1)
# )

date_start.value = date.today() - timedelta(days=200 * 2)
# date_end = date_start.value + timedelta(days=1) # date.today()

menu_button = pn.widgets.Select(name='Time Frame (min)', options=['1', '5', '10'])

pn.Row(
    pn.Column( ticker, window , window2, date_start , menu_button),
    # pn.bind(calc_fairprice_CDF,ticker),
    # pn.bind(calc_fairprice_DnetP,ticker)),
    # pn.panel(pn.bind(get_hvplot, ticker, "2010-01-01","2023-09-01","1d")) #, sizing_mode='stretch_width')
    pn.panel(pn.bind(get_hvplot, ticker, date_start , menu_button,window,window2)), #, sizing_mode='stretch_width')
    # pn.panel(pn.bind(get_income_hvplot, ticker))    #, sizing_mode='stretch_width')    
).servable(title="Intraday Price Action - Pattern Detection")