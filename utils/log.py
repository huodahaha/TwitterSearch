#encoding=utf-8

import logging

from SearchEngine.conf import LOG_LEVEL, CUR_WORK_DIRECTORY
from . import mkdir_p

WSE_LOG_NAME = "WSE.log"
WSE_LOG_DIR = CUR_WORK_DIRECTORY + "/tmp/log"
WSE_LOG_PATH = WSE_LOG_DIR + "/" + WSE_LOG_NAME

def init_log():
    """
    Configure Log System
    """
    logger = logging.getLogger("WebSearchEngineApp")

    if LOG_LEVEL == "DEBUG":
        logger.setLevel(logging.DEBUG)
    elif LOG_LEVEL == "WARNING":
        logger.setLevel(logging.WARNING)
    elif LOG_LEVEL == "INFO":
        logger.setLevel(logging.INFO)
    elif LOG_LEVEL == "ERROR":
        logger.setLevel(logging.ERROR)
    else:
        print "log level set fail, should be DEBUG/WARNING/INFO/ERROR"
        print "current level <%s>"%LOG_LEVEL
        exit(-1)

    mkdir_p(WSE_LOG_DIR)
    log_fh = logging.FileHandler(WSE_LOG_PATH)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(funcName)s -\
            %(lineno)d -%(levelname)s - %(message)s')
    log_fh.setFormatter(formatter)
    # add handler to logger object
    logger.addHandler(log_fh)
    logger.info("Log System inited")

    return logger
