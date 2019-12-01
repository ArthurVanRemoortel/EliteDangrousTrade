import time
import os
import subprocess

cmd = 'python3 trade.py import -P eddblink'

print(subprocess.call(cmd.split(' ')))