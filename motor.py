#!/usr/bin/python3
from multiprocessing import Process, Value
import threading, time
import can
from can import Message
from time import time, sleep
from datetime import datetime, timedelta
import PID                                   # PID routines
import MOT                                   # same as a config file

""" SRI ATRS Car Motor Controller
    #       open a can bus socket.... close it after move

    #       // Convert tacho into inches
    #       // wheel diameter = 59mm = 2.322835 inches
    #       // wheel circumference = 7.2974 inches
    #       // 1 tacho is 1/42nd of a revolution or 0.17375 inches

    # the VESC updates his status 50 times per second 1/50 = 0.020 milliseconds
    # at full speed the car moves almost 12 inches (67 tachos) in that amount of time
"""

class Motor:
  global bus
  #bus = can.interface.Bus('can0', bustype='socketcan_native')
  bus = can.interface.Bus(channel='can0', bustype='socketcan', fd=True)

  def startController(self, qm):
    global bus
    target = 't,1200'
    run_process = Process(target=self.start, args=(target, ))
    run_process.start()
    done = False
    while (not done):
      while (not qm.empty()):
        m = qm.get()
        m="".join( chr(x) for x in m)
#        print(" target received inside motor controller = ",m)
        if m == "quit":
          target = 'x'
          done = True
        else:
          pos = m.find(',')
          num = '{}'.format(m)[pos + 1: len(m)]
          print("target received inside motor controller = ",m,num)
          target = m                                 ###float(num)

