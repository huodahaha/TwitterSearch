#encoding=utf-8

import os

CUR_WORK_DIRECTORY = os.getcwd()

# Database
HBASE_DOMAIN = "localhost"
RAW_DATA_TABLE = "Twitter_DataTable"
ID_DATA_TABLE = "Tid_DataTable"
IS_TEST = False

# Log Level: DEBUG/WARNING/INFO/ERROR
LOG_LEVEL = "INFO"
PRINT_SCREEN = True

# Twitter Application Set 
CONSUMER_KEY        = "IceR7uq5VJ6ohICoxOZ7yXkqi"
CONSUMER_SECRET     = "EoXhoKIDokcwv39fbADNybqkvSevDhfvHNGXrnxSVnnPCJjiy5"
ACCESS_TOKEN        = "853661430515728384-ba7r6ZI6vDjMaXb0TasvO2aekq87DyR"
ACCESS_TOKEN_SECRET = "6ZlCG3Tzqz7TnHjGUuTvlvrAo92gNM2BBKK503cEWDZtF"

# Twitter Crawler
THREAD_CNT = 20
DEFAULT_TIME_DURATION = 365     # count by day
