#encoding
import re
from datetime import datetime
from flask import Flask, render_template, request

from TwitterSearch.analyzer.exceptions import * 
from TwitterSearch.analyzer.analyzer import * 
from TwitterSearch.utils.util import date2ts

app = Flask(__name__, static_url_path="/static")

def extract_arg(arg):
    related_user_cnt = args.get("related_user_cnt")
    related_user_cnt = 0 if not related_users else int(related_user_cnt)

    start_year = args.get("start_year")
    start_year = 2016 if not start_year else int(start_year)

    start_month = args.get("start_month")
    start_month = 1 if not start_month else int(start_month)

    start_day = args.get("start_day")
    start_day = 1 if not start_day else int(start_day)

    end_year = args.get("end_year")
    end_year = 2018 if not end_year else int(end_year)

    end_month = args.get("end_month")
    end_month = 1 if not end_month else int(end_month)

    end_day = args.get("end_day")
    end_day = 1 if not end_day else int(end_day)

    start_ts = date2ts(start_year, start_month, start_day)
    end_ts = date2ts(end_year, end_month, end_day)
    return start_ts, end_ts, related_user_cnt

@app.route('/')
def main_page():
    return render_template("main.html")

@app.route('/check_user')
def check_user():
    user_name = request.args.get("user_name")
    if user_name is None:
        return render_template('main.html')

@app.route('/search_text')
def search():
    user_name = request.args.get("user_name")
    if user_name is None:
        return render_template("main.html")

    # 1. extract keyword
    start_ts, end_ts, related_cnt = extract_arg(request.args)

    # 2. search in filed introduction and teacher
    start = datetime.now()
    search_res = search_text(user_name, start_ts, end_ts, related_cnt)
    end = datetime.now()

    if (len(courses_info) == 0):
        return render_template('no_result.html', keyword = q)
    else:
        return render_template('display_new.html', keyword = q, search_res = search_res
                , search_times = (end-start).total_seconds(), cnt=len(search_res))
