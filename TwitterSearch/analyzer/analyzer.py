#encoding=utf-8

"""
analyzer.analyzer
This module contains analyzer of processed tweet data.
"""

from math import log
from nltk.corpus import wordnet as wn

from TwitterSearch.analyzer.data_crawler import *
from TwitterSearch.analyzer.hbase_connection import *
import datetime

import pdb

class Keyword_Analyzer:
    def __init__(self, users, start_ts = 0, end_ts = 0):
        if not isinstance(users, list):
            users = [users]
        self.gen = get_raw_data_generator(users, start_ts, end_ts)
        self.reverted_idx = {}
        self.total_tweets_cnt = 0

    def build_reverted_lists(self):
        """
        build reverted list:
        word_1 -> [document_id_x, document_id_y]
        word_2 -> [document_id_z, document_id_y]
        """
        print "start build reverted index...." 
        self.reverted_idx = {}
        self.total_tweets_cnt = 0
        for tweet in self.gen:
            self.total_tweets_cnt += 1

            tweet_id = tweet["id"]
            for word in tweet["word_bag"]:
                if word in self.reverted_idx:
                    self.reverted_idx[word].append(tweet_id)
                else:
                    self.reverted_idx[word] = [tweet_id]
     
        print "total effective word count is %d"%len(self.reverted_idx)
        print "total tweet count is %d"%self.total_tweets_cnt
        return 

    def calculate_keywords(self):
        """
        use tf-idf algorithm to calculate keyword lists
        """
        word_scores = {}
        for (word, document_list) in self.reverted_idx.items():

            # filter out adjective
            if len(wn.synsets(word, wn.ADJ)) > 0:
                continue

            # filter out signle character
            if len(word) == 1:
                continue

            # idf is term frequency in all document
            idf = log(self.total_tweets_cnt/len(document_list))
            word_score = 0
            tweets_list = get_twitter_by_id_list(document_list)

            for document_id in document_list:
                text = tweets_list[document_id]["text"].split()
                if not len(text):
                    continue

                # count term frequency in a single document
                cnt = 0
                for w in text:
                    if w == word:
                        cnt += 1

                # calculate word score
                tf = (1.0*cnt)/len(text)
                impact_score = log(len(text))
                word_score += tf*idf*impact_score

            word_scores[word] = round(word_score,2)

        print "analyzing success"
        sorted_keywords = sorted(word_scores.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
        return sorted_keywords

    def search_word(self, text):
        """
        boolean retrival
        """
        processed_text, keywords = text_process(text)
        documents_score = {}

        for keyword in keywords:
            if not keyword in self.reverted_idx:
                continue
            documents_list = self.reverted_idx[keyword]
            idf = log(self.total_tweets_cnt/len(documents_list))            

            tweets_list = get_twitter_by_id_list(documents_list)
            for document_id in documents_list:
                processed_tweet = tweets_list[document_id]
                if not document_id in documents_score:
                    ts_string = datetime.datetime.fromtimestamp(processed_tweet["ts"]).\
                            strftime('%Y-%m-%d %H:%M:%S')

                    documents_score[document_id] = {\
                            "raw_test":processed_tweet["raw_text"],\
                            "user_name":processed_tweet["user_name"],\
                            "ts":ts_string,\
                            "score": 0}
                
                text = processed_tweet["text"].split()
                cnt = 0
                for w in text:
                    if w == keyword:
                        cnt += 1
                tf = (1.0*cnt)/len(text)
                word_score = tf*idf*processed_tweet["impact_score"]
                documents_score[document_id]["score"] += word_score

        sorted_documents = sorted(documents_score.values(), \
                lambda x, y: cmp(x["score"], y["score"]), reverse=True)

        return sorted_documents
        
def get_keywords(user, start_ts = 0, end_ts = 0, related_cnt = 0):
    """
    search a user and his related users keyword
    use tf-idf and tweet impact score to calculate every word's score.
    """
    c = Tweet_Crawler()
    users = [user]
    if related_cnt != 0:
        related_users = c.get_related(user)

        # since twitter API has rate limit, default related users is 10
        users = related_users[0:related_cnt]

    # 1. crawl data
    c.crawler_users(users)

    # 2. build reverted list
    analyzer = Keyword_Analyzer(users, start_ts, end_ts)
    analyzer.build_reverted_lists()

    # 3. calculate keywords
    keywords = analyzer.calculate_keywords()
    result = keywords[0:50]
    if related_cnt == 0:
        return result, []
    else:
        return result, users

def search_text(user, text, start_ts = 0, end_ts = 0, related_cnt = 0):
    """
    search text from a user's timeline
    note that, if related_cnt > 0, we will seaerch from a even wide range, including 
    twitter uses who have been mentioned recently by the given user
    """
    c = Tweet_Crawler()
    # 0. extend user range
    users = [user]
    if related_cnt != 0:
        related_users = c.get_related(user)

        # since twitter API has rate limit, default related users is 10
        users.extend(related_users[0:related_cnt])

    # 1. crawl data
    c.crawler_users(users)

    # 2. build reverted list
    analyzer = Keyword_Analyzer(users, start_ts, end_ts)
    analyzer.build_reverted_lists()

    # 3. calculate keywords
    result = analyzer.search_word(text)
    if related_cnt == 0:
        return result, []
    else:
        return result, users
