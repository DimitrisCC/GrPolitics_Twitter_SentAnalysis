import db
from processing import TermClassifier

neighbors = [1, 2, 4, 5, 10]
rank = 300

db.connect()
tweets = db.select("SELECT clean_text FROM Tweets WHERE date BETWEEN '2016-12-18' AND '2017-01-07'")
tweets_ = []

for t in tweets:
    tweets_.append(t[0])

tc = TermClassifier(tweets_, rank)

for n in neighbors:
    print('\n\nNeighbors: ', n)
    print('Waiting... :/ Be patient ;)')
    tc.classify_terms(n)
