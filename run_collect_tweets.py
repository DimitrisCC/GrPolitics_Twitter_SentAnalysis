import sched
import time
import tweepy

import preprocessing
import processing
import db

consumer_key = 'YRnp0q7lSJLRU1KFzXzfQpgBj'
consumer_secret = '1GrTLHR67JMjqh1jzeHzfZEwesEGTI8WMkH5IlrvEKzw5VKXWl'
access_token = '157119280-8DPkm3KENaA7rrBbhk52PizQL8gKIGnS4q1crk5o'
access_token_secret = 'v6XmeY9PwfyIBf85dvud31e3GfJCM5VaaqnmTL7nhhONx'

oauth = tweepy.OAuthHandler(consumer_key, consumer_secret)
oauth.set_access_token(access_token, access_token_secret)

api = tweepy.API(oauth)

db.connect()
db.create()

last_id = {'#syriza': 0, '#neadimokratia': 0, '@tsipras': 0, '@mitsotakis': 0}
loops = 0

schedule = sched.scheduler(time.time, time.sleep)


def get_tweets():
    global last_id, loops
    print("Let's collect some tweets!")
    tweets = {'id': [], 'text': [], 'clean_text': [], 'category': [], 'date': []}

    while True:
        try:
            new_tweets = []
            cur = None

            search_res = api.search(q='#syriza -rt',  max_id=str(last_id['#syriza'] - 1), count=100)
            for t in search_res:
                new_tweets.append((t, '#syriza'))
                cur = t
            last_id_syriza = 0 if cur is None else cur.id

            search_res = api.search(q='#neadimokratia -rt', max_id=str(last_id['#neadimokratia'] - 1), count=100)
            for t in search_res:
                new_tweets.append((t, '#neadimokratia'))
                cur = t
            last_id_nd = 0 if cur is None else cur.id

            search_res = api.search(q='@tsipras -rt', max_id=str(last_id['@tsipras'] - 1), count=100)
            for t in search_res:
                new_tweets.append((t, '@tsipras'))
                cur = t
            last_id_tsipras = 0 if cur is None else cur.id

            search_res = api.search(q='@mitsotakis -rt', max_id=str(last_id['@mitsotakis'] - 1), count=100)
            for t in search_res:
                new_tweets.append((t, '@mitsotakis'))
                cur = t
            last_id_mitsotakis = 0 if cur is None else cur.id

            loops += 1
            print(len(new_tweets), "new tweets")
            if not new_tweets:
                print("No new tweets")
                if loops > 15:
                    last_id['#syriza'] = 0
                    last_id['#neadimokratia'] = 0
                    last_id['@tsipras'] = 0
                    last_id['@mitsotakis'] = 0
                    loops = 0
                schedule.enter(60, 1, get_tweets, ())
                # a minute delay so it won't abuse the limit if not new tweets are there
                break
            else:
                for t in new_tweets:
                    if t[0].id not in tweets['id']:
                        # checking for duplicates here load-balances the overhead
                        tweets['id'].append(t[0].id)
                        tweets['text'].append(t[0].text)
                        tweets['category'].append(t[1])
                        ttime = t[0].created_at
                        tweets['date'].append('%s-%s-%s' % (str(ttime.year),
                                                            preprocessing.format_time(ttime.month),
                                                            preprocessing.format_time(ttime.day)))
                last_id['#syriza'] = last_id_syriza
                last_id['#neadimokratia'] = last_id_nd
                last_id['@tsipras'] = last_id_tsipras
                last_id['@mitsotakis'] = last_id_mitsotakis
        except tweepy.TweepError as e:
            print("Error: ", str(e))
            if 'Rate limit exceeded' in str(e):
                last_id['#syriza'] = 0
                last_id['#neadimokratia'] = 0
                last_id['@tsipras'] = 0
                last_id['@mitsotakis'] = 0
                schedule.enter(60*15+1, 1, get_tweets, ())
                loops = 0
            else:
                schedule.enter(1, 1, get_tweets, ())
            break

    if tweets:
        tweets = preprocessing.clean_tweets(tweets)
        tweets = processing.classify(tweets, ('#syriza', '#neadimokratia', '@tsipras', '@mitsotakis'))
        db.insert(tweets)
        tweets.clear()


schedule.enter(0, 1, get_tweets, ())
schedule.run()
