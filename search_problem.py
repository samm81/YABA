from collections import namedtuple

ArbitrageSearchNode = namedtuple('ArbitrageSearchNode', ['exchange', 'currency', 'amount', 'timestep', 'already_transferred'])

class ArbitrageSearchProblem():
  default_start_node = ArbitrageSearchNode('bank', 'USD', 100, 0, False)

  def __init__(self, exchange_data, start_node=default_start_node, depth_limit=5):
    self.exchange_data = exchange_data
    self.start_node = start_node
    self.depth_limit = depth_limit

  def getStartState(self):
    return self.start_node

  def isGoalState(self, state):
    return state.currency == 'USD'

  def value(self, state):
    return state.amount

  fees = {
      'btcc': {
        'trade': lambda a: a * (1 - 0.002),
        'withdrawl': {
          'BTC': lambda a: a - 0.001,
          'USD': lambda a: a * (1 - 0.003)
        }
      },
      'kraken': {
        'trade': lambda a: a * (1- 0.0026),
        'withdrawl': {
          'BTC': lambda a: a - 0.001,
          'ETH': lambda a: a - 0.005,
          'USD': lambda a: a - 5
        }
      },
      'gdax': {
        'trade': lambda a: a * (1 - 0.003),
        'withdrawl': lambda a: a
      },
      'gemini': {
        'trade': lambda a: a * (1 - 0.0025),
        'withdrawl': lambda a: a,
      },
      'bitfinex': {
        'trade': lambda a: a * (1 - .002),
        'withdrawl': {
          'BTC': lambda a: a - .0004,
          'ETH': lambda a: a - 0.01,
          'USD': lambda a: a * (1- .001)
        }
      },
      'bitstamp': {
        'trade': lambda a: a * (1 - .0025),
        'withdrawl': {
          'BTC': lambda a: a,
          'ETH': lambda a: a,
          'USD': lambda a: a - 3.45,
        }
      }
    }

  def getSuccessors(self, state):
    exchange_data = self.exchange_data
    exchange, currency, amount, timestep, already_transferred = state

    if exchange == 'bank': # then we can bring our USD to any exchange
      assert currency == 'USD'
      assert timestep == 0
      return [
        ArbitrageSearchNode(exchange_, currency, amount, timestep, False)
        for exchange_, data in exchange_data.items()
        if any([ from_ == currency for (from_, to), _ in data.items() ]) # though really they should all have USD...
      ]

    fee_ = self.fees[exchange]['trade']
    assert type(fee_) == type(lambda a: a)
    fee = fee_

    successors = []
    if not already_transferred:
      successors += [
        ArbitrageSearchNode(exchange, to, fee(prices[timestep][0] * amount), timestep, True)
        for (from_, to), prices in exchange_data[exchange].items()
        if from_ == currency
      ]

    # all successors past here will increase the timestep, so if we've maxed out, just return what we have
    if timestep >= self.depth_limit:
      return successors

    # just hold the money for an hour
    successors += [ ArbitrageSearchNode(exchange, currency, amount, timestep + 1, already_transferred) ]

    # we don't need to calculate trading USD to another exchange...
    if currency == 'USD':
      return successors

    fee_ = self.fees[exchange]['withdrawl']
    if not type(fee_) == type(lambda a: a):
      fee_ = fee_[currency]
    assert type(fee_) == type(lambda a: a)
    fee = fee_

    successors += [
      ArbitrageSearchNode(exchange_, currency, fee(amount), timestep + 1, False)
      for exchange_, data in exchange_data.items()
      if (exchange_ != exchange # don't transfer to current exchange
        and any([ from_ == currency for (from_, to), _ in data.items() ]))
    ]

    return successors
