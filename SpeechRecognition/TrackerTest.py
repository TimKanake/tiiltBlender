#import socket, time
#import subprocess 

##Be sure to download this package. 
import zmq

HOST = ''
PORT = 8220
ADDR = (HOST,PORT)
BUFSIZE = 2048
data = "(200, 430) 12:23:60 EST -"

bytes = data

#subprocess.call(['C:\\Users\\plane\\Documents\\GitHub\\finemotor\\EyeTracker\\EyeTribe.exe'])

#client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#client.connect(ADDR)
#
#total_size_sent = len(data)
#while(True):
#    print(str(total_size_sent) + "   # of messages: " + str(total_size_sent / len(data)))
#    client.send(bytes)
#    total_size_sent += len(data)
#    time.sleep(0.01)
#
#
#
#
#client.close()

context = zmq.Context()
socket = context.socket(zmq.SUB)

socket.connect("tcp://localhost:8220")

topic = "9001"
socket.setsockopt(zmq.SUBSCRIBE, topic)

while True:
    response = socket.recv()
    print response

