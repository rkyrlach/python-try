
import can
import socket
from _thread import *
import threading
#import multiprocessing
import time
import logging

import serial
import binascii
import array as arr

cfc="                                                   "             # command from client
dmxbuf = arr.array('b', [0,0,0,0,0,0,0,0,0])                          # dmx lights all off
ser = serial.Serial(port = "/dev/ttyS5", baudrate=250000, stopbits=2) # setup dmx port
#bus = can.interface.Bus('can0', bustype='socketcan_native')           # setup can
tacho = 0
vin = 0

def msg(nn):
    switcher={
       2305:'VESC Status message 1 ', # bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00')
       3585:'VESC Status message 2 ', # bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00')
       3841:'VESC Status message 3 ', # bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00')
       4097:'VESC Status message 4 ', # bytearray(b'\x01\x1a\xfc\x99\x00\x00\x18\xf5')
       6913:'VESC Status message 5 '} # bytearray(b'\x00\x00\x00\x96\x00\xef\x00\x00')
    return switcher.get(nn,"Invalid can message")

def canStat():
  global tacho
  global vin
  bus = can.interface.Bus('can0', bustype='socketcan_native')           # setup can
  while True:
     message = bus.recv()
     print ('id = ', message.arbitration_id)
     num = int(message.arbitration_id)
     msgn = msg(num)
     if(msgn.find('5') != -1):
        print ('msg from can = ', message.data)
        a=message.data[0]; b=message.data[1]; c=message.data[2]; d=message.data[3]
        e=message.data[4]; f=message.data[5]
        tacho = (d + (c*256) + (b*65536) + (a*16777216))
        if(a==255): tacho = tacho-4294967296
        vin = (f + (e*256))/10.0
#        print ("\033[44;1Htacho = ", tacho, " Vin = ", vin)
        print ("tacho = ", tacho, " Vin = ", vin)

def dmxset():
    print("dummy for now")

def dmx():
   global cfc
   global dmxbuf
   while True:
      dmx="".join( chr(x) for x in dmxbuf)
#      print ("command = ", cfc[0], cfc[1])
      if ((cfc[0] == "c") & (cfc[1] == "t")):
         st = cfc.find(',')                  # first comma
         nd = cfc.find(',' , st+1)           # second comma
         aa = int('{}'.format(cfc)[st+1:nd]) # first parameter
#         print("first parm = ", aa)
         st = nd                             # second comma
         nd = cfc.find(',' , st+1)           # third comma
         bb = int('{}'.format(cfc)[st+1:nd]) # second parameter
#         print("second  parm = ", bb)
         st = nd                             # third comma
         nd = cfc.find(',' , st+1)           # forth comma
         cc = int('{}'.format(cfc)[st+1:nd]) # third parameter
#         print("third  parm = ", cc)
         st = nd                             # forth comma
         nd = len(cfc)                       # end of string
         dd = int('{}'.format(cfc)[st+1:nd]) # third parameter
#         print("fourth  parm = ", dd)
         dmxbuf[0]=aa                        # target red
         dmxbuf[1]=bb                        # target green
         dmxbuf[2]=cc                        # target blue
         dmxbuf[3]=dd                        # target white

      if ((cfc[0] == "c") & (cfc[1] == "a")):
         st = cfc.find(',')                  # first comma
         nd = cfc.find(',' , st+1)           # second comma
         aa = int('{}'.format(cfc)[st+1:nd]) # first parameter
#         print("first parm = ", aa)
         st = nd                             # second comma
         nd = cfc.find(',' , st+1)           # third comma
         bb = int('{}'.format(cfc)[st+1:nd]) # second parameter
#         print("second  parm = ", bb)
         st = nd                             # third comma
         nd = cfc.find(',' , st+1)           # forth comma
         cc = int('{}'.format(cfc)[st+1:nd]) # third parameter
#         print("third  parm = ", cc)
         dd = 0
#         print("fourth  parm = ", dd)
         dmxbuf[5]=aa                        # accent red
         dmxbuf[6]=bb                        # accent green
         dmxbuf[7]=cc                        # accent blue
         dmxbuf[8]=dd
      ser.send_break()
      ser.write(dmxbuf)
#      time.sleep(1)


print_lock = threading.Lock()

# thread function
def threaded(cz):
	global cfc
	while True:

		# data received from client
		dataz = cz.recv(1024)
		if not dataz:
			print('Bye')

			# lock released on exit
			print_lock.release()
			break

		# reverse the given string from client
		# data = data[::-1]
		# send back reversed string to client
		cz.send(dataz)
#		print ("data = ", data)
		cfc="".join( chr(x) for x in dataz)
#		print ("cfc = ", cfc)
#		print ("cfc type = ", type(cfc))
	# connection closed
	cz.close()


def Main():
	host = ""  ###  client is "10.249.1.2" but could be anyone
	# reserved port is 12345 but it can be anything
	port = 12345
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((host, port))
	print("socket bound to port", host, " ", port)

	# put the socket into listening mode
	s.listen(5)
	print("socket is listening")

	# a forever loop until client wants to exit
	while True:

		# establish connection with client
		c, addr = s.accept()

		# lock acquired by client
		print_lock.acquire()
		print('Connected to :', addr[0], ':', addr[1])

		# Start a new thread and return its identifier
		start_new_thread(threaded, (c,))
	s.close()

exitFlag = 0

class myThread (threading.Thread):
   def __init__(self, threadID, name, counter):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.counter = counter
   def run(self):
      print ("Starting " + self.name)
      print_time(self.name, 1000, self.counter)
      print ("Exiting " + self.name)

def print_time(threadName, counter, delay):
   while counter:
      if exitFlag:
         threadName.exit()
      time.sleep(delay)
      print ("%s: %s" % (threadName, time.ctime(time.time())))
      # counter -= 1  # turn off and exit when count is over

# Create new threads
thread1 = myThread(1, "Thread-1", 3)
#thread2 = threading.Thread(target=canStat, args=())
thread3 = threading.Thread(target=dmxset, args=())
 
# Start new Threads
thread1.start()
#thread2.start()
thread3.start()

print ("Exiting Main Thread")


if __name__ == '__main__':
        Main()

