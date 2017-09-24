import os
import pandas
import sqlite3
from fbprophet import Prophet
import crayons

from scraper import trusted_exchanges
from process_db import generate_exchange_tree, ArbitrageSearchProblem
from bfs import arbitrageBFS

# stolen from https://github.com/facebookincubator/prophet/issues/223
class suppress_stdout_stderr(object):
  '''
  A context manager for doing a "deep suppression" of stdout and stderr in
  Python, i.e. will suppress all print, even if the print originates in a
  compiled C/Fortran sub-function.
     This will not suppress raised exceptions, since exceptions are printed
  to stderr just before a script exits, and after the context manager has
  exited (at least, I think that is why it lets exceptions through).

  '''
  def __init__(self, suppress_output):
    self.suppress_output = suppress_output
    if not self.suppress_output:
      return
    # Open a pair of null files
    self.null_fds = [os.open(os.devnull, os.O_RDWR) for x in range(2)]
    # Save the actual stdout (1) and stderr (2) file descriptors.
    self.save_fds = [os.dup(1), os.dup(2)]

  def __enter__(self):
    if not self.suppress_output:
      return
    # Assign the null pointers to stdout and stderr.
    os.dup2(self.null_fds[0], 1)
    os.dup2(self.null_fds[1], 2)

  def __exit__(self, *_):
    if not self.suppress_output:
      return
    # Re-assign the real stdout/stderr back to (1) and (2)
    os.dup2(self.save_fds[0], 1)
    os.dup2(self.save_fds[1], 2)
    # Close the null files
    for fd in self.null_fds + self.save_fds:
        os.close(fd)

# input is a double layered dict with exchange -> (fromType, toType) -> sequence of modeled exchange rates
def generate_predictions_tree(history, distance=3, suppress_output=True, render=False):
  prediction_tree = {}
  for exchange, crypto_pairs in history.items():
    print(crayons.cyan('    predicting {} hours into the future for {} exchange...'.format(distance, exchange)))
    prediction_tree[exchange] = {}
    figures = []
    for exchange_pair, rates in crypto_pairs.items():
      (from_, to) = exchange_pair
      df = pandas.DataFrame(rates)
      df.columns = ['y', 'ds']
      with suppress_stdout_stderr(suppress_output):
        ml = Prophet()
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
  best_actions, best_value = arbitrageBFS(problem)
  print(best_value)
  print(list(best_actions))
