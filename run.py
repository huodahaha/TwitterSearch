#encoding=utf-8

from datetime import datetime

from TwitterSearch.web import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000) 
