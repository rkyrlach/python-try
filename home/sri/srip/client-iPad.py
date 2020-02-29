
#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  peertalk.py
#
# Copyright (C) 2012    David House <davidahouse@gmail.com> Russell Gries
# **  edited to except and extract data from peertalk simple ( a new version of the X code project using swift) then wright to a file called fromIpad.txt
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 or version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
#
# This script depends on the usbmux python script that you can find here:
# http://code.google.com/p/iphone-dataprotection/source/browse/usbmuxd-python-client/?r=3e6e6f047d7314e41dcc143ad52c67d3ee8c0859
# Also only works with the PeerTalk iOS application that you can find here:
# https://github.com/rsms/peertalk
#

import usbmux
import socket                              #SocketServer
from socket import error as SocketError
import errno
import sys
import select
from optparse import OptionParser
from multiprocessing import Process, Queue
import threading
import struct
import subprocess
import os

subprocess.call(["echo HI Richard > /root/msg.txt"], shell=True)
q = Queue()

class PeerTalkThread(threading.Thread):

    def __init__(self, *args):
        self._psock = args[0]
        self._running = True
        threading.Thread.__init__(self)

    def run(self):
        framestructure = struct.Struct('! I I I I')
        while self._running:
            try:
                msg = self._psock.recv(16)
                if len(msg) > 0:
                    frame = framestructure.unpack(msg)
                    size = frame[3]
                    msgdata = self._psock.recv(size)
                    ### print ('Received from ipad: {}'.format(msgdata))
                    fullData = '{}'.format(msgdata)
                    startEXT = fullData.find('$$$$')              # # find start position of $$$$
                    endEXT = fullData.find('$$$$', startEXT + 5)  # # find Stop Position of $$$$
                    extmsgdata = '{}'.format(fullData)[startEXT
                        + 6:endEXT - 2]                           # # Extract bytes between $$$$ and $$$$
                    print (' external message = ', extmsgdata)
                    if extmsgdata.find("StartClient") != -1:
                        print (' --- we detected start client --- ')
                        ### os.system('nohup /root/development/cpp11/Ice/SRI/client &')
                        ### subprocess.Popen("nohup /root/development/cpp11/Ice/SRI/client>/dev/null 2>&1 &", shell=True)
                        subprocess.call("systemctl start sri-client.service", shell=True)
                    else:
                        dataToFile = 'echo ' + extmsgdata \
                            + ' >> /home/sri/srip/fromIpad.txt'                   # # chose where to write the data
                        subprocess.call([dataToFile], shell=True)                 # # send text to fromIpad.txt file
                        s.send(extmsgdata.encode('utf-8'))
                        ### subprocess.call([extmsgdata], shell=True)             # # send the command to command line
            except:
                pass

    def stop(self):
        self._running = False

#    def main(self, q,):

print ('peertalk starting')
mux = usbmux.USBMux()
status = mux.process(1.0)
print ('usbmux status = ', status)
#print (status)

print (mux.devices)
print ('Waiting for devices...')
if not mux.devices:
	mux.process(1.0)
if not mux.devices:
	print ('No device found')

dev = mux.devices[0]
print ('connecting to device %s' % str(dev))
print (dev )    ### <MuxDevice: ID 1 ProdID 0x12ab Serial '17506777147e51f79c10a61d7b3b5ed70147f388' Location 0x10002>
psock = mux.connect(dev, 2345)
psock.setblocking(0)
psock.settimeout(2)

#subprocess.call(['systemctl stop sri-connect.timer'], shell=True)
#subprocess.call(['systemctl start sri-running.timer'], shell=True)

ptthread = PeerTalkThread(psock)
ptthread.start()
print (" --------  Starting client now ----------- ")
### subprocess.call("/etc/sri/start_client1.sh", shell=True)

host = '10.249.1.3'
# Define the port on which you want to connect
port = 12345
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# connect to server on local computer
try:
   s.connect((host,port))
except SocketError as e:
   if e.errno == errno.ECONNREFUSED:
      subprocess.call(['/bin/bash /etc/sri/look-iPad.sh'], shell=True);     # rs.close();
      # add a script to kill the iPad connection and retry the connection to the server again
      raise ConnectionError(" Connection to server refused ")               # error we are looking for
   pass # Handle other errors here if needed
#        while True:
	# message sent to server
#            print("enter a command: (eg t,600 or t,-600)" )
#            command = input()
#            s.send(command.encode('utf-8'))
	# messaga received from server
#            data = s.recv(1024)
	# print the received message
#            print('Received from the server :',str(data.decode('utf-8')))
	# ask the client whether he wants to continue
#            ans = input('\nDo you want to continue(y/n) :')
#            if ans == 'y':
#                continue
#            else:
#                break
# close the connectio
#s.close()

print ('type quit to exit!')

done = False

while not done:
    if os.path.isfile('/home/sri/srip/toIpad.txt'):
        f = open('/home/sri/srip/toIpad.txt', 'r')
        for x in f:
            print (x)
            cmd = x
            if cmd[0:3] == 'quit':
                done = True
            else:
                r8 = cmd.encode('ascii')
                headervalues = (1, 101, 0, len(r8) + 4)
                framestructure = struct.Struct('! I I I I'.encode('ascii'))
                packed_data = framestructure.pack(*headervalues)
                try:
                   # read from a client
                   psock.send(packed_data)
                except SocketError as e:
                   if (e.errno == errno.EPIPE) or (e.errno == errno.ESHUTDOWN):
                      subprocess.call(['/bin/bash /etc/sri/look-iPad.sh'], shell=True);    # rs.close();
                      raise ConnectionError(" Connection to iPad broken ")                 # error we are looking for
                   pass # Handle other errors here if needed
                messagevalues = (len(r8), r8)
                fmtstring = '! I {0}s'.format(len(r8))
                sm = struct.Struct(fmtstring)
                packed_message = sm.pack(*messagevalues)
                try:
                   # read from a client
                   psock.send(packed_message)
                except SocketError as e:
                   if (e.errno == errno.EPIPE) or (e.errno == errno.ESHUTDOWN):
                      subprocess.call(['/bin/bash /etc/sri/look-iPad.sh'], shell=True);    # rs.close();
                      raise ConnectionError(" Connection to iPad broken ")                 # error we are looking for
                   pass # Handle other errors here if needed
        f.close()
        os.remove('/home/sri/srip/toIpad.txt')
remove('/home/sri/srip/toIpad.txt')
ptthread.stop()
ptthread.join()
psock.close()

s.close()

#if __name__ == '__main__':
#main()

