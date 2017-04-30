#encoding=utf-8

import os, errno, datetime, time

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5 (except OSError, exc: for Python <2.5)
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def date2ts(_year, _month, _day):
    dt = datetime.datetime(year = _year, month = _month, day = _day)
    return int(time.mktime(dt.timetuple()))
