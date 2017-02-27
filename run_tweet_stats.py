import copy
import db

db.connect()
data = db.select("SELECT date, category, class, count(*) FROM Tweets GROUP BY date, category, class")

datadict_template = {'#neadimokratia': {'Positive': 0, 'Negative': 0},
                     '#syriza': {'Positive': 0, 'Negative': 0},
                     '@tsipras': {'Positive': 0, 'Negative': 0},
                     '@mitsotakis': {'Positive': 0, 'Negative': 0}}
datadict = copy.deepcopy(datadict_template)
datedatadict = {}
prev_date = data[0][0]
for row in data:
    if row[0] != prev_date:
        datedatadict[prev_date] = datadict
        datadict = copy.deepcopy(datadict_template)
    datadict[row[1]][row[2]] = row[3]
    prev_date = row[0]

final_data = []
for date in datedatadict:
    for cat in datedatadict[date]:
        catdict = datedatadict[date][cat]
        final_data.append([cat, catdict['Positive'], catdict['Negative'], date])

db.insert_stats(final_data)
print('Done ;)')


