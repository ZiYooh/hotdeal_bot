import sys
import requests

from modules import myconf
from modules import mylogger


# Logger Setting Start
logger = mylogger.set_logger()
sys.excepthook = mylogger.handle_exception
# Logger Setting End


# 웹훅 설정
class WebhookConf:
	def __init__(self, url):
		logger.debug("웹훅 클래스 생성")
		self.discord_webhook = url
		self.headers = {
    		'Content-Type': 'application/json',
		}


	def set_webhook_url(self, url):
		self.discord_webhook = url

    
	def send_webhook_msg(self, msg):
		data = '{"content": "' + msg + '"}'
		data = data.encode('utf-8').decode('iso-8859-1')
		response = requests.post(self.discord_webhook, headers=self.headers, data=data)

