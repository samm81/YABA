import sqlite3

con = sqlite3.connect('prices.db')
cur = con.cursor()
cur.execute('select * from gemini order by datetime(timestamp) DESC')
print(len(cur.fetchall()))
