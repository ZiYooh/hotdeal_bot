import datetime
import logging
import logging.handlers
import os
import sys

from rich.logging import RichHandler
from logging.handlers import RotatingFileHandler

# LOG_PATH = "./log/agent_log_{:%Y%m%d_%H%M%S}".format(datetime.datetime.now()) + ".log"
LOG_PATH = "./log/hotdealbot_logfile" + ".log"
RICH_FORMAT = "[%(filename)s:%(lineno)s] >> %(message)s"
FILE_HANDLER_FORMAT = "[%(asctime)s]\t%(levelname)s\t[%(filename)s:%(funcName)s:%(lineno)s]\t>> %(message)s"

LOG_MAX_SIZE = 1024 * 1204 * 5  # 로그 파일 크기 개당 최대 5MB

def set_logger() -> logging.Logger:
    # 로그 파일 경로 존재 확인
    if not os.path.isdir('./log'):
        try:
            if not os.path.exists('./log'):
                os.makedirs('./log')
            else:
                pass
        except OSError:
            os._exit(0)

            
    # Rich 로거 기본 설정
    logging.basicConfig(
        level="INFO",
        format=RICH_FORMAT,
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    logger = logging.getLogger("rich")

    # 각 모듈 마다 중복 로깅 되는 현상 방지
    if logger.hasHandlers():
        logger.handlers = []

    # 파일 핸들러 설정
    # file_handler = logging.FileHandler(LOG_PATH, mode="a", maxBytes=LOG_MAX_SIZE, encoding="utf-8")
    file_handler = RotatingFileHandler(LOG_PATH, mode="a", maxBytes=LOG_MAX_SIZE, encoding="utf-8", backupCount=40)
    file_handler.setFormatter(logging.Formatter(FILE_HANDLER_FORMAT))
    logger.addHandler(file_handler)

    return logger


def handle_exception(exc_type, exc_value, exc_traceback):
    logger = logging.getLogger("rich")

    logger.error("Unexpected exception",
                 exc_info=(exc_type, exc_value, exc_traceback))