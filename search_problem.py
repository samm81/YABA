class ArbitrageSearchProblem():
  def __init__(self, exchange_to_data, start_exchange='bank', start_currency='USD', start_amount=100, steps_limit=3):
    self.exchange_to_data = exchange_to_data
    self.start_exchange = start_exchange
    self.start_currency = start_currency
    self.start_amount = start_amount
    self.steps_limit = steps_limit

  def getStartState(self):
    return (self.start_exchange, self.start_currency, 0, self.start_amount, False)

  def isGoalState(self, state):
    _, currency, _, _, _ = state
    return currency == 'USD'

  fees = {
      'btcc': {
        'trade': lambda a: a * (1 - 0.002),
        'withdrawl': {
          'USD': lambda a: a - 0.001,
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
      }
    }
#Gemini
#  - triangle: 0.25%
#  - withdrawal: free
#Bitfinex
#  - triangle: 0.200%
#  - withdrawal
#    + BTC: 0.0004
#    + ETH: 0.01
#    + USD: 0.1%
#Bitstamp
#  - triangle: 0.25%
#  - withdrawal
#    + BTC: free
#    + ETH: free
#    + USD: 3.45

  def getSuccessors(self, state):
    fee_orig = lambda a: a * (1 - .0025)
    fee = fee_orig
    etd = self.exchange_to_data
    exchange, currency, steps, amount, already_transferred = state

    if exchange == 'bank':
      assert currency == 'USD'
      assert steps == 0
      return [ (exchange_, currency, steps, amount, False) for exchange_, data in etd.items() if any([ from_ == currency for (from_, to), _ in data.items() ]) ]

    try:
      fee_ = self.fees[exchange]['trade']
      assert type(fee_) == type(lambda a: a)
      fee = fee_
    except KeyError:
      pass

    succs = []
    if not already_transferred:
      succs += [ (exchange, to, steps, fee(prices[steps][0] * amount), True) for (from_, to), prices in etd[exchange].items() if from_ == currency ]

    if steps >= self.steps_limit:
      return succs

    succs += [ (exchange, currency, steps + 1, amount, already_transferred) ] # just hold the money for an hour

    if currency == 'USD':
      return succs # we don't need to calculate trading USD to another exchange...

    try:
      fee_ = self.fees[exchange]['withdrawl']
      if not type(fee_) == type(lambda a: a):
        fee_ = fee_[currency]
      assert type(fee_) == type(lambda a: a)
      fee = fee_
    except KeyError:
      fee = fee_orig

    succs += [ (exchange_, currency, steps + 1, fee(amount), False) for exchange_, data in etd.items() if any([ from_ == currency for (from_, to), _ in data.items() ]) and exchange_ != exchange ]
    return succs

