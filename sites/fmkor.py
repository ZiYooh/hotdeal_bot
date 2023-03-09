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
from modules import myconf


# Logger Setting Start
logger = mylogger.set_logger()
sys.excepthook = mylogger.handle_exception
# Logger Setting End

# URL 설정
fmkor_url = 'https://www.fmkorea.com/hotdeal'


# 임시 변수 선언
temp_num = ''
temp_category = ''
temp_title = ''
temp_price = ''
temp_delivery = ''
temp_link = ''

insert_data_query = ''
select_count_query = ''

temp_msg = ''


class FmkorHotdealInfo:
	def __init__(self, num, category, title, price, delivery, link):
		self.num = num
		self.category = category
		self.title = title
		self.price = price
		self.delivery = delivery
		self.link = link
        
    
	def get_webhook_msg_template(self):
		temp_msg = ''
		
		temp_msg += '카테고리: ' + self.category + '\\n'
		temp_msg += '__**제목: ' + self.title + '**__\\n'
		temp_msg += '가격: ' + self.price + '\\n'
		temp_msg += '배송비: ' + self.delivery + '\\n'
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
	logger.info('[에펨코리아 핫딜 게시판 크롤링 시작]')

	# 페이지 소스 가져오기
	headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'}
	response = requests.get(fmkor_url, headers = headers)
	
	if response.status_code == 200:
		logger.info('HTTP 응답 코드: ' + str(response.status_code))
		html = response.text
		# Soup에 HTML 데이터 넣어주기
		soup = BeautifulSoup(html, 'html.parser')

		# 스크래핑 시작
		div_result = soup.find('div', 'fm_best_widget')
		li_result = div_result.find_all('li')

		for i in range(len(li_result)):
			if li_result[i].find('h3', 'title').find('a').get_text().replace('\n', '') != '':
				# 데이터 가져오기
				temp_num = li_result[i].find('h3', 'title').find('a').get('href').replace('/', '') # 글번호
				temp_category = li_result[i].find('span', 'category').find('a').get_text().replace('\n', '') # 카테고리
				temp_title = li_result[i].find('h3', 'title').find('a').get_text().replace('\n', '') # 제목

				# hotdeal_info 클래스 가진 div 태그에 가격, 배송비 정보가 각각 2번째, 3번째 span 태그에 있음
				temp_price = li_result[i].find('div', 'hotdeal_info').find_all('span')[1].find('a').get_text().replace('\n', '') # 가격
				temp_delivery = li_result[i].find('div', 'hotdeal_info').find_all('span')[2].find('a').get_text().replace('\n', '') # 배송비
				temp_link = f'https://www.fmkorea.com/{temp_num}' # 링크
                
				# DB 연결
				con = sqlite3.connect("./temp_list.db", isolation_level=None)

				# 게시글 중복 유무 확인
				select_count_query = "SELECT count (*) FROM fmkor_list WHERE num=" + temp_num + ";"
				cursor = con.cursor()
				select_count_result = cursor.execute(select_count_query).fetchone()[0]
				cursor.close()

				# 게시글 데이터 삽입 및 모드에 따라 알림 발송
				if select_count_result != 1:
					temp_msg = ''
					
					hotdeal_info = ArcaHotdealInfo(temp_num, temp_category, temp_title, temp_price, temp_delivery, temp_link)
                    
					insert_data_query = "INSERT INTO fmkor_list (num, category, title, price, delivery, link) VALUES (?, ?, ?, ?, ?, ?, )"
					cursor = con.cursor()
					cursor.execute(insert_data_query, (int(temp_num), temp_category, temp_title, temp_price, temp_delivery, temp_link))
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
					
					# ck(혹은 kc) 모드 (설정 키워드 or 카테고리의 새 글)
					if _mode == 'ck' or _mode == 'kc':
						keyword_list = _keyword.split(',')
						category_list = _category.split(',')
						
						# 설정 키워드 확인
						for i in range(0, len(keyword_list)):
							# 문자열 좌우 공백 존재시 제거
							user_set_keyword = keyword_list[i].strip()
							
							if user_set_keyword in hotdeal_info.get_title():
								temp_msg = hotdeal_info.get_webhook_msg_keyword(user_set_keyword)
								logger.info(f'키워드 알림 발송: {user_set_keyword}')
								time.sleep(1)
						
						# 설정 카테고리 확인
						for i in range(0, len(category_list)):
							# 문자열 좌우 공백 존재시 제거
							user_set_category = category_list[i].strip()
							
							if user_set_category in hotdeal_info.get_category():
								temp_msg = hotdeal_info.get_webhook_msg_category(user_set_category)
								logger.info(f'카테고리 알림 발송: {user_set_category}')
								time.sleep(1)
					
					# 웹훅 클래스 생성 및 메세지 전송
					webhook_conf = mywebhook.WebhookConf(_webhook)
					webhook_conf.send_webhook_msg(temp_msg)
					
					del hotdeal_info
					del webhook_conf
		logger.info('[에펨코리아 핫딜 게시판 크롤링 종료]')
	else:			
		logger.error('통신 에러가 발생하였습니다.')
		logger.error('HTTP 응답 코드: ' + str(response.status_code))
		if response.status_code == 429:
			retry_after = response.headers["Retry-After"]
			logger.info(f'Retry-After: {retry_after}')