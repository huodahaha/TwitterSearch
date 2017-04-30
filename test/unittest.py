#encoding=utf-8

"""
test.unittest
This module contains the set of test functions.
"""

from datetime import datetime

from TwitterSearch.conf import RAW_DATA_TABLE
from TwitterSearch.analyzer.hbase_connection import *
from TwitterSearch.analyzer.data_crawler import *
from TwitterSearch.analyzer.exceptions import * 
from TwitterSearch.analyzer.analyzer import * 

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
        start_time = datetime.now()
        foo()
        end_time = datetime.now()
        print "%s done"%foo.__name__
        print "%s execute time: %s\n\n\n"%(foo.__name__, str(end_time - start_time))
    return deco_foo

@unit_test_deco
def test_hbase_connection():
    # reset table data
    delete_table(RAW_DATA_TABLE)

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
    test_name = "NYUStern"
    c = Tweet_Crawler()
    ret = c.get_related(test_name)
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
    get_keyword(['NYUStern'])
