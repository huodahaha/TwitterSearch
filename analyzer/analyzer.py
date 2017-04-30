#encoding=utf-8

"""
analyzer.analyzer
This module contains analyzer of processed tweet data.
"""

from math import log
from nltk.corpus import wordnet as wn

from TwitterSearch.analyzer.data_crawler import *
from TwitterSearch.analyzer.hbase_connection import *

import pdb

class Keyword_Analyzer:
    def __init__(self, users, start_ts = 0, end_ts = 0):
        self.gen = get_raw_data_generator(users, start_ts, end_ts)
        self.reverted_idx = {}
        self.total_tweets_cnt = 0

        # should use database here
        self.tweets_list = {}

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
            self.tweets_list[tweet_id] = tweet["text"]
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

            idf = log(self.total_tweets_cnt/len(document_list))
            word_score = 0
            for document_id in document_list:
                text = self.tweets_list[document_id].split()
                cnt = 0
                for w in text:
                    if w == word:
                        cnt += +1
                tf = (1.0*cnt)/len(text)
                impact_score = log(len(text))
                word_score += tf*idf*impact_score
            word_scores[word] = word_score

        print "analyzing success"
        sorted_keywords = sorted(word_scores.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
        return sorted_keywords
        
def get_keyword(users, start_ts = 0, end_ts = 0):
    # 1. crawl data
    c = Tweet_Crawler()
    c.crawler_users(users, True)

    # 2. build reverted list
    analyzer = Keyword_Analyzer(users, start_ts, end_ts)
    analyzer.build_reverted_lists()

    # 3. calculate keywords
    keywords = analyzer.calculate_keywords()

    # 4. show keywords
    print "Top 100"
    top_n = min(100, len(keywords))
    for i in range(top_n):
        print keywords[i]

def get_related_keywords(user, start_ts, end_ts):

