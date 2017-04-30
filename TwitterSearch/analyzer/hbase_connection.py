#encoding=utf-8

import happybase, time
import cPickle as pickle
from datetime import datetime as date

import pdb

from TwitterSearch.conf import \
        HBASE_DOMAIN, \
        RAW_DATA_TABLE, \
        ID_DATA_TABLE

def convert_ts(ts):
    return ("%012d"%(int(ts))).encode("ascii")

def convert_tid(id):
    return ("%020d"%(int(id))).encode("ascii")

def get_table(table_name):
    connection = happybase.Connection(HBASE_DOMAIN)
    table_lists = connection.tables()
    if not table_name in table_lists:
        cfs = {"cf":None}
        connection.create_table(table_name, families = cfs)

    # get table instance
    return connection.table(table_name)

def delete_table(table_name):
    connection = happybase.Connection(HBASE_DOMAIN)
    table_lists = connection.tables()
    if table_name in table_lists:
        connection.delete_table(table_name, disable=True)

def get_raw_table():
    return get_table(RAW_DATA_TABLE)

def get_tid_table():
    return get_table(ID_DATA_TABLE)

def put_raw_data(tweet_list):
    table = get_raw_table()
    # write into hbase
    with table.batch() as b:
        for tweet in tweet_list:
            if not tweet:
                continue
            ts = tweet["ts"]
            user_name = tweet["user_name"]
            row_key = convert_ts(ts)
            cloumn = ("cf:" + user_name).encode("ascii")
            value = pickle.dumps(tweet)
            b.put(row_key, {cloumn:value})

    table = get_tid_table()
    # write into hbase
    with table.batch() as b:
        for tweet in tweet_list:
            if not tweet:
                continue
            row_key = convert_tid(tweet["id"])
            cloumn = "cf:tweet".encode("ascii")
            value = pickle.dumps(tweet)
            b.put(row_key, {cloumn:value})


def get_raw_data(user_names, start_ts = 0, end_ts = 0):
    table = get_raw_table()
    ret = []
    cols = []

    if not end_ts:
        end_ts= int(time.mktime(date.now().timetuple()))

    if not isinstance(user_names, list):
        user_names = [user_names]

    for user_name in user_names:
        cols.append(("cf:" + user_name).encode("ascii"))
   

    scanner = table.scan(row_start= convert_ts(start_ts),
                         row_stop = convert_ts(end_ts),
                         columns = cols)

    for res in scanner:
        value = res[1].values()[0]
        ret.append(pickle.loads(value))
    return ret

def get_twitter_by_id(id):
    table = get_tid_table()
    res = table.row(convert_tid(id))
    if res == None:
        return res
    else:
        return pickle.loads(res["cf:tweet"])

def get_twitter_by_id_list(ids):
    table = get_tid_table()
    ret = {}
    for id in ids:
        res = table.row(convert_tid(id))
        if res == None:
            continue
        ret[id] = pickle.loads(res["cf:tweet"])
    return ret

def get_raw_data_generator(user_names, start_ts = 0, end_ts = 0):
    table = get_raw_table()
    cols = []

    if not end_ts:
        end_ts= int(time.mktime(date.now().timetuple()))

    if not isinstance(user_names, list):
        user_names = [user_names]

    for user_name in user_names:
        cols.append(("cf:" + user_name).encode("ascii"))
   

    scanner = table.scan(row_start= convert_ts(start_ts),
                         row_stop = convert_ts(end_ts),
                         columns = cols)

    for res in scanner:
        info = res[1]
        col = res[1].keys()[0]
        value = res[1].values()[0]
        yield pickle.loads(value)

def is_user_data_exist(user_name):
    table = get_raw_table()

    cols = [("cf:" + user_name).encode("ascii")]
    start_ts = 0
    end_ts= int(time.mktime(date.now().timetuple()))

    scanner = table.scan(row_start= convert_ts(start_ts),
                         row_stop = convert_ts(end_ts),
                         columns = cols)

    for res in scanner:
        return True
    return False
