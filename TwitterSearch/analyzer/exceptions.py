#encoding=utf-8

"""
analyzer.exceptions
This module contains the set of exceptions of crawler and analyzer.
"""

class TwitterSearcherException(Exception):
    """ base exception of all """
    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)
        super(TwitterSearcherException, self).__init__(*args)

class UnDefinedException(TwitterSearcherException):
    """ undefined excepetion, need to implement later"""

class NoneUserException(TwitterSearcherException):
    """ Given User doest not exist """

class TimeStampOutofDate(TwitterSearcherException):
    """ TimeStamp out of date """

class RateLimitException(TwitterSearcherException):
    """ crawler rate reach the API upper limit """

class TableNotExist(TwitterSearcherException):
    """ HBASE Table not exist """
