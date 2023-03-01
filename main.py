# -*- coding: UTF-8 -*-
import time
import os
import sys
import requests
import sqlite3
import psutil
import atexit

from bs4 import BeautifulSoup
from sqlite3 import OperationalError

from modules import mylogger
from modules import mywebhook
from modules import myutil
from modules import myconf

from sites import arca
from sites import ruliweb
from sites import ppomppu

# 로거 설정
logger = mylogger.set_logger()
sys.excepthook = mylogger.handle_exception


def handle_exit(_webhook, _exit_msg):
	webhook_conf = mywebhook.WebhookConf(_webhook)
	webhook_conf.send_webhook_msg(_exit_msg)

	
if __name__ == "__main__":
	con = sqlite3.connect("./temp_list.db", isolation_level=None)
	
	try:
		cursor = con.cursor()
		cursor.execute(
			  "CREATE TABLE arca_list (\
				  num INT NOT NULL,\
				  category VARCHAR(512),\
				  title VARCHAR(512),\
				  price VARCHAR(512),\
				  delivery VARCHAR(512),\
				  link VARCHAR(512),\
				  time VARCHAR(512),\
				  PRIMARY KEY (num)\
				);"
		  )
		cursor.close()
	except OperationalError:
		pass

	try:
		cursor = con.cursor()
		cursor.execute(
			  "CREATE TABLE ruli_list (\
				  num INT NOT NULL,\
				  category VARCHAR(512),\
				  title VARCHAR(512),\
				  link VARCHAR(512),\
				  PRIMARY KEY (num)\
				);"
		  )
		cursor.close()
	except OperationalError:
		pass
	
	try:
		cursor = con.cursor()
		cursor.execute(
			  "CREATE TABLE ppom_list (\
				  num INT NOT NULL,\
				  category VARCHAR(512),\
				  title VARCHAR(512),\
				  link VARCHAR(512),\
				  PRIMARY KEY (num)\
				);"
		  )
		cursor.close()
	except OperationalError:
		pass
	index = 1
	
	hotdeal_conf = myconf.HotdealConf()
	
	cur_pid = os.getpid()
	cur_ppid = psutil.Process(os.getpid()).ppid()
	
	ps_start_msg = f"프로세스 시작 [PID={cur_pid} | PPID={cur_ppid}]"
	ps_end_msg = f"프로세스 종료 [PID={cur_pid} | PPID={cur_ppid}]"
	webhook_conf = mywebhook.WebhookConf(hotdeal_conf.get_webhook())
	webhook_conf.send_webhook_msg(ps_start_msg)
	del webhook_conf
	
	atexit.register(handle_exit, hotdeal_conf.get_webhook(), ps_end_msg)
	
	while 1:
		logger.info(f"{index} 회차 루프중")
		myutil.check_usage_of_cpu_and_memory()
		hotdeal_conf.update_conf()
		hotdeal_conf.check_conf_value()	

		arca.run_scraping(hotdeal_conf.get_webhook(),
						  hotdeal_conf.get_mode(),
						  hotdeal_conf.get_category(),
						  hotdeal_conf.get_keyword()
						)
		
		ruliweb.run_scraping(hotdeal_conf.get_webhook(),
						  	hotdeal_conf.get_mode(),
						  	hotdeal_conf.get_category(),
							hotdeal_conf.get_keyword()
						)
		
		ppomppu.run_scraping(hotdeal_conf.get_webhook(),
						  	hotdeal_conf.get_mode(),
						  	hotdeal_conf.get_category(),
							hotdeal_conf.get_keyword()
						)
		index += 1
        
		time.sleep(hotdeal_conf.get_interval())