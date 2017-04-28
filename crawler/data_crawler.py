import tweepy, re, json, time, Queue, threading
from datetime import timedelta as duration
from datetime import datetime as date
from threading import Lock
from math import log
from sets import Set
from nltk.corpus import wordnet as wn

from stopword import stopwords

import pdb

# auth infomation
from key import *

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

JOB_CNT = 100
QUEUE_LEN = 20
CONSUMNER_CNT = 20

crawling_results = []
results_lock = Lock()

# single tweet crawler supervisor thread
class Tweet_Supervisor(threading.Thread):
    def __init__(self, q, name_list):
        threading.Thread.__init__(self)
        self.q = q
        self.name_list = name_list

    def run(self):
        # fill the queues 
        for screen_name in self.name_list:
            self.q.put(screen_name)

        # terminate all consumers
        for i in range(CONSUMNER_CNT):
            self.q.put(None)

# single tweet cralwer thread
class Tweet_Worker(threading.Thread):
    def __init__(self, auth, q):
        threading.Thread.__init__(self)
        self.q = q
        api = tweepy.API(auth)

    def run(self):
        while True:
            if not self.q.empty():
                screen_name = self.q.get()
                if screen_name != None:
                    processing_result = self.get_all_tweets(screen_name)

                    # save to databases
                    results_lock.acquire()
                    crawling_results.extend(processing_result)
                    results_lock.release()
                else:
                    break
            else:
                time.sleep(1)

    @staticmethod
    def text_process(text):
        # https:// pattern
        text = re.sub("(https?|ftp|file)://[-a-zA-Z0-9+&@#/%?=~_|!:,.;]*[-a-zA-Z0-9+&@#/%=~_|]", "", text)

        # RT @xxxx: pattern
        text = re.sub("RT @[^:]+:","", text)

        # @xxx pattern
        text = re.sub("@[^ ]+ ","", text)

        # illegal characters
        text = re.sub("[^A-Za-z0-9 ']","",text)

        # lower case
        text = text.lower()

        # filter out consecutive spaces
        processed_text = re.sub(" +", " " , text.strip()).split(" ")

        # filter out stop words
        word_bag = Set(processed_text)
        word_bag = list(word_bag - stopwords)

        return processed_text, word_bag

    # return tweets cnt that have been crawled
    def get_all_tweets(self, screen_name, delta = duration(days = 365)):
        all_tweets = []    
        new_tweets = []

        # ret
        processed_results = []

        latest_id = 0
        end_time = date.now() - delta
        is_over = False
       
        while not is_over:
            if latest_id is 0:
                new_tweets = api.user_timeline(screen_name = screen_name,count=200)
            else:
                new_tweets = api.user_timeline(screen_name = screen_name,count=200, max_id = latest_id)

            if len(new_tweets) == 0:
                break

            last_tweet = new_tweets[-1]
            if last_tweet.created_at < end_time:
                # filter out all the tweets that has been passed over a year
                new_tweets = [t for t in new_tweets if t.created_at >= end_time]
                is_over = True

            all_tweets.extend(new_tweets)
            if len(all_tweets) == 0:
                latest_id = 0
            else:
                latest_id = all_tweets[-1].id - 1

        for tweet in all_tweets:
            if tweet.lang != "en":
                continue
            ts = int(time.mktime(tweet.created_at.timetuple()))
            tweet_id = tweet.id
            user_id = tweet.user.id
            text = tweet.text
            processed_text, word_bag = self.text_process(text)
            # print ts, user_id, text, word_bag
            processed_results.append({"ts": ts,\
                               "id":tweet_id,\
                               "user_id": user_id,\
                               "text": processed_text,\
                               "word_bag": word_bag})

        return processed_results

# Tweet crawler would crawl tweet data and store into HBase database
class Tweet_Crawler:
    def __init__(self, auth):
        self.auth = auth

    def crawler_follower():
        