#  def start(self, speed):
#    done = False
#    while (not done):
#      time.sleep(1)
#      if speed.value < 0:
#        done = True
#      else:
#        print("Motor is now at speed: " + str(speed.value))

  def lock(self):     #keeps can alive and motor stopped
    global bus
    packet = Message(arbitration_id=1, data=[0, 0, 0, 0])
    bus.send(packet)
    packet = Message(arbitration_id=2, data=[0, 0, 0, 0])
    bus.send(packet)

  def clr_buf(self):
    cnt = 0
    while (cnt <= 100):
      cs = Motor.tacho_get(self)
      cnt = cnt + 1

  def tacho_get(self):
  #   this routine reads the vesc can buss and extracts the current status for use by the program
  #   VESC status messages 2305: 3585: 3841: 4097: 6913:
  #   now = datetime.now()
  #   print(now.strftime("%H:%M:%S.%f"))
    global bus
    num = 0;   m1 = False;   m2 = False;   m3 = False;   m4 = False;   m5 = False
    while ((m1 and m2 and m3 and m4 and m5) == False):
      message0 = bus.recv();  num = int(message0.arbitration_id)
      if (num == 2305):                                # message1
         a=message0.data[0]; b=message0.data[1]; c=message0.data[2]; d=message0.data[3]
         e=message0.data[4]; f=message0.data[5]; g=message0.data[6]; h=message0.data[7]
         rpm = (d + (c*256) + (b*65536) + (a*16777216))
         if (a>=128): rpm = rpm-4294967296             # extract the RPM
         current = float(f + (e*256))                  # extract the supply current
         if (e>=128): current = current-65536
         duty = (h + (g*256))                          # extract the duty cycle
         if (g>=128): duty = duty-65536
         m1 = True
      if (num == 3585):                                # message2
         a=message0.data[0]; b=message0.data[1]; c=message0.data[2]; d=message0.data[3]
         e=message0.data[4]; f=message0.data[5]; g=message0.data[6]; h=message0.data[7]
         m2 = True
      if (num == 3841):                                # message3
         a=message0.data[0]; b=message0.data[1]; c=message0.data[2]; d=message0.data[3]
         e=message0.data[4]; f=message0.data[5]; g=message0.data[6]; h=message0.data[7]
         m3 = True
      if (num == 4097):                                # message4
         a=message0.data[0]; b=message0.data[1]; c=message0.data[2]; d=message0.data[3]
         e=message0.data[4]; f=message0.data[5]; g=message0.data[6]; h=message0.data[7]
         Imot = float(f + (e*256))/10.0                # extract the motor current
         if (e>=128): Imot = Imot-6553.6
         m4 = True
      if (num == 6913):                                # message5
         a=message0.data[0]; b=message0.data[1]; c=message0.data[2]; d=message0.data[3]
         e=message0.data[4]; f=message0.data[5]; g=message0.data[6]; h=message0.data[7]
         tacho = (d + (c*256) + (b*65536) + (a*16777216))
         if (a>=128): tacho = tacho-4294967296          # extract the tacho position
         vin = (f + (e*256))/10.0                       # extract the supply voltage
         m5 = True
    canstat = [int(tacho), float(vin), float(rpm), float(Imot), float(duty)]
    # now = datetime.now()
    # now.microsecond
    # print(now.strftime("%H:%M:%S.%f"))
    return canstat

  def erpm_tab(self, nn, mm):
    mn = 255-mm
    # global min
    #   this table is the heart of the motion planner. These vectors are good for all 4 tiers (I hope)
    #   It consists of 6 vectors as follows:
    #               vector[0] = cumulative distance steps while accelerating
    #               0   1   2    3    4    5    6     7     8     9     10   11   12   13   14   15   16   17   18
    distUp =     [  0,  40,  80, 120, 160, 200, 240,  280,  320,  360,  400, 440, 480, 520, 560, 600, 640, 680, 720,
    #               19   20   21   22   23   24   25    26    27    28    29
                    760, 800, 840, 880, 920, 960, 1000, 1040, 1080, 1120, 1160]
    #               vector[1] = cumulative distance steps while slowing down
    #               0   1    2    3    4    5    6    7    8    9   10   11   12   13   14   15   16   17    18
    distDown =   [  0, 61,  122, 183, 244, 305, 366, 427, 488, 549, 610, 671, 732, 793, 854, 915, 976, 1037, 1098,
    #               19    20    21    22    23    24    25    26    27    28    29
                    1159, 1220, 1281, 1342, 1403, 1464, 1505, 1546, 1587, 1628, 1638]
    #               vector[2] = vesc commands for a positive move while accelerating
    #               0   1   2    3    4    5    6     7     8     9     10   11   12   13   14   15   16   17   18
    #accelPlus = [  0,  50,  55,  60,  65,  70,  75,  80,   85,   90,   95,  100, 105, 110, 115, 120, 125, 130, 135,
    accelPlus  = [  0,  40,  42,  45,  49,  53,  58,  63,   68,   73,   79,  85,  91,  97,  104, 111, 118, 125, 132,
    #               19   20   21   22   23   24   25    26    27    28    29
    #               140, 145, 150, 155, 160, 165, 170,  175,  180,  185,  190
                    138, 144, 150, 155, 160, 165, 170,  175,  180,  185,  190]
    #               vector[3] = vesc commands for a positive move while slowing down
    #               0   1   2    3    4    5    6     7     8     9     10   11   12    13    14   15   16   17   18
    slowPlus   = [  0, 184, 178, 172, 166, 160, 154,  148,  142,  135,  129, 123, 117, 111,  105,  99,  93,  87,  81,
    #               19   20   21   22   23   24   25   26      27     28     29
                    75,  69,  63,  57,  50,  44,  38,  mm+24,  mm+16, mm+8,  mm]
    #               vector[4] = vesc commands for a negative move while accelerating
    #               0    1    2    3    4    5    6    7     8     9     10   11   12   13   14   15   16   17   18
    #accelMinus= [  255, 205, 200, 195, 190, 185, 180, 175,  170,  165,  160, 155, 150, 145, 140, 135, 130, 125, 120,
    accelMinus = [  255, 215, 213, 210, 206, 202, 197, 192,  187,  182,  176, 170, 164, 158, 151, 144, 137, 130, 123,
    #               19   20   21   22   23   24   25   26    27    28    29
    #               115, 110, 105, 100, 95,  90,  85,  80,   75,   70,   65]
                    117, 111, 105, 100, 95,  90,  85,  80,   75,   70,   65]
    #               vector[5] = vesc commands for a negative move while slowing down
    #               0    1    2    3    4    5    6     7     8     9     10   11   12   13   14   15   16   17   18
    slowMinus  = [  255, 71,  77,  83,  89,  95,  101,  107,  113,  120,  126, 132, 138, 144, 150, 156, 162, 168, 174,
    #               19   20   21   22   23   24   25    26       27       28      29
                    180, 186, 192, 198, 205, 211, 217,   mn-24,   mn-16,   mn-8,   mn]
    #   end of vectors. call to this routine returns current value for all 6 vectors in an array
    val = [int(distUp[nn]), int(distDown[nn]), int(accelPlus[nn]), int(slowPlus[nn]), int(accelMinus[nn]), int(slowMinus[nn]) ]
    #   print("seek up = ", val[0], " seek dn = ", val[1], " posU = ", val[2]," posDn = ", val[3], " negUp = ", val[4], " negDn = ", val[5])
    return val


  def plan(self, move, tier, min, dir): # call with the distance you want to move in tachos
                                        # no moves lees than 5 ft and subtract 1 foot for creep to position
    rvesc = [0]; rdist = [0]        # start with "clean" temporary vectors (ie it's a new move)
    if (move <= 442):               # 442 = 6.4 feet, motion planner rejects any call below 6.4' and returns -1
      rvesc = [ -1 ]; rdist = [ -1 ]
      rv = [ rdist, rvesc ]
      return rv                    # return error code of -1
    movesv = 0
    if (tier == 1):
        maxI = 5       # set tier 1
        if (move >= 3798): movesv = 100  # >55 feet subtract
        else:
          if (move >= 3453): movesv = 100  # >50 feet subtract
          else:
            if (move >= 3108): movesv = 100  # >45 feet subtract
            else:
              if (move >= 2762): movesv = 100  # >40 feet subtract
              else:
                if (move >= 2417): movesv = 100  # >35 feet subtract
                else:
                  if (move >= 2072): movesv = 100  # >30 foot subtract
                  else:
                    if (move >= 1726): movesv = 100  # >25 feet subtract
                    else:
                      if (move >= 1380): movesv = 100  # >20 feet subtract
                      else:
                        if (move >= 1034): movesv = 100  # >15 feet subtract
                        else:
                          if (move >= 688): movesv = 90    # >10 feet subtract
                          else:
                            if (move >= 346): movesv = 80    # >5 feet subtract
                            else: movesv = 0
    if (tier == 2):
        maxI = 13      # set tier 2
        if (move >= 3798): movesv = 165  # >55 feet subtract
        else:
          if (move >= 3453): movesv = 165  # >50 feet subtract
          else:
            if (move >= 3108): movesv = 165  # >45 feet subtract
            else:
              if (move >= 2762): movesv = 160  # >40 feet subtract
              else:
                if (move >= 2417): movesv = 155  # >35 feet subtract
                else:
                  if (move >= 2072): movesv = 150  # >30 foot subtract
                  else:
                    if (move >= 1726): movesv = 150  # >25 feet subtract
                    else:
                      if (move >= 1380): movesv = 120  # >20 feet subtract
                      else:
                        if (move >= 1034): movesv = 100   # >15 feet subtract
                        else:
                          if (move >= 688): movesv = 90    # >10 feet subtract
                          else:
                            if (move >= 346): movesv = 80    # >5 feet subtract
                            else: movesv = 0
    if (tier == 3):
        maxI = 21      # set tier 3
        if (move >= 3798): movesv = 220  # >55 feet subtract
        else:
          if (move >= 3453): movesv = 210  # >50 feet subtract
          else:
            if (move >= 3108): movesv = 200  # >45 feet subtract
            else:
              if (move >= 2762): movesv = 190  # >40 feet subtract
              else:
                if (move >= 2417): movesv = 180  # >35 feet subtract
                else:
                  if (move >= 2072): movesv = 170  # >30 foot subtract
                  else:
                    if (move >= 1726): movesv = 140  # >25 feet subtract
                    else:
                      if (move >= 1380): movesv = 120  # >20 feet subtract
                      else:
                        if (move >= 1034): movesv = 100   # >15 feet subtract
                        else:
                          if (move >= 688): movesv = 90    # >10 feet subtract
                          else:
                            if (move >= 346): movesv = 80    # >5 feet subtract
                            else: movesv = 0
    if (tier == 4):
        maxI = 29      # set tier 4  (max)
        if (move >= 3798): movesv = 480  # >55 feet subtract
        else:
          if (move >= 3453): movesv = 400  # >50 feet subtract
          else:
            if (move >= 3108): movesv = 350  # >45 feet subtract
            else:
              if (move >= 2762): movesv = 270  # >40 feet subtract
              else:
                if (move >= 2417): movesv = 220  # >35 feet subtract
                else:
                  if (move >= 2072): movesv = 170  # >30 foot subtract
                  else:
                    if (move >= 1726): movesv = 140  # >25 feet subtract
                    else:
                      if (move >= 1380): movesv = 120  # >20 feet subtract
                      else:
                        if (move >= 1034): movesv = 100   # >15 feet subtract
                        else:
                          if (move >= 688): movesv = 90    # >10 feet subtract
                          else:
                            if (move >= 346): movesv = 80    # >5 feet subtract
                            else: movesv = 0
    move = move - movesv
    print("actual commanded move after subtraction of cushion = ", move)
    ck = Motor.erpm_tab(self, maxI, min)        # get highest distance for this tier
    dUp = ck[0]; dDn = ck[1]
    chop = True                     # if we need to move less than this then we must chop the pyramid
    if (move >= (dUp + dDn)):       # no chop needed if we are greater than the tier MAX accel and slow distances combined
      cntLimit = maxI; chop = False            # build temporary vector specific for this move
      cnt = 1                                  # start with the vesc acceleration vectors v[2] and v[4]
      while (not chop and (cnt <= cntLimit)):  # loop through the vectors defined in erpm_tab and get the
        nxt = Motor.erpm_tab(self, cnt, min)
        rdist.append(nxt[0])                   # next target distance added to our temp vector
        if (dir): rvesc.append(nxt[2])         # next vesc positive accel command added to our temp vector
        else: rvesc.append(nxt[4])             # next vesc negative accel command adde
        cnt += 1
      cntsv = cnt-1
      nxt = Motor.erpm_tab(self, cnt-1, min)
      middle = move - (dUp + dDn)              # compute how long we need to travel at tier MAX
      print(" d up ", dUp, " d dn ", dDn, "actual commanded move", move, " middle ", middle, " count ",cntsv)
      if (dir): rvesc.append(nxt[2])           # put the tier MAX vesc speed into our temp vector
      else: rvesc.append(nxt[4])
      dist_sv = nxt[0] + middle
      rdist.append(dist_sv)                    # put this distanc into our temp vector
      cnt = cntLimit
