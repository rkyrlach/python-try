

from multiprocessing import Process, Queue, Lock
import socket
import time
import os
import select
import sys

class SRV:
    """SRI ATRS Car Server Controller
    """
    q = Queue()

    def info(self):
        print('module name:', "SRI server ")
        print('parent process:', os.getppid())
        print('process id:', os.getpid())

    def serv(self, lck, q):
        #info('function serv')
        host = ""  ###  "10.249.1.3"
        port = 12345
        # Create a TCP/IP socket
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setblocking(0)
        server.bind((host, port))
        print("socket bound to port", host, " ", port)

        # put the socket into listening mode
        server.listen(5)
        print("socket is listening")
        # Sockets from which we expect to read
        inputs = [ server ]
        # Sockets to which we expect to write
        outputs = [ ]   ## server ?????????????????????????????
        # Outgoing message queues (socket:Queue)
        message_queues = {}
        while inputs:
            # Wait for at least one of the sockets to be ready for processing
            sys.stderr.write('\nwaiting for the next event ')
            readable, writable, exceptional = select.select(inputs, outputs, inputs)
            # Handle inputs
            for s in readable:
               if s is server:
                   # A "readable" server socket is ready to accept a connection
                   connection, client_address = s.accept()
                   sys.stderr.write('\nnew connection from ')  #, client_address[0], client_address[1])
                   connection.setblocking(0)
                   inputs.append(connection)
                   # Give the connection a queue for data we want to send
                   message_queues[connection] = Queue.Queue()
               else:
                   data = s.recv(1024)
                   if data:
                        # A readable client socket has data
                        sys.stderr.write('\nreceived "%s" from %s ' % (data, s.getpeername()))
                        message_queues[s].put(data)
                        # Add output channel for response
                        if s not in outputs:
                            outputs.append(s)
                   else:
                       # Interpret empty result as closed connection
                       sys.stderr.write('\nclosing ', client_address, ' after reading no data ')
                       # Stop listening for input on the connection
                       if s in outputs:
                            outputs.remove(s)
                       inputs.remove(s)
                       s.close()
                       # Remove message queue
                       del message_queues[s]
            # Handle outputs
            for s in writable:
                try:
                     next_msg = message_queues[s].get_nowait()
                except Queue.Empty:
                     # No messages waiting so stop checking for writability.
                     sys.stderr.write('\noutput queue for ', s.getpeername(), ' is empty ')
                     outputs.remove(s)
                else:
                     sys.stderr.write('\nsending "%s" to %s ' % (next_msg, s.getpeername()))
                     s.send(next_msg)
            # Handle "exceptional conditions"
            for s in exceptional:
                sys.stderr.write('\nhandling exceptional condition for ', s.getpeername())
                # Stop listening for input on the connection
                inputs.remove(s)
                if s in outputs:
                    outputs.remove(s)
                s.close()
                # Remove message queue
                del message_queues[s]


        # a forever loop until client wants to exit
        # establish connection with client
#        c, addr = server.accept()
#        print('Connected to :', addr[0], ':', addr[1])

#        while True:
            # data received from client
#            data = c.recv(1024)
#            if (len(data) <= 3): data = "i"
#            print ("data = ",data)
#            lck.acquire()
#            print("data[0] ",data[0])
#            if (q.qsize() != 0 ):
#                dmy = q.get()
#                print ("SRV q length = ", q.qsize(), dmy)
#            q.put(data)
#            lck.release()
#            if not data:
#               print('Bye')
#               break
            # reverse the given string from client
            # data = data[::-1]
#            c.send(data)
        # connection closed
#        c.close()

