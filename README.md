# TwitterSearch
TwitterSearch is a search engine for Tweets. 

__TwitterSearch DOESN'T USE ANY EXTERNAL INFORMATION RETRIVAL LIBARARY like Lucene.__

## Feature: Twitter Search
Using TwitterSearch, you can search tweets from a given twitter user's timeline. 
Also, the search time range could be set to a specific time spec. The result ranking algorithm combine a tf-idf algorithm
and tweets' impact score (calulating with each tweet's retweet count and favorite count)

## Feature: Keyword Retrieval
Using the tf-idf algorithm and tweet impact score, TwitterSearch can give analysis about a certain users
tweet keyword during a certain time spec.

## Feature: Related Users
TwitterSearch can analyze a certain twitter user's timeline to give a related users list. We can use this users list to search for
twitter or make a keyword retrieval on a more wide document(tweets) range. However, it may lead to API prohibition since the data would be large.

## Notice:
1. I use Twitter API to crawl data with my personal twitter API key, so pls keep the API key in TwitterSearch/conf/setting.py
secret. 
2. Frequent using Twitter API would lead to a temporary prohibition according to Twitter Corp. 

## Install and Use
Hbase require a Java version over 1.8, and __YOU SHOULD SET $JAVAHOME correctly__
```
# using install.sh to install the requirments
./install.sh 
# using start_hbase.sh to start hbase database
./start_hbase.sh.
# reset databases (need to reset when you first use)
python reset_database.py
# using stop_hbase.sh to shutdown hbase database
./stop_hbase.sh 
```

## Trouble Shooting
When runing into “Resource u'corpora/wordnet' not found.  Please use the NLTK” problem
You may need to download wordnet corpus manualy
```
python -m nltk.downloader wordnet
```


## Library dependencies
nltk 
tweepy (twitter API library for python)
happybase (for hbase connection)
flask (web end)
