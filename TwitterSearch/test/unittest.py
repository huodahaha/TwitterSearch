#encoding=utf-8

"""
test.unittest
This module contains the set of test functions.
"""

from datetime import datetime as dt

from TwitterSearch.conf import RAW_DATA_TABLE
from TwitterSearch.analyzer.hbase_connection import *
from TwitterSearch.analyzer.data_crawler import *
from TwitterSearch.analyzer.exceptions import * 
from TwitterSearch.analyzer.analyzer import * 
from TwitterSearch.utils.util import date2ts

import pdb

from nose.tools import (
    assert_dict_equal,
    assert_equal,
    assert_false,
    assert_in,
    assert_is_instance,
    assert_is_not_none,
    assert_list_equal,
    assert_not_in,
    assert_raises,
    assert_true,
)

def unit_test_deco(foo):
    def deco_foo():
        print "%s begin"%foo.__name__
        start_time = dt.now()
        foo()
        end_time = dt.now()
        print "%s done"%foo.__name__
        print "%s execute time: %s\n\n\n"%(foo.__name__, str(end_time - start_time))
    return deco_foo

@unit_test_deco
def test_hbase_connection():
    # test put
    tweet_list = []
    tweet_list.append({"ts":1000, "id":2000, "user_name":"111", "text":"text", "word_bag":["word", "bag"]})
    tweet_list.append({"ts":1001, "id":2000, "user_name":"111", "text":"text", "word_bag":["word", "bag"]})
    tweet_list.append({"ts":1002, "id":2000, "user_name":"111", "text":"text", "word_bag":["word", "bag"]})
    put_raw_data(tweet_list)

    # test get
    result = get_raw_data(["111"], 1000, 1003)
    print result

    # 
    assert_equal(is_user_data_exist("000"), False)
    assert_equal(is_user_data_exist("111"), True)

@unit_test_deco
def test_crawler_single():
    delete_table(RAW_DATA_TABLE)
    test_name = 'NYUStern'
    c = Tweet_Crawler()
    c.crawler_user(test_name)
    result = get_raw_data([test_name])
    assert_true(len(result) > 0)
    assert_equal(result[0]["user_name"], test_name)
    assert_equal(is_user_data_exist(test_name), True)

@unit_test_deco
def test_user_not_exist():
    test_name = "sdfasdfaseqwkjhv"
    c = Tweet_Crawler()
    try:
        c.crawler_user(test_name)
    except Exception, e:
        # pdb.set_trace()
        assert_true(isinstance(e, NoneUserException))

@unit_test_deco
def test_related_user():
    test_name = "realDonaldTrump"
    c = Tweet_Crawler()
    ret = c.get_related(test_name)
    print "total mention users: %d"%len(ret)
    print "mentions %s..."%(str(ret[0:3]))

@unit_test_deco
def test_crawler_users():
    test_name = 'Refinery29'
    c = Tweet_Crawler()
    c.crawler_users([test_name], True)
    result = get_raw_data([test_name])
    assert_true(len(result) > 0)
    assert_equal(result[0]["user_name"], test_name)
    assert_equal(is_user_data_exist(test_name), True)

def test_generator():
    test_name = 'NYUStern'
    c = Tweet_Crawler()
    c.crawler_user(test_name, True)
    gen = get_raw_data_generator(test_name)
    cnt = 0
    for tweet in gen:
        cnt += 1
        if cnt > 10:
            break
        print tweet

@unit_test_deco
def test_keywords():
    result, users = get_keywords('realDonaldTrump', related_cnt = 5)
    print result

@unit_test_deco
def test_search_text():
    # print "2017-1-1 -> 2017-5-1"
    # start_ts = date2ts(2017,1,1)
    # end_ts = date2ts(2017,5,1)
    # result = search_text('realDonaldTrump', 'china trade', start_ts, end_ts, related_cnt = 10)

    # top_n = min(100, len(result))
    # print "Top %d"%top_n
    # for i in range(top_n):
        # print result[i]

    print "2016-6-1 -> 2017-1-1"
    start_ts = date2ts(2016,6,1)
    end_ts = date2ts(2017,1,1)
    result, users = search_text('realDonaldTrump', 'china japan', start_ts, end_ts)
    print result
 
    # top_n = min(100, len(result))
    # print "Top %d"%top_n
    # for i in range(top_n):
        # print result[i]

@unit_test_deco
def test_get_twitter_by_tid():
    test_name = 'NYUStern'
    c = Tweet_Crawler()
    c.crawler_user(test_name, True)
    result = get_raw_data([test_name])
    id = result[0]["id"]
    print get_twitter_by_id(id)

def test_non_users():
    start_ts = date2ts(2016,6,1)
    end_ts = date2ts(2017,1,1)
    result = get_keyword('1048b9dkwej', start_ts, end_ts) 
