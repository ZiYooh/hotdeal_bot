# -*- coding: UTF-8 -*-
import time
import os
import sys
import requests
import sqlite3

from bs4 import BeautifulSoup
from sqlite3 import OperationalError

# 절대경로 참조
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from modules import mylogger
from modules import mywebhook


# Logger Setting Start
logger = mylogger.set_logger()
sys.excepthook = mylogger.handle_exception
# Logger Setting End

# URL 설정
ruli_url = 'https://bbs.ruliweb.com/market/board/1020'


# 임시 변수 선언
temp_num = ''
temp_category = ''
temp_title = ''
temp_link = ''

insert_data_query = ''
select_count_query = ''

temp_msg = ''


class RuliHotdealInfo:
	def __init__(self, num, category, title, link):
		self.num = num
		self.category = category
		self.title = title
		self.link = link
        
    
	def get_webhook_msg_template(self):
		temp_msg = ''
		
		temp_msg += '카테고리: ' + self.category + '\\n'
		temp_msg += '__**제목: ' + self.title + '**__\\n'
		temp_msg += '링크: ' + self.link
        
		return temp_msg
    
    
	def get_webhook_msg_all(self):
		temp_msg = ''
		
		temp_msg = '>>> _새글 알림_\\n' 
		temp_msg += self.get_webhook_msg_template()
        
		return temp_msg

	
	def get_webhook_msg_category(self, category):
		temp_msg = ''
		
		temp_msg = f'>>> _카테고리 알림 [{category}]_\\n' 
		temp_msg += self.get_webhook_msg_template()

		return temp_msg
	
	
	def get_webhook_msg_keyword(self, keyword):
		temp_msg = ''
		
		temp_msg = f'>>> _키워드 알림 [{keyword}]_\\n' 
		temp_msg += self.get_webhook_msg_template()

		return temp_msg
	
	
	def get_category(self):
		return self.category
	
	
	def get_title(self):
		return self.title
	

def run_scraping(_webhook, _mode, _category, _keyword):
	logger.info('[루리웹 핫딜 게시판 크롤링 시작]')

	# 페이지 소스 가져오기
	response = requests.get(ruli_url)
	if response.status_code == 200:
		logger.info('HTTP 응답 코드: ' + str(response.status_code))
		html = response.text
		# Soup에 HTML 데이터 넣어주기
		soup = BeautifulSoup(html, 'html.parser')

		# 스크래핑 시작
		tbody_result = soup.find('tbody')
		tr_result = tbody_result.find_all('tr', 'table_body blocktarget')
		
		for i in range(len(tr_result)):
			# 데이터 가져오기
			if tr_result[i].find('td', 'id').get_text().replace('\n', '') != '':
				temp_num = tr_result[i].find('td', 'id').get_text().replace('\n', '').strip() # 글번호
			
			if tr_result[i].find('td', 'divsn').find('a').get_text().replace('\n', '') != '':
				temp_category = tr_result[i].find('td', 'divsn').find('a').get_text().replace('\n', '').strip() # 카테고리
			
			if tr_result[i].find('td', 'subject').find('a', 'deco').get_text().replace('\n', '') != '':
				temp_title = tr_result[i].find('td', 'subject').find('a', 'deco').get_text().replace('\n', '').strip() # 글제목
				temp_link = tr_result[i].find('td', 'subject').find('a', 'deco').get('href') #링크
	
			# DB 연결
			con = sqlite3.connect("./temp_list.db", isolation_level=None)

			# 게시글 중복 유무 확인
			select_count_query = "SELECT count (*) FROM ruli_list WHERE num=" + temp_num + ";"
			cursor = con.cursor()
			select_count_result = cursor.execute(select_count_query).fetchone()[0]
			cursor.close()

			# 게시글 데이터 삽입 및 모드에 따라 알림 발송
			if select_count_result != 1:
				temp_msg = ''

				hotdeal_info = RuliHotdealInfo(temp_num, temp_category, temp_title, temp_link)

				insert_data_query = "INSERT INTO ruli_list (num, category, title, link) VALUES (?, ?, ?, ?)"
				cursor = con.cursor()
				cursor.execute(insert_data_query, (int(temp_num), temp_category, temp_title, temp_link))
				cursor.close()

				# a 모드 (모든 새 글)
				if _mode is 'a':
					temp_msg = hotdeal_info.get_webhook_msg_all()
					logger.info('새글 알림 발송')
					time.sleep(1)

				# c 모드 (설정 카테고리의 새 글)
				if _mode is 'c':
					category_list = _category.split(',')

					# 설정 카테고리 확인
					for i in range(0, len(category_list)):
						# 문자열 좌우 공백 존재시 제거
						user_set_category = category_list[i].strip()

						if user_set_category in hotdeal_info.get_category():
							temp_msg = hotdeal_info.get_webhook_msg_category(user_set_category)
							logger.info(f'카테고리 알림 발송: {user_set_category}')
							time.sleep(1)


				# k 모드 (설정 키워드의 새 글)
				if _mode is 'k':
					keyword_list = _keyword.split(',')

					# 설정 키워드 확인
					for i in range(0, len(keyword_list)):
						# 문자열 좌우 공백 존재시 제거
						user_set_keyword = keyword_list[i].strip()

						if user_set_keyword in hotdeal_info.get_title():
							temp_msg = hotdeal_info.get_webhook_msg_keyword(user_set_keyword)
							logger.info(f'키워드 알림 발송: {user_set_keyword}')
							time.sleep(1)

				# 웹훅 클래스 생성 및 메세지 전송
				webhook_conf = mywebhook.WebhookConf(_webhook)
				webhook_conf.send_webhook_msg(temp_msg)

				del hotdeal_info
				del webhook_conf
		logger.info('[루리웹 핫딜 게시판 크롤링 종료]')
		
	else:
		logger.error('통신 에러가 발생하였습니다.')
		logger.error('HTTP 응답 코드: ' + str(response.status_code))