def arbitrageBFS(problem):
  start = problem.getStartState()
  q = []
  q.append(start)
  back = {}
  back[start] = None

  bestActions = []
  bestValue = 0

  while len(q) > 0:
    cur = q.pop(0)
    exchange, currency, time, amount, _ = cur

    if problem.isGoalState(cur):
      if amount > bestValue:
        bestValue = amount
        actions = [cur]
        while cur != start:
          back_node, _ = back[(cur[0], cur[1], cur[2])]
          actions.append(back_node)
          cur = back_node
        bestActions = reversed(actions)

    for succ in problem.getSuccessors(cur):
      state = (succ[0], succ[1], succ[2])
      if (state in back and back[state][1] < succ[3]) or state not in back:
        q.append(succ)
        back[state] = (cur, succ[3])

  return (list(bestActions), bestValue)

class TestProblem():
  def __init__(self, trades, start):
    self.trades = trades # (exchange, currency, time) -> (succs, conversion_rate)
    self.start = start # (exchange, currency, time, amount)

  def getStartState(self):
    return self.start

  def isGoalState(self, state):
    # can change this to also match same market
    _, start_currency, _, _, _ = self.start
    _, currency, _, _, _ = state
    return start_currency == currency

  # return format [ (exchange, currency, time, amount), ... ]
  def getSuccessors(self, state):
    succs = []
    exchange, currency, time, amount, stayed = state
    for succ, conversion_rate in self.trades[(exchange, currency, time, stayed)]:
      exchange_, currency_, time_, stayed_ = succ
      succs.append( (exchange_, currency_, time_, amount * conversion_rate, stayed_) )
    return succs

if __name__ == '__main__':
  from collections import defaultdict
  trades = defaultdict(list)
  trades[('A', '$', 0, False)] = [(('A', 'BTC', 0, True), .2), (('A', 'ETH', 0, True), 10)]
  trades[('A', 'BTC', 0, True)] = [(('B', 'BTC', 1, False), 1.01), (('C', 'BTC', 1, False), 0.98)]
  trades[('B', 'BTC', 1, False)] = [(('B', '$', 1, True), 6.02)]
  trades[('C', 'BTC', 1, False)] = [(('C', '$', 1, True), 5.5)]
  start = ('A', '$', 0, 1, False)
  problem = TestProblem(trades, start)
  best_actions, best_value = arbitrageBFS(problem)
  print(best_value)
  print(list(best_actions))
