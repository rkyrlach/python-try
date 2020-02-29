


from multiprocessing import Process, Queue
import socket
import select
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
        s = socket.socket()
        host = ""  ###  "10.249.1.3"
        port = 12345
        s.bind((host, port))
        print("socket bound to port", host, " ", port)
        s.listen(1)
        print("socket is listening")
        readable = [s] # list of readable sockets.  s is readable if a client is waiting.

        # Testing non-blocking recv
        conn, addr = s.accept()
        #self.addCleanup(conn.close)
        conn.setblocking(0)


        while True:
            # r will be a list of sockets with readable data
            r,w,e = select.select(readable,[],[],0)
            for rs in r: # iterate through readable sockets
                if rs is s: # is it the server
                    c,a = s.accept()
                    print('\r{}:'.format(a),'connected')
                    readable.append(c) # add the client
                else:
                    # the server didn't send data yet: non-blocking recv() fails
                    with self.assertRaises(socket.error):
                        data = conn.recv(len(MSG))

                    self.event.set()

                    read, write, err = select.select([conn], [], [], MAIN_TIMEOUT)
                    if conn not in read:
                        self.fail("Error during select call to non-blocking socket.")

                    # the server sent data yet: non-blocking recv() doesn't block
                    data = conn.recv(len(MSG))
                    self.assertEqual(data, MSG)

                    print('length of data ',len(data))
                    if not data:
                        print('\r{}:'.format(rs.getpeername()),'disconnected')
                        readable.remove(rs)
                        rs.close()
                    else:
                        print('\r{}:'.format(rs.getpeername()),data)
                        rs.send(data)
                        q.put(data)




