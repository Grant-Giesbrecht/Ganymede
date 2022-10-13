#!"C:\Users\grant\AppData\Local\Programs\Python\Python310\python.exe"


import psutil
import time
import winsound
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame import mixer

mixer.init()
alert = mixer.Sound("Strange_Noise.wav")

optimizer_proc_name = "awr_as.exe"

num_misses = 0

# Loop indefinitely
while True:
	
	# Pause for 5 seconds
	time.sleep(5)
	
	# Check if process is running
	opt_running = False
	for proc in psutil.process_iter():
		if proc.name() == optimizer_proc_name:
			num_misses = 0
			opt_running = True
			print("Still running...")
			break
	
	# Quit if optimizer is done
	if not opt_running:
		num_misses += 1
	
	if num_misses >= 5:
		print("Optimizer finished!")
		break


# Loop until user turns off alarm
while True:
	
	alert.play()
	
	time.sleep(60)
	