#     if (tier == 4): cnt = 1
#     else: cnt = 29 - maxI                    #########################################################################
      while (not chop and (cnt >= 1)):               # now do the slowing portion of the vector v[3] and v[5]
        nxt = Motor.erpm_tab(self, 30-cnt, min)
        if (dir): rvesc.append(nxt[3])           # next vesc positive slow command added to our temporary vector
        else: rvesc.append(nxt[5])               # next vesc negative slow command added
#       print("full move cnt, rvesc vector ", cnt, rvesc)
        cnt -= 1
      cnt = 1
      while (not chop and cnt <= cntLimit):           # while (chop and (cnt <= cntsv-2)):
        nxt = Motor.erpm_tab(self, cnt, min)
        rdist.append(nxt[1] + dist_sv)            # put target "slow" distance into our temp vector
        cnt += 1
    else:                                      # chop needed if we are moving less then the tier MAX accel and slow distances combined
      cnt = maxI
      while (move <= (dUp + dDn) and cnt >= 1):   # calculate how much we need to "chop"
        ck = Motor.erpm_tab(self, cnt, min)                   # get next highest distance for this tier
        dUp = ck[0]; dDn = ck[1]
        print(" chopped move, index, dUp, dDn  ", move, cnt, dUp, dDn)
        cnt -= 1
        cntLimit = cnt + 1
      cnt = 1
      rvesc = [0]; rdist = [0]                    # start "chopped" by clearing the temporary vectors (new move)
      print(" chopped move count limit = ", move, cntLimit, dUp, dDn)
      while (chop and cnt <= cntLimit):        # loop through the vectors defined in erpm_tab and get the
        nxt = Motor.erpm_tab(self, cnt, min)
        rdist.append(nxt[0])                   # next target distance added to our temp vector
        if (dir): rvesc.append(nxt[2])         # next vesc positive accel command added to our temp vector
        else: rvesc.append(nxt[4])             # next vesc negative accel command added
        cnt += 1
      nxt = Motor.erpm_tab(self, cnt-1, min)
      middle = move - (dUp + dDn)              # compute how long we need to travel at our current tier speed
      print(" d up, d dn, chopped move, middle ",dUp,dDn,move,middle)
      if (dir): rvesc.append(nxt[2])           # put the tier MAX vesc speed into our temp vector
      else: rvesc.append(nxt[4])
      dist_sv = nxt[0] + middle
      rdist.append(dist_sv)                      # put this distanc into our temp vector
      cnt = cntLimit                             # get the low end of the curve not the high end
      while (chop and (cnt >= 1)):               # now do the slowing portion of the vector v[3] and v[5]
        nxt = Motor.erpm_tab(self, 30-cnt, min)
        if (dir): rvesc.append(nxt[3])           # next vesc positive slow command added to our temporary vector
        else: rvesc.append(nxt[5])               # next vesc negative slow command added
