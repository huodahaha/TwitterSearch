#encoding=utf-8
from TwitterSearch

def test_put():
    tweet_list = []
    tweet_list.append({"ts":1000, "id":2000, "user_name":"111", "text":"text", "word_bag":["word", "bag"]})
    tweet_list.append({"ts":1001, "id":2000, "user_name":"111", "text":"text", "word_bag":["word", "bag"]})
    tweet_list.append({"ts":1002, "id":2000, "user_name":"111", "text":"text", "word_bag":["word", "bag"]})
    put_raw_data(tweet_list)

def test_get():
    test_put()
    print get_raw_data(["111"], 1000, 1002)

def test_is_exist():
    is_user_data_exist("000")

if __name__ == "__main__":
    test_is_exist()
