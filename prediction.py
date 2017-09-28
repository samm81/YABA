import pandas
import sqlite3
from fbprophet import Prophet
import crayons

from process_db import generate_exchange_tree, ArbitrageSearchProblem
from bfs import brutebfs
from suppress_stdout_stderr import suppress_stdout_stderr

def generate_predictions_tree(history, distance=5, suppress_prophet_output=True, render=False):
  prediction_tree = {}
  for exchange, coin_pairs in history.items():
    print(crayons.cyan('    predicting {} hours into the future for {} exchange...'.format(distance, exchange)))
    prediction_tree[exchange] = {}
    figures = []
    for exchange_pair, prices in coin_pairs.items():
      (from_, to) = exchange_pair
      df = pandas.DataFrame(prices)
      df.columns = ['y', 'ds']
      with suppress_stdout_stderr(suppress_prophet_output):
        ml = Prophet(changepoint_prior_scale=0.9)
        ml.fit(df)
        future = ml.make_future_dataframe(periods=distance, freq='1H', include_history=False)
        forecast = ml.predict(future)

      if render:
        label = '{} {}/{}'.format(exchange, from_, to)
        figure = ml.plot(forecast, xlabel='time', ylabel=label)
        figure.suptitle(label)
        figures.append(figure)

      forecast_set = forecast[['yhat']]
      tuple_list = [(x[0], 0) for x in forecast_set.values]
      tuple_list = [ ( df['y'][df.index[-1]], 0 ) ] + tuple_list # add t=now back in
      prediction_tree[exchange][exchange_pair] = tuple_list

    if render:
      for figure in figures:
        figure.show()
      print(crayons.white('    (enter to continue, "skip" to skip rest) '), end='')
      i = input()
      render = (i != 'skip')

  return prediction_tree

if __name__ == '__main__':
  depth = 3
  cur = sqlite3.connect('prices.db').cursor()
  prediction_tree = generate_predictions_tree(generate_exchange_tree(cur, depth=1000), depth)
  print(prediction_tree)
  problem = ArbitrageSearchProblem(prediction_tree, depth)
  best_actions, best_value = brutebfs(problem)
  print(best_value)
  print(list(best_actions))