#       print("chopped move cnt, rvesc vector ", cnt, rvesc)
        cnt -= 1
      cnt = 1
      while (chop and cnt <= cntLimit):           # while (chop and (cnt <= cntsv-2)):
        nxt = Motor.erpm_tab(self, cnt, min)
        rdist.append(nxt[1] + dist_sv)            # put target "slow" distance into our temp vector
#       print("chopped move cnt, rdist vector ", cnt, rdist)
        cnt += 1
    rv = ( rdist, rvesc )
    return rv

  """  ----------------------------------------------------------------------------------- """
  """  ----------------------------------------------------------------------------------- """

  def start(self, target):
    global forward
    done = False
    targetsv = target
#    target=b"r"
#    Motor.lock(self)
    while (not done):
        cnt = 0
#        print("enter motor command: (eg t,600 or t,-600)" )
#        command = input()                                  # string = str(input())
#        while not qm.empty():
#          command = qm.get()
#        command="".join( chr(x) for x in command)
        if (target[0] == 'r'): return()
#        if (target == 't,0'): done = True; return()
        Motor.lock(self)
        mot = MOT.MOT()
        av = mot.motInit()                                 # import the PID values, tier,  and other parameters
        P=av[0]; I=av[1]; D=av[2]; min=av[3]; max=av[4]; dz=av[5]; tier=av[6]
