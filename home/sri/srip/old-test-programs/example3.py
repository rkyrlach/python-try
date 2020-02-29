# import socket programming library
import socket

# import thread module
from _thread import *
import threading
import time

print_lock = threading.Lock()

# thread function
def threaded(c):
	while True:

		# data received from client
		data = c.recv(1024)
		if not data:
			print('Bye')

			# lock released on exit
			print_lock.release()
			break

		# reverse the given string from client
		data = data[::-1]

		# send back reversed string to client
		c.send(data)

	# connection closed
	c.close()


def Main():
	host = ""

	# reverse a port on your computer
	# in our case it is 12345 but it
	# can be anything
	port = 12345
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((host, port))
	print("socket bound to port", port)

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
thread1 = myThread(1, "Thread-1", 1)
thread2 = myThread(2, "Thread-2", 2)

# Start new Threads
thread1.start()
thread2.start()

print ("Exiting Main Thread")


if __name__ == '__main__':
        Main()

