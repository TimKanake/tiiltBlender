# -*- coding: utf-8 -*-
"""
Created on Sat Apr 15 11:11:03 2017

@author: Haley
"""
## NOTE: You must run the EyeTribe Server (in EyeTracker folder) first, then this file, then the TrackerTest.py
## You'll notice on start-up that a screen flashes without info. This is normal
## OS might complain at the "connection request" from the server, but its not doing anything shady
import zmq
import time
from pygaze.display import Display
from pygaze.screen import Screen
from pygaze.eyetracker import EyeTracker

disp = Display(disptype='psychopy')
scr = Screen(disptype='psychopy')
disp.close()
tracker = EyeTracker(disp, trackertype='eyetribe')

print "start"
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:%s" % 8220)

#must send random 'topic' value for subscriber to subscribe to.
while True:


    data = tracker.sample()
    time_val = (time.time() - 1492478000)
    data_plus_time = str(data + (time_val,))
    topic = 9001
    socket.send("%d %s" % (topic, data_plus_time))