#       now = datetime.now()
#       print(now.strftime("%H:%M:%S.%f"))
        p=target.find(",")                       # find the start of the desired position
        dd='{}'.format(target)[p+1:len(target)] # dd has the value in tenths of inches that we want to move
        dd=round((float(dd)/10.0)*5.755)          # dd now has the number of tachos we need to move
        if (dd > 0): forward = True
        else: forward = False                     # are we going forward or back towards home
        dds = dd; dd = abs(dd)
        #set_vesc(1)
        ss = Motor.plan(self, dd, tier, min, forward)
        rdist = ss[0]
        rvesc = ss[1]
        print("Target = ", target, " distance ", dds, " tier ", tier, " direction ", forward)
        print("distance vector ",rdist)
        print("VESC vector is ",rvesc)
#        done = True
#        target = "t,0"
#        return
        pid = PID.PID(P, I, D)
        pid.setSampleTime(0.019999)
        mso = time(); t = 0; sci = 0
        Motor.clr_buf(self)
#       W
        Motor.lock(self)
        tot_moved = 0; delta_moved = 0; cs = Motor.tacho_get(self); posAE = cs[0]+dds   # get our current position
        posAS = cs[0];  pid_only = False; dda = abs(dds); pos = posAS; cnt=1  # position at start of move is now in posAS
        print ("pos at start ", posAS," distance to move ", dds, " pos at end ", posAE)
        now = datetime.now()
        print(now.strftime(" starting run %H:%M:%S.%f"))
        while (cnt <= len(rdist)-1):                           # 0-29 = 30 counts
          mv = rdist[cnt]
          print(" next point = ", mv)
          if (forward): seek =  posAS + mv                     # get next target tacho value
          else: seek = posAS - mv
