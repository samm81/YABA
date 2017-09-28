import pandas
import requests
from pyquery import PyQuery as pq
import sqlite3
from collections import defaultdict
from datetime import datetime

import crayons

from yaba import trusted_exchanges
from yaba import tickers

exchange_to_series = defaultdict(dict)
exchange_tickers = tickers + [ 'usd' ]
ticker_to_coin = { 'btc': 'bitcoin', 'eth': 'ethereum' }
coins = [ ticker_to_coin[ticker] for ticker in tickers ]

session = requests.Session()

if __name__ == '__main__':
  conn = sqlite3.connect('/v/filer5b/v38q001/maynard/hackrice/prices.db')

  master_df = pandas.DataFrame()

  print(crayons.yellow('Scraping coins {}...'.format(coins)))

  for ticker, coin in [ (ticker, ticker_to_coin[ticker]) for ticker in tickers ]:
    print(crayons.green('Scraping {}'.format(coin)))

    url = 'https://coinmarketcap.com/currencies/{}/#markets'.format(coin)

    r = session.get(url)
    html = pq(pq(r.content)('table')[0]).html()
    df = pandas.read_html('<table>{}</table>'.format(html), index_col=0)
    df = pandas.concat(df)

    df = df.filter(items=['Pair', 'Source', 'Price' ])
    df = df.loc[df['Source'].isin(trusted_exchanges)]
    df['Price'] = df['Price'].map(lambda price_str: float(price_str[price_str.index('$') + 1:]))

    exchange_pairs = [ '{}/{}'.format(ticker.upper(), to_ticker.upper()) for to_ticker in exchange_tickers ]
    df = df.loc[df['Pair'].isin(exchange_pairs)]

    def add_to_exchange_series(exchange):
      currencies = df.loc[df['Source'] == exchange, 'Pair'].values
      prices = df.loc[df['Source'] == exchange, 'Price'].values
      for currency, price in zip(currencies, prices):
        exchange_to_series[exchange][currency] = price
    df['Source'].map(lambda source: add_to_exchange_series(source))

  print(crayons.yellow('Finished scraping.'))

  print(crayons.yellow('Compiled the following data....'))
  for exchange, dict_ in exchange_to_series.items():
    print(crayons.green(exchange))
    df = pandas.Series(dict_).to_frame().transpose()
    df['timestamp'] = [ datetime.now() ]
    print(df)
    print(crayons.yellow('writing to db...'))
    df.to_sql(exchange.lower(), conn, if_exists='append')

  #conn.commit() DO NOT RE-ADD
  conn.close()

  print(crayons.yellow('Finished.'))
  print()
