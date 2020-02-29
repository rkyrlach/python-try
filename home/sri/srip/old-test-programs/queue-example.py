from multiprocessing import Process, Queue
import DMX
import SRV
import time
import os
import serial
import binascii
import array as arr

q =  Queue()
dmx = DMX.DMX()
dmx.init()
srv = SRV.SRV()
srv.info()

if __name__ == '__main__':

    srv_process = Process(target=srv.serv, args=(q,))
    srv_process.start()

    dmx_process = Process(target=dmx.dmx, args=(q,))
    dmx_process.start()

    while True:
       print("hi")
       time.sleep(1)