#         posAS = seek
          print("next pair, index, & position ", rdist[cnt], rvesc[cnt], cnt, pos)
          while (forward and pos <= seek) or ((not forward) and pos >= seek):       # 200 times 0.005 seconds = 1 second run
            pos_sav = pos; cs = Motor.tacho_get(self);  pos = cs[0]                           #    print("can status: ",cs)
            delta_moved = pos - pos_sav; tot_moved = tot_moved + delta_moved
            vi = cs[1]; sp = cs[2]; cu = cs[3]; du = cs[4]
            ms = time(); sci = ms - mso;                                            # print("uSec = ", sci)
            sci = sci - int(sci); t = t + round(sci * 1000000); t1 = float(t/1000000)
            mso = ms; sci=0.0
            print("Tacho =, ", pos, " ,delta =, ", delta_moved, " ,eT =, %.4f" % t1, " ,eRPM =, ", sp, " ,Duty =, ", du,
                  " ,Vin =, ", vi, " ,Imot =, %.2f" % cu,  " ,Moved =, ", tot_moved, )
#           break
            if (forward):  # forward
              packet = Message(arbitration_id=1, data=[0, 0, rvesc[cnt], 0])   # motor 1
              bus.send(packet)
              packet = Message(arbitration_id=2, data=[0, 0, rvesc[cnt], 0])   # motor 2
              bus.send(packet)
            else:          # backwards
              packet = Message(arbitration_id=1, data=[255, 255, rvesc[cnt], 255])   # motor 1
              bus.send(packet)
              packet = Message(arbitration_id=2, data=[255, 255, rvesc[cnt], 255])   # motor 2
              bus.send(packet)
          cnt += 1
          now = datetime.now()
          print(now.strftime(" should be end of segment %H:%M:%S.%f"))

#          if (forward and sp <= 1500 and cnt >= (len(rvesc)/2)): break              # if we are moving slowly, then kick in PID
#          if ( not forward and sp >= -1500 and cnt >= (len(rvesc)/2)): break

### --- move is over so enable pid ( will home in to target position and then hold us there )
        else:
          print("start PID loop here -------------- ",target, targetsv)
          cs = Motor.tacho_get(self)
          dest = posAE - posAS             # destination is the position at start + or minus the size of the move
          nowT = cs[0] - posAS
          pid.clear                        # clear all the PID parameters to a fresh start
          pid.SetPoint = int(dest)         # set PID to desired relative distance that we saved
          pid.update(nowT)                 # feed PID our current relative position
#         scale = min / pid.output         # use first PID output value & create scale control vesc based on min vesc command value
          pid_out = pid.output
          scale = min/1000
          pid_out = abs(int(pid_out * scale))   # creat the vesc command value from the PID output
          if (pid_out >= max): pid_out = max
          if (pid_out <= min): pid_out = min
          print ("PID destination ", dest, " PID output = ", pid_out)
          while (target == targetsv):
