from sklearn.preprocessing import LabelEncoder

import db
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")
matplotlib.style.use('ggplot')

db.connect()
stats = db.select('SELECT date, category, positive, negative FROM Stats ORDER BY date')

last_day = stats[-1][0]

days = 0
week_num = 1
prev_date = stats[0][0]
weeks = []
istats = []

for row in stats:
    if row is stats[-1]:
        days = 6
    if days == 7:
        days = 0
        week_num += 1
    istats.append([row[0], row[1], int(row[2]), int(row[3])])
    if row[0] > prev_date:  # new day
        days += 1
    prev_date = row[0]
    weeks.append(week_num)

df = pd.DataFrame(istats)
df.columns = ['Date', 'Category', 'Positive', 'Negative']
df['Week'] = weeks
grouped = df[['Week', 'Category', 'Positive', 'Negative']].groupby(['Week', 'Category'])
wstats_toshow = grouped.agg([np.sum, np.average, np.std])
wstats = grouped.agg([np.sum, np.average, np.std]).reset_index()

print(wstats_toshow)

print(df.groupby(['Week', 'Category']).describe())  # more stats

# plot please
for w in range(np.max(df['Week']), 0, -1):
    dfp = df.query('Week == %d' % w)[['Date', 'Category', 'Positive', 'Negative']]
    legend = []
    le = LabelEncoder()
    fig, ax = plt.subplots(1, 1)
    for sent in [('Positive', 1), ('Negative', -1)]:
        for cat in [('#syriza', 'r'), ('#neadimokratia', 'b'), ('@tsipras', 'k'), ('@mitsotakis', 'c')]:
            dfcat = dfp[dfp.Category == cat[0]]
            le.fit(dfcat['Date'])
            plt.xticks(le.transform(dfcat['Date']), dfcat['Date'])
            dfcat['Date'] = le.transform(dfcat['Date'])
            lstyle = cat[1] + '-' if sent[1] == 1 else '--'
            plt.plot(dfcat['Date'], sent[1]*dfcat[sent[0]], lstyle, linewidth=4)
            plt.title("Week %d summary" % w)
            legend.append(sent[0] + " " + cat[0])
    plt.legend(legend, prop={'size': 9}, loc=4)
    fig_man = plt.get_current_fig_manager()
    fig_man.window.showMaximized()
plt.show()
