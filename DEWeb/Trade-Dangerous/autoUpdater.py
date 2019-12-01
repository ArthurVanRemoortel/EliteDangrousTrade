import time
import os
import subprocess


cmd = 'python3 trade.py import -P eddblink'
cmd2 = 'python3 trade.py'
cmd3 = 'cd tradedangerous && ls'
cmd4 = 'python3 trade.py import -P eddblink'
#print(subprocess.check_output(cmd4, shell=True))

initial_command = 'python3 trade.py import -P eddblink'
update_command = 'python3 trade.py import -P eddblink -O all'
while True:
	process = subprocess.run(update_command.split(' '), check=True, stdout=subprocess.PIPE, universal_newlines=True)
	print("------"*10)
	time.sleep(3600*6)