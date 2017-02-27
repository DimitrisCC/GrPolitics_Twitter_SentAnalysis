import sqlite3 as lite

con = None


def connect():
    global con
    con = lite.connect('pypolDB.db')


def create():
    global con
    with con:
        cur = con.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS Tweets(id INT, text TEXT, clean_text TEXT, category TEXT,"
            "date TEXT, class INT, PRIMARY KEY (id, category), UNIQUE(text) ON CONFLICT IGNORE)")
        cur.execute(
            "CREATE TABLE IF NOT EXISTS Stats(category TEXT, positive TEXT, negative TEXT, date TEXT,"
            "PRIMARY KEY(category, date) ON CONFLICT IGNORE)")


# tweets is a dict
def insert(tweets):
    global con
    with con:
        cur = con.cursor()
        tweets_arr = []
        for i in range(len(tweets['id'])):
            if tweets['clean_text'][i].strip() == "":
                continue  # no greek text -> throw away
            tweets_arr.append([tweets['id'][i], tweets['text'][i], tweets['clean_text'][i], tweets['category'][i],
                               tweets['date'][i], tweets['class'][i]])
        cur.executemany("INSERT OR IGNORE INTO Tweets VALUES(?, ?, ?, ?, ?, ?)", tweets_arr)


def insert_stats(stats):
    global con
    with con:
        cur = con.cursor()
        cur.executemany("INSERT OR IGNORE INTO Stats VALUES(?, ?, ?, ?)", stats)


def select(query):
    global con
    with con:
        cur = con.cursor()
        cur.execute(query)
        return cur.fetchall()
