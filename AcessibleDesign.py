import signal
import subprocess
import time
import sys
import platform
import argparse
from Tkinter import *
import tkFileDialog
import psutil
import os
from os.path import join

global subs
global directory

def main():
	parser = argparse.ArgumentParser(description='Specifies options (Watson, PocketSphinx, Text Input) for command input.')
	parser.add_argument('--input', dest='input_method', default='text', help='Specify the input method that will be used (default: sphinx)', choices = ['watson', 'sphinx','text'])

	args = vars(parser.parse_args())
	input_method = args['input_method']
	global subs
	global directory

	subs = []
	directory = None

	sys.stdout.write("\033[1;31m") # Red
	print 'Press Ctrl-C to kill all AccessibleDesign processes'

	plat = platform

	try:
		root = Tk()
		root.withdraw()
		root.update()
		directory = tkFileDialog.askdirectory(initialdir='.')
		while not directory:
			time.sleep(0.1)
		root.update()
		root.destroy()

		if plat.system() == 'Windows': # Windows
			eye_tribe = subprocess.Popen("EyeTracker/EyeTribe.exe", stdout=subprocess.PIPE, shell=False)
		elif plat.system() == 'Darwin': # MacOS
			eye_tribe = subprocess.Popen("EyeTracker/EyeTribe", stdout=subprocess.PIPE, shell=False)
		else:
			print 'Unsupported Operating System'
			exit()
		
		subs.append(eye_tribe)
		recognition_sockets = subprocess.Popen(['python', 'RecognitionSockets.py', '--input', input_method], cwd='SpeechRecognition', stdout=subprocess.PIPE, shell=False)
		subs.append(recognition_sockets)

		#find_dir()
		blender = subprocess.Popen('./blender.app/Contents/MacOS/blender -d --python tiilt/blender.py', stdout=subprocess.PIPE, cwd=directory, shell=True)
		subs.append(blender)

		sys.stdout.write("\033[0;32m") # Green
		print ''
		print 'Process PIDs...'
		print 'eye_tribe = ', eye_tribe.pid
		print 'recognition_sockets = ', recognition_sockets.pid
		print 'blender = ', blender.pid
		sys.stdout.write("\033[0;0m") # Reset
		print ''

	except Exception as e:
		# If any of them couldn't open
		raise e
		exit()

	while True:
		try:
			for sub in subs:
				if sub.poll():
					exit()
		except KeyboardInterrupt:
			exit()

def find_dir():
	lookfor = "blender.app"
	temp_dir = ''
	if platform.system() == 'Windows':
		temp_dir = 'C:\\'
	elif platform.system() == 'Darwin':
		temp_dir = '/'
	else:
		return
	walklevel(lookfor, temp_dir, 1)
	return

def walklevel(lookfor, some_dir, level=1):
    some_dir = some_dir.rstrip(os.path.sep)
    assert os.path.isdir(some_dir)
    num_sep = some_dir.count(os.path.sep)
    for root, dirs, files in os.walk(some_dir):
        yield root, dirs, files
        print "searching ", root
        if lookfor in files:
        	print "found: %s" % join(root, lookfor)
        	break
        num_sep_this = root.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]

def kill_proc_tree(pid, including_parent=True):    
    parent = psutil.Process(pid)
    children = parent.children(recursive=True)
    for child in children:
        child.kill()
    gone, still_alive = psutil.wait_procs(children, timeout=5)
    if including_parent:
        parent.kill()
        parent.wait(5)

# Kill processes and exit shell
def exit():
	global subs
	sys.stdout.write("\033[1;31m") # Red
	for sub in subs:
		try:
			kill_proc_tree(sub.pid)
		except Exception as e:
			print ''
			print 'Subprocess error'
			print e, ' -- ', sub.pid
	sys.stdout.write("\033[0;0m") # Reset
	print ''
	sys.exit()


# https://stackoverflow.com/questions/1230669/subprocess-deleting-child-processes-in-windows

main()