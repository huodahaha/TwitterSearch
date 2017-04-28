import tweepy, re, json, time, Queue, threading
import cPickle as pickle
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

class Producer(threading.Thread):
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

class Tweet_Crawler(threading.Thread):
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

if __name__ == "__main__":

    workQueue = Queue.Queue(QUEUE_LEN)
    threads = []

    # follower
    user = api.get_user("KingJames")
    # friends means following 
    friends_list = []
    for friend in user.friends():
        friends_list.append(friend.screen_name)

    producer = Producer(workQueue, friends_list)
    producer.start()
    threads.append(producer)

    # start thread 
    print "starting crawling data"
    for worker_ID in range(CONSUMNER_CNT):
        thread = Tweet_Crawler(auth, workQueue)
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()

    # data analyzing
    print "start build reverted index...." 
    total_tweets_cnt = len(crawling_results)
    print "total tweets: %d"%total_tweets_cnt

    # count all word
    reverted_idx = {}
    tweets_list = {}
    for result in crawling_results:
        tweet_id = result["id"]
        tweets_list[tweet_id] = result["text"]
        for word in result["word_bag"]:
            if word in reverted_idx:
                reverted_idx[word].append(tweet_id)
            else:
                reverted_idx[word] = [tweet_id]
    
    print "total effective word count is %d"%len(reverted_idx)

    print "start analyzing"
    word_scores = {}
    for (word,document_list) in reverted_idx.items():

        # filter out adjective
        if len(wn.synsets(word, wn.ADJ)) > 0:
            continue

        # filter out signle character
        if len(word) == 1:
            continue

        idf = log(total_tweets_cnt/len(document_list))
        word_score = 0
        for document_id in document_list:
            text = tweets_list[document_id]
            cnt = 0
            for w in text:
                if w == word:
                    cnt += +1
            tf = (1.0*cnt)/len(text)
            impact_score = log(len(text))
            word_score += tf*idf*impact_score
        word_scores[word] = word_score

    print "analyzing success"
    sorted_scores = sorted(word_scores.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
    
    print "Top 100"
    top_n = min(100, len(sorted_scores))
    for i in range(top_n):
        print sorted_scores[i]
