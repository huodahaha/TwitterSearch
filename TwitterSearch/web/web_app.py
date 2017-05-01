#encoding
import json
from datetime import datetime
from flask import Flask, render_template, request

from TwitterSearch.analyzer.exceptions import * 
from TwitterSearch.analyzer.analyzer import * 
from TwitterSearch.utils.util import date2ts

app = Flask(__name__, static_url_path="/static")

def extract_arg(args):
    related_user_cnt = args.get("related_user_cnt")
    related_user_cnt = 0 if not related_user_cnt else int(related_user_cnt)

    start_date = args.get("begin_date")
    end_date = args.get("end_date")

    start_year =int(start_date.split("/")[2])
    start_month =int(start_date.split("/")[0])
    start_day =int(start_date.split("/")[1])

    end_year =int(end_date.split("/")[2])
    end_month =int(end_date.split("/")[0])
    end_day =int(end_date.split("/")[1])

    start_ts = date2ts(start_year, start_month, start_day)
    end_ts = date2ts(end_year, end_month, end_day)
    return start_ts, end_ts, related_user_cnt

def dump_error_msg(msg):
    ret = {}
    ret["errcode"] = 1
    ret["errmsg"] = msg
    ret["result"] = None
    return json.dumps(ret)

@app.route('/')
def main_page():
    return render_template("twitter_search.html")

@app.route("/SearchTwitter")
def search():
    ret = {}
    # 0. extract users
    user_name = request.args.get("user_name")
    print "========================="
    print request.args.get("user_name")

    if user_name is None:
        return dump_error_msg("user_name is None")

    # 1. extract search text
    text = request.args.get("search_text")
    if text is None:
        return dump_error_msg("search text is None")

    # 2. extract other parameters
    start_ts, end_ts, related_cnt = extract_arg(request.args)
    if end_ts <= start_ts:
        return dump_error_msg("end time < start time")
    elif (related_cnt < 0) or (related_cnt > 20):
        return dump_error_msg("related_cnt should be [0,20]")

    # 3. seaerch result
    try:
        result, users = search_text(user_name, text, start_ts, end_ts, related_cnt)
    except NoneUserException:
        return dump_error_msg("user_name does not exist")
    except RateLimitException:
        return dump_error_msg("raeach API rate limit! Wait 15 mininutes and try again")
    except TableNotExist:
        return dump_error_msg("Hbase database unset")
    # except Exception as e:
	# print e
        # return dump_error_msg("unexpected error")
    else:
        ret["errcode"] = 0
        ret["errmsg"] = "OK"
        ret["related_users"] = users
        ret["result"] = result
        return json.dumps(ret)

@app.route("/Keyword")
def keyword():
    ret = {}
    # 0. extract users
    user_name = request.args.get("user_name")
    if user_name is None:
        return dump_error_msg("user_name is None")

    # 1. extract other parameters
    start_ts, end_ts, related_cnt = extract_arg(request.args)
    if end_ts <= start_ts:
        return dump_error_msg("end time < start time")
    elif (related_cnt < 0) or (related_cnt > 20):
        return dump_error_msg("related_cnt should be [0,20]")

    try:
        result, users = get_keywords(user_name, start_ts, end_ts, related_cnt)
    except NoneUserException:
        return dump_error_msg("user_name does not exist")
    except RateLimitException:
        return dump_error_msg("raeach API rate limit! Wait 15 mininutes and try again")
    except TableNotExist:
        return dump_error_msg("Hbase database unset")
    # except Exception as e:
	# print e
    else:
        ret["errcode"] = 0
        ret["errmsg"] = "OK"
        ret["related_users"] = users
        ret["result"] = result
        return json.dumps(ret)
