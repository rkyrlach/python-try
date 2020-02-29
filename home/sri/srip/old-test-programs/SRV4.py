
from multiprocessing import Process, Queue
import socket
import time
import os

class SRV:
    """SRI ATRS Car Server Controller
    """
    q = Queue()

    def info(self):
#    print(title)
        print('module name:', "SRI server ")
        print('parent process:', os.getppid())
        print('process id:', os.getpid())

    def serv(self, q):
        #info('function serv')
        host = ""  ###  "10.249.1.3"
        port = 12345
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        print("socket bound to port", host, " ", port)

        # put the socket into listening mode
        s.listen(5)
        print("socket is listening")
        # a forever loop until client wants to exit
        # establish connection with client
        c, addr = s.accept()
        print('Connected to :', addr[0], ':', addr[1])
        s.setblocking(0)           ### blocking turned off
        while True:
                # data received from client
                data = ""
                data = c.recv(1024)
                print ("Data is ",data)
                if (data == b''): data = b'58'
                print ("data == ",data)
                q.put(data)
                if (data == b'58'):
                        print('Bye')
                        break
                # reverse the given string from client
                # data = data[::-1]
                c.send(data)
        # connection closed
        c.close()

