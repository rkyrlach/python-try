
from multiprocessing import Process, Queue
import array as arr
import serial
import time

class DMX:
    """DMX Controller
    """
    global dmxbuf
    global ser
    dmxbuf = arr.array('B', [0,0,0,0,0,0,0,0,0])
    ser = serial.Serial(port = "/dev/ttyS5", baudrate=250000, stopbits=2)
    q = Queue()

    def init(self):
       global dmxbuf
       ser.send_break()
       ser.write(dmxbuf)

    def dmx(self, q):
      global dmxbuf
      global ser
      while True:
        cfc = None
        cfc = q.get()
        dmy = cfc
        if (cfc == b'r'):
#            ser.send_break()
#            ser.write(dmxbuf)
            break

#        print("cfc in DMX = ",cfc," -1- ",cfc[0],cfc[1],cfc[2],cfc[3],cfc[4],cfc[5],cfc[6],cfc[7],cfc[8])
        cfc="".join( chr(x) for x in cfc)
        print('joined cfc = ',cfc)
        if ((cfc[0] == 'c') & (cfc[1] == 't')):
#          print("cfc= ",cfc," -ct- ",cfc[0],cfc[1],cfc[2],cfc[3],cfc[4],cfc[5])
          st = cfc.find(',')                  # first comma
          nd = cfc.find(',' , st+1)           # second comma
          aa = int('{}'.format(cfc)[st+1:nd]) # first parameter
#          print("first parm = ", aa)
          st = nd                             # second comma
          nd = cfc.find(',' , st+1)           # third comma
          bb = int('{}'.format(cfc)[st+1:nd]) # second parameter
#          print("second  parm = ", bb)
          st = nd                             # third comma
          nd = cfc.find(',' , st+1)           # forth comma
          cc = int('{}'.format(cfc)[st+1:nd]) # third parameter
#          print("third  parm = ", cc)
          st = nd                             # forth comma
          nd = cfc.find(',' , st+1)           # fifth comma or end of string
          if (nd == -1): nd = len(cfc)
          dd = int('{}'.format(cfc)[st+1:nd]) # third parameter
#          print("fourth  parm = ", dd)
          dmxbuf[1]=aa                        # target red
          dmxbuf[2]=bb                        # target green
          dmxbuf[3]=cc                        # target blue
          dmxbuf[4]=dd                        # target white
          ser.send_break()
          ser.write(dmxbuf)
          break

        if ((cfc[0] == 'c') & (cfc[1] == 'a')):
#          print("cfc= ",cfc," -ca- ",cfc[0],cfc[1],cfc[2],cfc[3],cfc[4],cfc[5])
          st = cfc.find(',')                  # first comma
          nd = cfc.find(',' , st+1)           # second comma
          aa = int('{}'.format(cfc)[st+1:nd]) # first parameter
#          print("first parm = ", aa)
          st = nd                             # second comma
          nd = cfc.find(',' , st+1)           # third comma
          bb = int('{}'.format(cfc)[st+1:nd]) # second parameter
#          print("second  parm = ", bb)
          st = nd                             # third comma
          nd = cfc.find(',' , st+1)           # forth comma
          cc = int('{}'.format(cfc)[st+1:nd]) # third parameter
#          print("third  parm = ", cc)
          dd = 0
#          print("fourth  parm = ", dd)
          dmxbuf[5]=aa                        # accent red
          dmxbuf[6]=bb                        # accent green
          dmxbuf[7]=cc                        # accent blue
          dmxbuf[8]=dd
          ser.send_break()
          ser.write(dmxbuf)
          break

