""" Predict future arbitrage opportunities on major digital currency exchanges.

Usage:
  yaba [options] -d FILE

Options:
  -d --db-file          Price data sqlite3 database file..
  -f --figures          Show graphs and figures as they are calculated.
  --verbose             Print more output.
  -h --help             Show this screen
  --version             Show version.

Examples:
  yaba -d prices.db --verbose -f
    Presentation mode. Show all output, show graphs.
  yaba -d prices.db
    Minimal output mode.

"""
# depth
# log level
# starting exchange
# starting money
import sys
from docopt import docopt
import sqlite3
import crayons

from process_db import generate_exchange_tree
from prediction import generate_predictions_tree
from search_problem import ArbitrageSearchProblem
from bfs import brutebfs

tickers = [ 'btc', 'eth' ]
trusted_exchanges = [ 'Kraken', 'GDAX', 'Gemini', 'Bitfinex', 'Bitstamp' ] # BTCC

if __name__ == '__main__':
  """Main CLI entrypoint"""
  arguments = docopt(__doc__, version='Alpha')

  pricef = arguments['FILE']
  verbose = arguments['--verbose']
  figures = arguments['--figures']

  print('\n{} {} {}\n'.format(crayons.blue('Welcome to yaba (Yet Another Bitcoin Arbitrage).'), crayons.green('CA$H and CO1NZ', bold=True), crayons.blue('are in your future...')))

  print(crayons.yellow('loading prices database {}...'.format(pricef)))
  conn = None
  try:
    conn = sqlite3.connect(pricef)
  except Exception as e:
    print(crayons.red('failed to load sqlite3 database file {}!'.format(pricef)))
    print(crayons.red(e))
    print(crayons.red('exiting...'))
    sys.exit(1)

  print(crayons.yellow('generating exchange tree...'))
  exchange_tree = generate_exchange_tree(conn.cursor(), trusted_exchanges)

  print(crayons.yellow('predicting future values (this may take a while)...'))
  predictions_tree = generate_predictions_tree(exchange_tree, suppress_prophet_output=(not verbose), render=figures, distance=6)

  print(crayons.yellow('starting arbitrage search...'))
  arbitrage_search_problem = ArbitrageSearchProblem(predictions_tree, depth_limit=6)
  actions, result = brutebfs(arbitrage_search_problem)
  print(crayons.yellow('done!'))

  max_timestep = actions[-1].timestep
  print('\n{} {} {} {} {}\n'.format(crayons.blue('found a way to make'), crayons.red('${:.2f}'.format(result), bold=True), crayons.blue('in'), crayons.blue(max_timestep, bold=True), crayons.blue('hours')))

  def format_amount(amount, currency):
    if currency == 'USD':
      amount = '{:.2f}'.format(amount)
    else:
      amount = '{:.4f}'.format(amount)
    return amount

  for step, ((exchange1, currency1, amount1, time1, _), (exchange2, currency2, amount2, time2, _)) in enumerate(zip(actions, actions[1:])):
    amount1, amount2 = [ format_amount(amount, currency) for amount, currency in zip([amount1, amount2], [currency1, currency2]) ]
    step_str = 'step {}: '.format(step)
    if time1 == time2:
      if exchange1 == exchange2:
        step_str += 'take your {} {} on {} and buy {} {}'.format(amount1, currency1, exchange1, amount2, currency2)
      else:
        step_str += 'take your {} {} on {} and move it to {}'.format(amount1, currency1, exchange1, exchange2)
    else:
      if exchange1 == exchange2:
        step_str += 'hold on to your {} {} on {} for an hour'.format(amount1, currency1, exchange1)
      else:
        step_str += 'take your {} {} on {} and move it to {} (allow one hour for processing)'.format(amount1, currency1, exchange1, exchange2)
    print(crayons.magenta(step_str))

  print(crayons.blue('\nAll data provided here is provided purely for informational purposes only. We are not responsible for any losses you incur from these suggestions. (We will take the credit for gains ;) )\n'))

  print(crayons.yellow('closing database connection...'))
  conn.close()
  print(crayons.yellow('all done\n'))
