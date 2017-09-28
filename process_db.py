import sqlite3

from bfs import brutebfs
from search_problem import ArbitrageSearchProblem

def generate_exchange_tree(cursor, trusted_exchanges, depth=10000, earliest=False): # default take all data
  exchanges = [ exchange.lower() for exchange in trusted_exchanges]
  def get_data(exchange):
    if earliest:
      query = 'select * from {} order by datetime(timestamp) DESC limit {}'.format(exchange, depth)
    else:
      query = 'select * from {} limit {}'.format(exchange, depth)
    cursor.execute(query)
    descs = [ desc[0] for desc in cursor.description ]
    rows = cursor.fetchall()
    if earliest:
      rows.reverse()
    data = { tuple(desc.split('/')): [ (row[i], row[-1]) for row in rows ] for i, desc in enumerate(descs) if desc != 'index' and desc != 'timestamp' }
    def process_prices(from_, to, prices):
      if to == 'USD':
        return prices
      # coin to coin is weird
      # for ex: it will say ETH/BTC is $282.51, which clearly doesn't make sense
      # this means we get $282.51 worth of BTC for 1 ETH
      # (which is usually pretty close to the amount we can get for a cashout)
      def convert(price, time):
        to_in_dollars, _ = data[(to, 'USD')][time]
        return price / to_in_dollars
      return [ (convert(price, i), timestamp) for i, (price, timestamp) in enumerate(prices) ]
    data = { key: process_prices(*key, prices) for key, prices in data.items() }
    inverse_data = { (to, from_): [ (1/price, timestamp) for (price, timestamp) in prices ] for (from_, to), prices in data.items() }
    return {**data, **inverse_data}
  return { exchange: get_data(exchange) for exchange in exchanges }

# TODO
if __name__ == '__main__':
  depth = 3
  exchange_tree = get_exchange_tree(depth)
  #print(exchange_tree)
  problem = ArbitrageSearchProblem(exchange_tree, depth)
  best_actions, best_value = brutebfs(problem)
  print(best_value)
  print(list(best_actions))
