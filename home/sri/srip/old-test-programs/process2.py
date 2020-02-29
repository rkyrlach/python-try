#import ray
from multiprocessing import Pool
import multiprocessing as mp
#from multiprocessing import Process
import socket
import time
import os

def test():
        info('function test')
#        rfk.put('hello RFK')
        while True:
          time.sleep(1)
          print ("%s" % (time.ctime(time.time())))

def info(title):
    print(title)
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', os.getpid())

def serv():
        info('function serv')
        # print("process name = ",name)
#        name.put('hello SRI')
        host = ""  ###  "10.249.1.3"
        # reverse a port on your computer
        # in our case it is 12345 but it
        # can be anything
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

        # lock acquired by client
        #print_lock.acquire()
        print('Connected to :', addr[0], ':', addr[1])

        while True:
                # Start a new thread and return its identifier
                # start_new_thread(threaded, (c,))

                # data received from client
                data = c.recv(1024)
                print ("data ",data)
                if not data:
                        print('Bye')

                        # lock released on exit
                        #print_lock.release()
                        break

                # reverse the given string from client
                # data = data[::-1]

                # send back reversed string to client
                c.send(data)

        # connection closed
        c.close()

#        s.close()
if __name__ == '__main__':
#    info('main line')
#    p = Process(target=serv, args=('server',))
#    p.start()
#    p.join()

    def main():
      pool = Pool(processes=2)
      parsed = pool(serv)
      pattern = pool(test)
      pool.close()
      pool.join()

#    final = FinalProcess(parsed.get(), pattern.get(), calc_res.get())




#    mp.set_start_method('spawn')
#    q = mp.Queue()
#    info('main line')

#    p = mp.Process(target=serv, args=(q,))
#    p.start()
#    print(q.get())
#    p.join()

#    p = mp.Process(target=test, args=(q,))
#    p.start()
#    print(q.get())
#    p.join()

