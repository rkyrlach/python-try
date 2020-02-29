
import os
from multiprocessing import Process, Queue


if __name__ == '__main__':
    print("server starting ")
    q = Queue()
    p1 = Process(target="serv1.py")      ### , args="(q,)")
#    os.system('python3 {}'.format("serv1.py"))
    p1.start()
    print (" q ", q.get())
    p1.join()
    p2 = Process(target="dmx-serv.py")
    p2.start()
    p2.join()

