import tweepy
from tweepy.error import *
import re, json, time, Queue, threading
from datetime import timedelta as duration
from datetime import datetime as date
from threading import Lock
from sets import Set

from TwitterSearch.stopword import stopwords
from TwitterSearch.utils import logger

from TwitterSearch.conf import \
        CONSUMER_KEY,\
        CONSUMER_SECRET,\
        ACCESS_TOKEN,\
        ACCESS_TOKEN_SECRET,\
        THREAD_CNT,\
        JOB_QUEUE_LEN,\
        RAW_DATA_TABLE

from exceptions import *
from hbase_connection import *

# process tweet text, filter out all the illegal text
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


# process tweet, extract all the infomation we need
def tweet_process(tweet):
    if tweet.lang != "en":
        return None

    ts = int(time.mktime(tweet.created_at.timetuple()))
    tweet_id = tweet.id
    user_name = tweet.user.screen_name
    text = tweet.text
    processed_text, word_bag = text_process(text)
    # print ts, user_id, text, word_bag
    return {"ts": ts,\
            "id":tweet_id,\
            "user_name": user_name,\
            "text": processed_text,\
            "word_bag": word_bag}


# extract mentioned users list within a tweet
def extract_mention(tweet):
    ret = []
    for mention in tweet.entities['user_mentions']:
        ret.append(mention['screen_name'])
    return ret


class Crawler:
    def __init__(self, auth):
        self.api = tweepy.API(auth)

    # get all tweets raw data for a given duration
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

    # fun should be type fun => single object
    def map_tweets(self, screen_name, fun):
        all_tweets = self.get_all_tweets(screen_name)
        processed_results = map((lambda t:[fun(t)]), all_tweets)
        if len(processed_results):
            processed_results = reduce((lambda a,b:a+b), processed_results)
        return processed_results


    # fun should be type fun => list 
    def flatmap_tweets(self, screen_name, fun):
        all_tweets = self.get_all_tweets(screen_name)
        processed_results = map(fun, all_tweets)
        if len(processed_results):
            processed_results = reduce((lambda a,b:a+b), processed_results)
        return processed_results


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
class Crawler_Thread(threading.Thread):
    def __init__(self, auth, q):
        threading.Thread.__init__(self)
        self.q = q
        self.crawler = Crawler(auth)

    def run(self):
        while True:
            screen_name = self.q.get()
            if not screen_name:
                # tasks over
                break

            # get processed result
            processed_tweets = self.crawler.map_tweets(screen_name, tweet_process)

            # save to database
            put_raw_data(processed_tweets)
            
            
"""
Tweet crawler would crawl tweet data and store into HBase database
"""
class Tweet_Crawler:
    def __init__(self):
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

        self.crawler = Crawler(auth)
        self.api = tweepy.API(auth)
        self.auth = auth
    
    """
    crawler data single-threadly 
    if update is set to be True, crawler will ignore the data in database
    """
    def crawler_user(self, user, update = False):
        # get processed result
        if not update:
            if is_user_data_exist(user):
                return

        try:
            processed_tweets = self.crawler.map_tweets(user, tweet_process)
        # save to database
        except TweepError, e:
            if e[0][0]['code'] == 135:
                raise TimeStampOutofDate 

        put_raw_data(processed_tweets)

    # crawler data multi-threadly
    # users should be a list
    def crawler_users(self, users, update = False):
        workQueue = Queue.Queue(JOB_QUEUE_LEN)
        threads = []

        producer = Producer(workQueue, users)
        producer.start()
        threads.append(producer)

        # start threads 
        print "starting crawling data"
        for worker_ID in range(CONSUMNER_CNT):
            thread = Tweet_Crawler(auth, workQueue)
            thread.start()
            threads.append(thread)

        for t in threads:
            t.join()

    def user_exist(self, user_name):
        try:
            user = self.api.get_user(user_name)
        except TweepError, e:
            
            logger.error("user_name <%s> not found"%user_name)
            return False
        return True

    # crawl all the related users(users who have been @) of a given user
    def get_related(self, user_name):
        return self.crawler.flatmap_tweets(user_name, extract_mention)
