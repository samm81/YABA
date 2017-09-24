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

  def getSuccessors(self, state):
    fee = (1 - .0025)
    etd = self.exchange_to_data
    exchange, currency, steps, amount, already_transferred = state

    if exchange == 'bank':
      assert currency == 'USD'
      assert steps == 0
      return [ (exchange_, currency, steps, amount, False) for exchange_, data in etd.items() if any([ from_ == currency for (from_, to), _ in data.items() ]) ]

    succs = []
    if not already_transferred:
      succs += [ (exchange, to, steps, prices[steps][0] * amount * fee, True) for (from_, to), prices in etd[exchange].items() if from_ == currency]

    if steps >= self.steps_limit:
      return succs

    succs += [ (exchange, currency, steps + 1, amount, already_transferred) ] # just hold the money for an hour

    if currency == 'USD':
      return succs # we don't need to calculate trading USD to another exchange...

    succs += [ (exchange_, currency, steps + 1, amount * fee, False) for exchange_, data in etd.items() if any([ from_ == currency for (from_, to), _ in data.items() ]) and exchange_ != exchange ]
    return succs