#           break
#           try:
            if (forward):
              while ( cs[0]-posAS <= dest - dz):
                pos_sav = pos; cs = Motor.tacho_get(self);  pos = cs[0]                           #    print("can status: ",cs)
                delta_moved = pos - pos_sav; tot_moved = tot_moved + delta_moved
                vi = cs[1]; sp = cs[2]; cu = cs[3]; du = cs[4]
                ms = time(); sci = ms - mso;                                            # print("uSec = ", sci)
                sci = sci - int(sci); t = t + round(sci * 1000000); t1 = float(t/1000000)
                mso = ms
                if (forward):  # forward
                  packet = Message(arbitration_id=1, data=[0, 0, pid_out, 0])   # motor 1 controlled by PID
                  bus.send(packet)
                  packet = Message(arbitration_id=2, data=[0, 0, pid_out, 0])   # motor 2 controlled by PID
                  bus.send(packet)
                else:          # backwards
                  packet = Message(arbitration_id=1, data=[255, 255, 255-pid_out, 255])   # motor 1 controlled by PID
                  bus.send(packet)
                  packet = Message(arbitration_id=2, data=[255, 255, 255-pid_out, 255])   # motor 2 controlled by PID
                  bus.send(packet)
                pidu = (cs[0]-posAS)
                pid.update(pidu)
                pid_out = pid.output
                pid_out = abs(int(pid_out * scale))      # creat the vesc command value from the PID output
                if (pid_out >= max): pid_out = max
                if (pid_out <= min): pid_out = min       # make sure can can move
                print (" Target ", dest, " time ", t1, "currently @" , pidu, " Erpm ", cs[2], " current ", cs[3], " pid = ", pid_out )
#               cs = Motor.tacho_get(self)
            else:     # we need to back up
              while ( cs[0]-posAS >= dest + dz):
                pos_sav = pos; cs = Motor.tacho_get(self);  pos = cs[0]                           #    print("can status: ",cs)
                delta_moved = pos - pos_sav; tot_moved = tot_moved + delta_moved
                vi = cs[1]; sp = cs[2]; cu = cs[3]; du = cs[4]
                ms = time(); sci = ms - mso;                                            # print("uSec = ", sci)
                sci = sci - int(sci); t = t + round(sci * 1000000); t1 = float(t/1000000)
                mso = ms
                if (forward):  # forward
                  packet = Message(arbitration_id=1, data=[0, 0, pid_out, 0])   # motor 1 PID
                  bus.send(packet)
                  packet = Message(arbitration_id=2, data=[0, 0, pid_out, 0])   # motor 2 PID
                  bus.send(packet)
                else:          # backwards
                  packet = Message(arbitration_id=1, data=[255, 255, 255-pid_out, 255])   # motor 1 PID
                  bus.send(packet)
                  packet = Message(arbitration_id=2, data=[255, 255, 255-pid_out, 255])   # motor 2 PID
                  bus.send(packet)
                pidu = (cs[0] - posAS)
                pid.update(pidu)
                pid_out = pid.output
                pid_out = abs(int(pid_out * scale))      # creat the vesc command value from the PID output
                if (pid_out >= max): pid_out = max
                if (pid_out <= min): pid_out = min       # make sure can can move
                print (" Target ", dest, " time ", t1, " currently @", pidu, " Erpm ", cs[2], " current ", cs[3], " pid = ", pid_out )
            Motor.lock(self)
            cs = Motor.tacho_get(self)
            if (cs[0] - posAS >= dest + dz + 1): forward = False
            if (cs[0] - posAS <= dest - dz - 1): forward = True
#            if ((dest + dz) <= (cs[0] - posAS) or (dest - dz) >= (cs[0] - posAS)): done = true
#          except:
#             return()
#             pass
#       Motor.lock()

#// VESC Status message #1
#std::atomic<int32_t> rpm;
#std::atomic<int16_t> current;
#std::atomic<int16_t> duty;

#// VESC Status message #2
#std::atomic<int32_t> amp_hours;
#std::atomic<int32_t> amp_hours_charged;

#// VESC Status message #3
#std::atomic<int32_t> watt_hours;
#std::atomic<int32_t> watt_hours_charged;

#// VESC Status message #4
#std::atomic<int16_t> temp_fet;
#std::atomic<int16_t> temp_motor;
#std::atomic<int16_t> current_in;
#std::atomic<int16_t> pid_pos_now;

#// VESC Status message #5
#std::atomic<int32_t> tacho;      // VESC motor position
#std::atomic<int16_t> v_in;

#if __name__ == '__main__':
# main()



