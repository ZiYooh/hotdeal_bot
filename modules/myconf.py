# -*- coding: UTF-8 -*-
import time
import os
import sys

from modules import mylogger


# Logger Setting Start
logger = mylogger.set_logger()
sys.excepthook = mylogger.handle_exception
# Logger Setting End


class HotdealConf:
	def __init__(self):
		# setting.conf에서 값 읽어옴
		logger.info("설정값 클래스 생성")
        
		with open('setting.conf', 'r') as file:    # setting.conf 파일을 읽기 모드(r)로 열기
			line = None    # 변수 line을 None으로 초기화
			while line != '':
				line = file.readline().strip('\n')
				
				# 설정파일 내용 확인
				logger.debug("setting.conf 파일 내용")
				logger.debug(line)
				
				if 'WEBHOOK=' in line:
					self.conf_webhook = line.split('=')[1]

				if 'INTERVAL=' in line:
					self.conf_interval = line.split('=')[1]

				if 'MODE=' in line:
					self.conf_mode = line.split('=')[1]

				if 'CATEGORY=' in line:
					self.conf_category = line.split('=')[1]	

				if 'KEYWORD=' in line:
					self.conf_keyword = line.split('=')[1]
					
	def check_conf_value(self):
		logger.info("설정값 검사 시작")
		
		# 시간 간격
		# 1분 (60) ~ 24시간 (86400)
		if int(self.conf_interval) < 60 or int(self.conf_interval) > 86400:
			logger.error("INTERVAL 설정값이 잘못되었습니다.")
			logger.error("기본 설정값(300=5분)으로 동작합니다.")
			self.conf_interval = 300
		
		# 동작 모드
		# a = 모든 새글
		# c = 카테고리
		# k = 키워드
		if self.conf_mode != 'a' and self.conf_mode != 'c' and self.conf_mode != 'k' and self.conf_mode != 'ck' and self.conf_mode != 'kc': 
			logger.error("MODE 설정값이 잘못되었습니다.")
			logger.error("기본 설정값(a)으로 동작합니다.")
			self.conf_mode = 'a'
			
		logger.info("설정값 검사 종료")
		return

	
	def update_conf(self):
		with open('setting.conf', 'r') as file:    # setting.conf 파일을 읽기 모드(r)로 열기
			line = None
			
			while line != '':
				line = file.readline().strip('\n')
				if 'WEBHOOK=' in line:
					if line.split('=')[1] != self.conf_webhook:
						self.conf_webhook = line.split('=')[1]
						logger.info("WEBHOOK 설정값 변경 완료")

				if 'INTERVAL=' in line:
					if line.split('=')[1] != self.conf_interval:
						self.conf_interval = line.split('=')[1]
						logger.info("INTERVAL 설정값 변경 완료")

				if 'MODE=' in line:
					if line.split('=')[1] != self.conf_mode:
						self.conf_mode = line.split('=')[1]
						logger.info("MODE 설정값 변경 완료")

				if 'CATEGORY=' in line:
					if line.split('=')[1] != self.conf_category:
						self.conf_category = line.split('=')[1]
						logger.info("CATEGORY 설정값 변경 완료")

				if 'KEYWORD=' in line:
					if line.split('=')[1] != self.conf_keyword:
						self.conf_keyword = line.split('=')[1]
						logger.info("KEYWORD 설정값 변경 완료")

						
	def get_webhook(self):
		return self.conf_webhook
	
	
	def get_interval(self):
		return int(self.conf_interval)


	def get_mode(self):
		return self.conf_mode

	
	def get_category(self):
		return self.conf_category
	
	
	def get_keyword(self):
		return self.conf_keyword


def check_conf_file():
	if not os.path.isfile('./setting.conf'):
		logger.error("!! setting.conf 파일이 존재하지 않습니다.")
		logger.error("!! main.py와 같은 경로에 위치하여야 합니다.")
		return -1