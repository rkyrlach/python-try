
from multiprocessing import Process, Queue, Lock
import DMX
import SRV
import MTR
import threading, time
import os
import serial
import binascii
import array as arr

q  = Queue()
qm = Queue()

dmx = DMX.DMX()
dmx.init()
srv = SRV.SRV()
srv.info()
mtr = MTR.MTR()

if __name__ == '__main__':

    # lock = Lock()
    srv_process = Process(target=srv.serv, args=( q, qm))
    srv_process.start()

    dmx_process = Process(target=dmx.dmx, args=( q,))
    dmx_process.start()

    mtr_process = Process(target=mtr.mtr, args=( qm,))
    mtr_process.start()

    print('server, motor-controller and dmx driver started ')
    while True:
       dmx.dmx(q,)
       mtr.mtr(qm,)
       print(" q = ",q," qm = ", qm)
       time.sleep(10.2)
       #print("hi --------------------------------------------------------")
       #timer = threading.Timer(3, dmx.dmx( q,))
       #time.sleep(7)

