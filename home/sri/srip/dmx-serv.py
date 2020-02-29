import os
from multiprocessing import Process, Queue
import serial
import binascii
import array as arr

ser = serial.Serial(port = "/dev/ttyS5", baudrate=250000, stopbits=2)

dmxbuf = arr.array('B', [0,0,0,0,0,0,0,0,0])
print ("dmxbuf = ", dmxbuf)

def dmx():
      global cfc
      global dmxbuf
#   while True:
#      dmx="".join( chr(x) for x in dmxbuf)
#      print ("command = ", cfc[0], cfc[1])
      if ((cfc[0] == "c") & (cfc[1] == "t")):
         st = cfc.find(',')                  # first comma
         nd = cfc.find(',' , st+1)           # second comma
         aa = int('{}'.format(cfc)[st+1:nd]) # first parameter
#         print("first parm = ", aa)
         st = nd                             # second comma
         nd = cfc.find(',' , st+1)           # third comma
         bb = int('{}'.format(cfc)[st+1:nd]) # second parameter
#         print("second  parm = ", bb)
         st = nd                             # third comma
         nd = cfc.find(',' , st+1)           # forth comma
         cc = int('{}'.format(cfc)[st+1:nd]) # third parameter
#         print("third  parm = ", cc)
         st = nd                             # forth comma
         nd = len(cfc)                       # end of string
         dd = int('{}'.format(cfc)[st+1:nd]) # third parameter
#         print("fourth  parm = ", dd)
         dmxbuf[0]=aa                        # target red
         dmxbuf[1]=bb                        # target green
         dmxbuf[2]=cc                        # target blue
         dmxbuf[3]=dd                        # target white

      if ((cfc[0] == "c") & (cfc[1] == "a")):
         st = cfc.find(',')                  # first comma
         nd = cfc.find(',' , st+1)           # second comma
         aa = int('{}'.format(cfc)[st+1:nd]) # first parameter
#         print("first parm = ", aa)
         st = nd                             # second comma
         nd = cfc.find(',' , st+1)           # third comma
         bb = int('{}'.format(cfc)[st+1:nd]) # second parameter
#         print("second  parm = ", bb)
         st = nd                             # third comma
         nd = cfc.find(',' , st+1)           # forth comma
         cc = int('{}'.format(cfc)[st+1:nd]) # third parameter
#         print("third  parm = ", cc)
         dd = 0
#         print("fourth  parm = ", dd)
         dmxbuf[5]=aa                        # accent red
         dmxbuf[6]=bb                        # accent green
         dmxbuf[7]=cc                        # accent blue
         dmxbuf[8]=dd
      ser.send_break()
      ser.write(dmxbuf)
#      time.sleep(1)


if __name__ == '__main__':
    print("dmx loaded ")
#    q = Queue()
#    p = Process(target="serv1.py, args=(q,)")
#    os.system('python3 {}'.format("serv1.py"))
#    p.start()
#    print (" q ", q.get())
#    p.join()

while True:
    print("enter command ")
    q.get()
#    cfc = input()
    if (cfc.find('x') != -1): break
    dmx()


