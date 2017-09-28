import sqlite3

from bfs import brutebfs
from process_db import generate_exchange_tree
from prediction import generate_predictions_tree
from search_problem import ArbitrageSearchProblem

# get exchange tree with n earliest data points
# feed to generate_prediction_tree
# call BFS for actions
# simulate actions on real history

look_back = 115 # ideally, v high
look_ahead = 3
capital = 100

con = sqlite3.connect('prices.db')
cur = con.cursor()
prefix_tree = generate_exchange_tree(cur, look_back, True)
prediction_tree = generate_predictions_tree(prefix_tree, look_ahead)
prob = ArbitrageSearchProblem(prediction_tree, start_amount=capital)
bestActions, bestValue = brutebfs(prob)
print(bestActions)

time = 0
real_tree = generate_exchange_tree(cur, 1000, True)
for i in range(1, len(bestActions) - 1):
  exchange, currency, next_time, _, _ = bestActions[i]
  next_exchange, next_currency, _, _, _ = bestActions[i+1]
  if currency != next_currency:
    real_time = (time * 12) + look_back
    capital *= real_tree[exchange][(currency, next_currency)][real_time][0]
    capital *= 1 - 0.0005
  time = next_time
  if exchange != next_exchange:
    capital *= 1 - 0.0005
  print(capital)

print("expected value: ${}".format(bestValue))
print("actual value: ${}".format(capital))
