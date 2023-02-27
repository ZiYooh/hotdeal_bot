import os
import sys
import psutil

from modules import mylogger

# Logger Setting Start
logger = mylogger.set_logger()
sys.excepthook = mylogger.handle_exception
# Logger Setting End


def check_usage_of_cpu_and_memory():
	pid = os.getpid()
	py  = psutil.Process(pid)

	cpu_usage   = os.popen("ps aux | grep " + str(pid) + " | grep -v grep | awk '{print $3}'").read()
	cpu_usage   = cpu_usage.replace("\n","")

	memory_usage  = round(py.memory_info()[0] /2.**30, 2)

	# print("cpu usage\t\t:", cpu_usage, "%")
	# print("memory usage\t\t:", memory_usage, "%")
	logger.info(f"  CPU 사용량: {cpu_usage}")
	logger.info(f"메모리 사용량: {memory_usage}")
