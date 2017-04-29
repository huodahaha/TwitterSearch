import cPickle as pickle
from math import log
from nltk.corpus import wordnet as wn

import pdb

if __name__ == "__main__":

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
