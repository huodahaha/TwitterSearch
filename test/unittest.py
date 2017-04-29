#encoding=utf-8
from datetime import datetime

from TwitterSearch.conf import RAW_DATA_TABLE
from TwitterSearch.analyzer.hbase_connection import *
from TwitterSearch.analyzer.data_crawler import Tweet_Crawler

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
    test_name = "NYUStern"
    c = Tweet_Crawler()
    c.crawler_user(test_name)
    result = get_raw_data([test_name])
    assert_true(len(result) > 0)
    assert_equal(result[0]["user_name"], test_name)

@unit_test_deco
def test_crawler_single():
    test_name = "NYUStern"
    c = Tweet_Crawler()
    c.crawler_user(test_name)
    result = get_raw_data([test_name])
    assert_true(len(result) > 0)
    assert_equal(result[0]["user_name"], test_name)
