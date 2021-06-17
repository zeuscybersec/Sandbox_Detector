import ctypes
import random
import time
import sys

user32   = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

keystrokes    = 0
mouse_clicks  = 0
double_clicks = 0 

class LASTINPUTINFO(ctypes.Structure):
	_fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_ulong)]

def get_last_input():

	struct_lastinputinfo = LASTINPUTINFO()
	struct_lastinputinfo.cbSize = ctypes.sizeof(LASTINPUTINFO)

	# get last input regestered
	user32.GetLastInputInfo(ctypes.byref(struct_lastinputinfo))

	# now determine how long the machine has been running 
	run_time = kernel32.GetTickCount()

	elapsed = run_time - struct_lastinputinfo.dwTime

	print("[*] It's been %d milliseconds since last input event." % (elapsed))
	return elapsed


def get_key_press():
		
	global mouse_click
	global keystrokes

	for i in range(0, 0xff):
		if user32.GetAsyncKeyState(i) == -32767:
			# 0x1 is the code for left mouse click
			if i == 0x1:
				mouse_click +=1 
				return time.time()
			elif i > 32 and i < 127:
				keystrokes += 1
	return None


def detect_sandbox():
	global mouse_click
	global keystrokes

	max_keystrokes         = random.randint(10, 25)
	max_mouse_clicks       = random.randint(5, 25)
	double_click           = 0
	max_double_clicks      = 10 
	double_click_threshold = 0.250 # in seconds
	first_double_click     = None
	average_mousetime      = 0
	max_input_threshold    = 30000 # in milliseconds
	previous_timestamp     = None
	detection_complete     = False

	while not detection_complete:	
		time.sleep(5)
		last_input = get_last_input()
		if last_input >= max_input_threshold:
			detection_complete = True
		
		keypress_time = get_key_press()
		if keypress_time is not None and previous_timestamp is not None:

			# calculate the time between double clicks
			elapsed = keypress_time - previous_timestamp

			# the user double clicked
			if elapsed <= double_click_threshold:
				double_clicks += 1

				if  first_double_click is None:

					# grab the timestamp of first double click
					first_double_click = time.time()

				else:
					# did they try to emulate a rapid of clicks?
					if double_clicks == max_double_clicks:
						if keypress_time - first_double_click <= (max_double_click * double_click_threshold):	
							sys.exit(0)

			# we are happy there's enough user input
			if keystrokes >= max_keystrokes and double_clicks >= max_double_clicks and mouse_clicks >= max_mouse_clicks:
				return

			previous_timestamp = keypress_time

		elif keypress_time is not None:
			previous_timestamp = keypress_time


detect_sandbox()
print("We are ok!")
time.sleep(10)
# visit for detailed info:
# https://github.com/zedxpace/SandboxDetection-with-python/blob/master/sandboxdetection.py