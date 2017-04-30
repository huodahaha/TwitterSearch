#encoding=utf-8

"""
analyzer.data_crawler
This module provide a wrapper of tweepy, containing text processing
data persistencce, multithread crawling
"""

import tweepy
from tweepy.error import *
import re, json, time, Queue, threading, pdb
from datetime import timedelta as duration
from datetime import datetime as date
from threading import Lock
from sets import Set
from math import log

from TwitterSearch.stopword import stopwords
from TwitterSearch.utils import logger

from TwitterSearch.conf import *
from exceptions import *
from hbase_connection import *

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

def user_exist(user_name):
    ret = True
    try:
        api.get_user(user_name)
    except TweepError, e:
        ret = False
    return ret

def text_process(text):
    """
    process tweet text, filter out all the illegal text
    """
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
    processed_text = re.sub(" +", " " , text.strip())
    # filter out stop words
    word_bag = Set(processed_text.split(" "))
    word_bag = list(word_bag - stopwords)

    return processed_text, word_bag


def tweet_process(tweet):
    """
    process tweet, extract all the infomation we need
    """
    if tweet.lang != "en":
        return None

    ts = int(time.mktime(tweet.created_at.timetuple()))
    tweet_id = tweet.id
    user_name = tweet.user.screen_name
    text = tweet.text
    processed_text, word_bag = text_process(text)
    impact_score = log(10+tweet.favorite_count + tweet.retweet_count)
    # print ts, user_id, text, word_bag
    return {"ts": ts,\
            "id":tweet_id,\
            "user_name": user_name,\
            "text": processed_text,\
            "raw_text": text,\
            "impact_score": impact_score,\
            "word_bag": word_bag}


def extract_mention(tweet):
    """
    extract mentioned users list within a tweet
    """
    ret = []
    for mention in tweet.entities['user_mentions']:
        ret.append(mention['screen_name'])
    return ret


class Crawler:
    """ 
    a tweepy wrapper
    """
    def __init__(self, auth):
        self.auth = auth
        self.api = tweepy.API(auth)
        pass

    # get all tweets raw data for a given duration
    def get_all_tweets(self, screen_name, delta = duration(days = DEFAULT_TIME_DURATION)):
        all_tweets = []
        new_tweets = []

        # ret
        processed_results = []

        latest_id = 0
        end_time = date.now() - delta
        is_over = False

        while not is_over:
            if latest_id is 0:
                new_tweets = self.api.user_timeline(screen_name = screen_name,count=200)
            else:
                new_tweets = self.api.user_timeline(screen_name = screen_name,count=200, max_id = latest_id)

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

        return all_tweets

    def map_tweets(self, screen_name, proc_fun, store_func = None):
        """
        map tweet with a given process function
        proc_fun should be type of <tweet object => processed object>
        store func should be type of <processed object => None>
        """
        # 1. get raw data from API
        try:
            all_tweets = self.get_all_tweets(screen_name)
        except TweepError, e:
            print e
            error_code = e[0][0]['code']
            error_message = e[0][0]['message']
            if error_code == 135:
                logger.error("Twitter API error, local timestamp out of date")
                raise TimeStampOutofDate 
            elif error_code == 34:
                logger.error("Twitter API error, User <%s> do not exist"%screen_name)
                raise NoneUserException
            elif error_code == 88:
                logger.error("Twitter API error, reach rate limit")
                raise RateLimitException
            else:
                logger.error("undefined error, message:%s"%error_message)
                raise UnDefinedException

        # 2. process all data
        processed_results = map((lambda t:[proc_fun(t)]), all_tweets)
        if len(processed_results):
            processed_results = reduce((lambda a,b:a+b), processed_results)

        # 3. save to database or return
        if not store_func:
            return processed_results    
        else:
            store_func(processed_results)

    def flatmap_tweets(self, screen_name, fun):
        """
        flatmap tweet with a given process function
        fun should be type fun => list 
        """
        all_tweets = self.get_all_tweets(screen_name)
        processed_results = map(fun, all_tweets)
        if len(processed_results):
            processed_results = reduce((lambda a,b:a+b), processed_results)
        return processed_results


class Tweet_Supervisor(threading.Thread):
    """
    thread to add screen names to the queue shared by workers
    """
    def __init__(self, q, name_list):
        threading.Thread.__init__(self)
        self.q = q
        self.name_list = name_list
        self.thread_cnt = THREAD_CNT

    def run(self):
        # fill the queues 
        for screen_name in self.name_list:
            self.q.put(screen_name)

        # terminate all consumers
        for i in range(self.thread_cnt):
            self.q.put(None)


class Crawl_Worker_Thread(threading.Thread, Crawler):
    """
    twitter crawler thread
    """
    def __init__(self, q, update):
        threading.Thread.__init__(self)
        Crawler.__init__(self, auth)
        self.q = q
        self.update = update

    def run(self):
        while True:
            user = self.q.get()

            if not user:
                # tasks over
                break

            if not self.update and is_user_data_exist(user):
                continue

            try:
                self.map_tweets(user, tweet_process, put_raw_data)
            except RateLimitException:
                return
           
class Tweet_Crawler:
    """
    Tweet crawler would crawl tweet data and store into HBase database
    """
    def __init__(self):
        self.crawler = Crawler(auth)
        self.api = tweepy.API(auth)
    
    def crawler_user(self, user, update = False):
        """
        crawler data single-threadly 
        if update is set to be True, crawler will ignore the data in database
        """
        # get processed result
        if not update and is_user_data_exist(user):
            return
        self.crawler.map_tweets(user, tweet_process, put_raw_data)

    def get_related(self, user_name):
        """
        crawl all the related users(users who have been @) of a given user
        """
        return self.crawler.flatmap_tweets(user_name, extract_mention)

    def crawler_users(self, users, update = False):
        """
        crawler data multi-threadly
        users should be a list
        """
        workQueue = Queue.Queue(20)
        threads = []

        producer = Tweet_Supervisor(workQueue, users)
        producer.start()
        threads.append(producer)

        # start thread 
        for worker_ID in range(THREAD_CNT):
            thread = Crawl_Worker_Thread(workQueue, update)
            thread.start()
            threads.append(thread)

        for t in threads:
            t.join()
