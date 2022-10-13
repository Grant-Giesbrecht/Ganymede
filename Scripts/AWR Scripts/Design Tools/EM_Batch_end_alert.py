#!"C:\Users\grant\AppData\Local\Programs\Python\Python310\python.exe"


import psutil
import time
import winsound
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame import mixer

mixer.init()
alert = mixer.Sound("Strange_Noise.wav")

optimizer_proc_name = "AXIEM.exe"

quit_condition = 3;


# Check if process is running
num_axiem_missed = 0
while True:
	
	# Pause for 5 seconds
	time.sleep(5)
	
	# Check if AXIEM process is found
	found_axiem = False
	for proc in psutil.process_iter():
		if proc.name() == optimizer_proc_name:
			found_axiem = True
			print("Still running...")
	
	# Update counter
	if found_axiem:
		num_axiem_missed = 0
	else:
		num_axiem_missed += 1
		print(f"Found instance of missing AXIEM (No. = {num_axiem_missed})")
		
	if num_axiem_missed >= quit_condition:
		print("Batch complete")
		break;


# Loop until user turns off alarm
while True:
		
	alert.play()
	
	time.sleep(60)
	
