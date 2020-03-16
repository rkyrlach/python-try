
from multiprocessing import Process, Queue
import socket
from socket import error as SocketError
import errno
import select
import time
import subprocess
import os

class Server:
    """SRI ATRS Car Server Controller
    """

    def start(self, lq, mq, cq, qs):  # light q, motor q, all q, status q
        s = socket.socket()
        host = ""               ### "10.249.1.3" (private LAN)
        port = 12345            ### arbitrary port assignment (must match client port number)
        s.bind((host, port))
        print("socket bound to port", host, " ", port)
        s.listen(1)
        print("socket is listening")
        readable = [s] # list of readable sockets.  s is readable if a client is waiting.
        done = False
        while not done:
            # r will be a list of sockets with readable data
            r,w,e = select.select(readable,[],[],0)
            for rs in r:                    # iterate through readable sockets
                if rs is s:                 # is it the server
                    c,a = s.accept()
                    print('\r{}:'.format(a),'connected')
                    readable.append(c)      # add the client
                else:
                   print(' qs = ++++++++++++++ '. qs.get())
                   data = b'r'                  # old status command (may change) ************************
                   try:                         # try to read from client
                      data = rs.recv(1024)      # is there any new data from the client (a command?)
                   except SocketError as e:     # check for socket error
                      if (e.errno == errno.ECONNRESET):
                         subprocess.call(['systemctl start sri-server.service'], shell=True);        # rs.close();
                         raise ConnectionError(" Connection reset by Lane so restart the server ")   # error we are looking for
                      pass # Handle other errors here if needed
                   print('length of data ',len(data), " data[0] ",data[0])
                   if ((not data) or (data[0] == 120)):
                      print('\r{}:'.format(rs.getpeername()),'we have been disconnected ***** ')
                      readable.remove(rs)
                      rs.close()
                      done = True
                   else:
                      print('\r{}:'.format(rs.getpeername()),data)
                      rs.send(data)                                  # echo the received data back to the client
                      if (data[0] == 99):  lq.put(data)              # light commands go to q for lights.py
                      if (data[0] == 116): mq.put(data)              # motor target commands go to qm for motor.py
                      if (data[0] == 104): mq.put(data)              # motor home command
#                     cq.put(data)                                   # queue up what ever the command is
                      print('data put into queue = ', data, " integer command ID = ", data[0],
                             lq.empty(), mq.empty(), cq.empty(), qs.empty() )
                   try:
                      while (not qs.empty()):
                        vv = qs.get()
                        print( " ************** qs *********** ", vv)
                        rs.send(vv)
                   except SocketError as e:     # check for socket error
                      if (e.errno == errno.ECONNRESET):
                         subprocess.call(['systemctl start sri-server.service'], shell=True);        # rs.close();
                         raise ConnectionError(" Connection reset by Lane so restart the server ")   # error we are looking for
                      pass # Handle other errors here if needed
#

