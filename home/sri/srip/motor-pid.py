#!/usr/bin/python3
from multiprocessing import Process, Array   # multi-processing support
import threading, time
import Adafruit_BBIO.GPIO as GPIO
import can                                   # can buss support
from can import Message                      # can buss message handler support
from time import time, sleep                 # does anybody really know what time it is?
from datetime import datetime, timedelta     # does anybody really care?
import PID                                   # PID routines
import MOT                                   # config parameters come from this file

""" SRI ATRS Car Motor Controller """
    #       open a can bus socket.... close it after move

    #       // Convert tacho into inches
    #       // wheel diameter = 59mm = 2.322835 inches
    #       // wheel circumference = 7.2974 inches
    #       // 1 tacho is 1/42nd of a revolution or 0.17375 inches

    # the VESC updates his status 50 times per second 1/50 = 0.020 milliseconds
    # at full speed the car moves almost 12 inches (67 tachos) in that amount of time

#    myStatus[0] = myStatus[0]     ### mytarget for next move (in tenths of inches)
#    myStatus[1] = float(cs[0])    ### myposition.value = cs[0] in tachos
#    myStatus[2] = float(cs[1])    ### myvoltage.value = cs[1]
#    myStatus[3] = float(cs[2])    ### myerpm.value = int(cs[2])
#    myStatus[4] = float(cs[3])    ### mymotorcurrent.value = cs[3]
#    myStatus[5] = float(cs[4])    ### mydutycycle.value = int(cs[4])
#    myStatus[6] = myStatus[6]     ### myhome.value = saved home tacho value $$$$$$$$$$$$$$$$$
#    myStatus[7] = myStatus[7]     ### mydeadzone allowance in tachos
#    myStatus[8] = myStatus[8]     ### mymoving (is the current move finished)
#    myStatus[9] = myStatus[9]     ### myCommand (from client)
#    myStatus[10] = myhome         ### magnetic sensor for "home" 0=home, 1=not home

class Motor:
  global bus
  bus = can.interface.Bus(channel='can0', bustype='socketcan', fd=True)
  GPIO.setup("P8_15", GPIO.IN)           ### magnetic switch at "home"

  def crawl_home(self, myStatus):
    if (myStatus[10] != 0.0):
      Motor.pid_home(self, myStatus, posAS, posAE, targetsv, forward)

  def startController(self, mq, qs): ### starts the actual motor controller and processes motor commands
    myStatus = Array('d', range(15)) ### common array of 15 for passing status information
    Motor.stat(self, myStatus)       ### update the status values every time you call this routine
    myStatus[0] = 0.0                ### make sure target position starts with zero (no move)
    #Motor.pid_home(self, myStatus, posAS, posAE, targetsv)
    #Motor.crawl_home(slef, myStatus) ### before we do this (set home position) I need to make sure we are really home
                                     ### so I need to amke a subroutine to on initial load "crawl home" or from a jam
    myStatus[6] = myStatus[1]        ### set the home command equal to where we are now
    mot = MOT.MOT()                  ### activate our parameters to be read on the next line
    av = mot.motInit()               ### import the PID values, tier,  and other parameters
    myStatus[7] = av[5]              ### allowable "dead zone" plus or minus in tachos
    run_process = Process(target=self.start, args=( myStatus, ))  ### set up the main "motor looop" that runs forever
    run_process.start()              ### start the main motor controller loop as a "process"
    done = False                     ### we are not done (indeed just starting)
    myStatus[8] = 0                  ### we are not moving
    while (not done):                ### look for motor commands until we are done (until we quit the program completely)
      while ((not mq.empty()) and (myStatus[8] == 0)):  ### do we have a new motor command??? and are we moving???
        myStatus[8] = 1.0            ### tell it we are moving
        m = mq.get()                 ### get the motor command (home or "target")
        myStatus[9] = float(m[0]); print(' motor cmd from client = ', myStatus[9]) ### debug print the command we think we got
        m="".join( chr(x) for x in m)  ### python requires me to convert it from byutes to a string
        if m == "quit":                ### now I can see ifit is time to quit (ie we are done)
          mytarget.value = -1          ### -1 is used in python as a universal error condition (and we will never move to -1)
          done = True                  ### besides we are quitting now anyway
        else:                          ### if we are not done
          if (m[0] == 'h'):            ### see if we want to go "home"
            dtm = 0.0; dfh = 0.0;      ### initialize the distance to home and the distance to move both to zero
            print("--- we are here ", myStatus[1], " home is here ", myStatus[6])  ### debug print how far it is to home?
            if ((myStatus[1]+myStatus[7] >= myStatus[6]) and (myStatus[1]-myStatus[7] <= myStatus[6])):
            ### the above line checks to see if we are with8n the "dead zone" distance of our "home" position
            ### if(myStatus[10] == 0)    ### magnetic switch says "we are at home"
              print(' we seem to be home ', myStatus[10])         ### debug print the magnetic switch status
                                         ### if we have a home command and we are already home we don't need to do anything
                                         ### we previously set our distance to home = to zero and our distance to move also zero
            else:                        ### if we are not home then we need to go home
              dfh = myStatus[1] - myStatus[6]       ### calculate distance from home in tachos
              print( ' we are not home ', dfh)      ### first see if we are within 5 feet of home
              dtm = round(((dfh-345)/5.755) * 10.0) ### distance to move minus 5 feet for safety (converted tachos to 1/10th inches)
              print('generated home command in 1/10th inches(-60" safety) = ', -dtm)  ### we are going home so DTM is negative
                                         ### myStatus[8]=1 says we are moving now (soon) nad myStatus[0] is where we want to go
              myStatus[8] = 1.0; myStatus[0] = -dtm   ### tell it to "normal move" most of the way home (-5 feet)
          else:                                       ### if it is not a "home" then it is a "target" move
            pos = m.find(',')                         ### find the comma (t,600) so we can grab the distance to move
            print( ' target command from client ' ,m ,pos)  ### debug print where do we want the car?
            if ( pos >= 1 ):                                ### if there is no comma then do nothing
              num = float('{}'.format(m)[pos + 1: len(m)])  ### pos part of the target command from the client (iPad)
              dfh = myStatus[1] - myStatus[6]               ### distance from home (tachos) in other words where are we now?
              if (abs(dfh) <= myStatus[7]):                 ### are we home by any chane (plus or minus the dead zone)?
                print ( ' move from home ', myStatus[7])    ### debug print we are moving from home
              tpt = ((num/10.0) * 5.755)                    ### tpt = target position (in tachos now)
              print( ' num = ', num, ' home = ', myStatus[6], ' dfh = ', dfh, ' target pos tachos = ', tpt) ### debug print
              if( tpt >= dfh ):                             ### is target position >= our distance from home then we have
                myStatus[0] = round(((tpt-dfh)/5.755)*10.0) ### a positive move (away from shooter)
                myStatus[8] = 1                             ### flag we are moving (soon)
                print(" move out further (tachos) ", round(tpt-dfh), 'tachos ', myStatus[0], 'tenth of inches')  ### debug print
              else:                                         ### if target position is less than our distance from home then
                myStatus[0] = round(((dfh-tpt)/5.755)*-10.0) ### we have a negative move (back towards shooter)
                myStatus[8] = 1                              ### flag we are moving (soon)
                print( " move back closer to home ", round(tpt-dfh), 'tachos ', myStatus[0], 'tenth of inches')  ### debug print
              print("CMD + stat ", m, myStatus[:])         ### print our command and the cur status

      # qs.put(myStatus)  ### klater we will use our queues to send the status back to the iPad

  ### lock routine keeps the motor off and "not" burning rubber
  def lock(self):     # keeps can alive and motor stopped
    global bus        # can buss has to be globally available
    packet = Message(arbitration_id=1, data=[0, 0, 0, 0])  ### motor 1
    bus.send(packet)
    packet = Message(arbitration_id=2, data=[0, 0, 0, 0])  ### motor 2
    bus.send(packet)

  def clr_buf(self):    ### clear out any accumulated can bus messages to get a "fresh" look at the can status
    cnt = 0             ### this is just a safety precaution. I am not sure if it is needed
    while (cnt <= 100): ### can messages accumulate at a high rate so this flushes the can buffer
      cs = Motor.tacho_get(self)
      cnt = cnt + 1

  def tacho_get(self):
  #   this routine reads the vesc can buss and extracts the current status for use by the program
  #   this routine is called repeatedly by the motor controller to find out "where" it is
  #   VESC status messages 2305: 3585: 3841: 4097: 6913:
  #   now = datetime.now()
  #   print(now.strftime("%H:%M:%S.%f"))
  #   we linger in this routine until we get all five can buss messages
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
    ### the above line returns the can buss status including the current position and motor information
    # now = datetime.now()
    # now.microsecond
    # print(now.strftime("%H:%M:%S.%f"))
    return canstat


  ### This is our stored vectors for all motion commands
  ### repeated calls to this routine are made to "build" the motion vectors for any move
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
    accelPlus  = [  0,  40,  42,  45,  49,  53,  58,  63,   68,   73,   79,  85,  91,  97,  104, 111, 118, 125, 132,
    #               19   20   21   22   23   24   25    26    27    28    29
                    138, 144, 150, 155, 160, 165, 170,  175,  180,  185,  190]
    #               vector[3] = vesc commands for a positive move while slowing down
    #               0   1   2    3    4    5    6     7     8     9     10   11   12    13    14   15   16   17   18
    slowPlus   = [  0, 184, 178, 172, 166, 160, 154,  148,  142,  135,  129, 123, 117, 111,  105,  99,  93,  87,  81,
    #               19   20   21   22   23   24   25   26      27     28     29
                    75,  69,  63,  57,  50,  44,  38,  mm+24,  mm+16, mm+8,  mm]
    #               vector[4] = vesc commands for a negative move while accelerating
    #               0    1    2    3    4    5    6    7     8     9     10   11   12   13   14   15   16   17   18
    accelMinus = [  255, 215, 213, 210, 206, 202, 197, 192,  187,  182,  176, 170, 164, 158, 151, 144, 137, 130, 123,
    #               19   20   21   22   23   24   25   26    27    28    29
                    117, 111, 105, 100, 95,  90,  85,  80,   75,   70,   65]
    #               vector[5] = vesc commands for a negative move while slowing down
    #               0    1    2    3    4    5    6     7     8     9     10   11   12   13   14   15   16   17   18
    slowMinus  = [  255, 71,  77,  83,  89,  95,  101,  107,  113,  120,  126, 132, 138, 144, 150, 156, 162, 168, 174,
    #               19   20   21   22   23   24   25    26      27       28      29
                    180, 186, 192, 198, 205, 211, 217,  mn-24,  mn-16,   mn-8,   mn]
    #   end of vectors. call to this routine returns current value for all 6 vectors in an array
    val = [int(distUp[nn]), int(distDown[nn]), int(accelPlus[nn]), int(slowPlus[nn]), int(accelMinus[nn]), int(slowMinus[nn]) ]
    #   print("seek up = ", val[0], " seek dn = ", val[1], " posU = ", val[2]," posDn = ", val[3], " negUp = ", val[4], " negDn = ", val[5])
    return val


  ### this routine build the motion control vectors for every move (except PID when close to home)
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
  ### this routine updates all status information every time it is called
  def stat(self, myStatus ):     ### mytarget, mypos, myvoltage, myerpm, mycurrent, myduty, ):
    cs = Motor.tacho_get(self)
    myStatus[0] = myStatus[0]     ### mytarget for next move (in tenths of inches)
    myStatus[1] = float(cs[0])    ### myposition.value = cs[0] in tachos
    myStatus[2] = float(cs[1])    ### myvoltage.value = cs[1]
    myStatus[3] = float(cs[2])    ### myerpm.value = int(cs[2])
    myStatus[4] = float(cs[3])    ### mymotorcurrent.value = cs[3]
    myStatus[5] = float(cs[4])    ### mydutycycle.value = int(cs[4])
    myStatus[6] = myStatus[6]     ### myhome.value = saved home tacho value $$$$$$$$$$$$$$$$$
    myStatus[7] = myStatus[7]     ### mydeadzone allowance in tachos
    myStatus[8] = myStatus[8]     ### mymoving (is the current move finished)
    myStatus[9] = myStatus[9]     ### myCommand (from client)
    if GPIO.input("P8_15"):
      myhome = 1.0
    else:
      myhome = 0.0                ### magnetic home switch (1 = not home, 0 = home)
    myStatus[10] = myhome

  """  -----------------------------------------------------------------------------------
  this routine gets launched at the start of the server and runs forever (until server death)
       ----------------------------------------------------------------------------------- """
  def start(self, myStatus, ):
    global bus
    done = False       ### we are never done
    mot = MOT.MOT()    ### get our intial parameters
    av = mot.motInit() ### import the PID values, tier,  and other parameters
    P=av[0]; I=av[1]; D=av[2]; min=av[3]; max=av[4]; dz=av[5]; tier=av[6] ### set them all
    Motor.stat(self, myStatus)  ### update (read) the current status
    myStatus[7] = dz            ### allowable "dead zone" plus or minus in tachos
    print( " -*-*-*-*-*-*- motor target value = ", myStatus[0], ' int cmnd = ', myStatus[9])
    while (not done):           ### main motor control loop
        cnt = 0                 ### cnt is used to step through the motion control vectors one step at a time
#       if (myStatus[0] <= -1 ): return()
        Motor.lock(self)        ### insure motor is "off"
#       now = datetime.now()
#       print(now.strftime("%H:%M:%S.%f"))
        Motor.stat(self, myStatus)          # update status values
        dd=round((myStatus[0]/10.0)*5.755)  # dd (desired distance) now has the number of tachos we want to move
        if (dd > 0): forward = True   # determine the direction we want to go
        else: forward = False         # are we going forward or back towards home
        dds = dd; dd = abs(dd)        # dds (save the desired distance) we know the direction so make DD "positive"
        ss = Motor.plan(self, dd, tier, min, forward) # build our move vectores from the vector tables
        rdist = ss[0]                 # vector for distances
        rvesc = ss[1]                 # vector vor motor speeds (VESC)
        print( " -*-*-*-*-*-*- start motor target value = ", myStatus[0] )  # debug print of where we are going
        print("Target = ", myStatus[0], " distance ", dds, " tier ", tier, " direction ", forward)  #debug print
        print("distance vector ",rdist)  # debug print of distances for each move segment
        print("VESC vector is ",rvesc)   # debug print of VESC speed commands for each move segment
        targetsv = myStatus[0]           # save the target location (save where we are headed)
        mso = time(); t = 0; sci = 0     # keep track of time for this move
        Motor.clr_buf(self)              # clear out the can buss buffer (just in case)
        Motor.lock(self)                 # start out not moving (just in case) we should have been stopped anyway
        cs = Motor.tacho_get(self)
        if (myStatus[0]==0):
          print('init PID at startup to hold pos ',cs[0], myStatus[6], targetsv, forward)
          Motor.pid_home(self, myStatus, cs[0], myStatus[6], targetsv, forward)
          break
        else:
          tot_moved = 0; delta_moved = 0; cs = Motor.tacho_get(self); posAE = cs[0]+dds   # get our current position from can
                                           # compute our position at the end of the move (posAE)
          posAS = cs[0];  pid_only = False; pos = posAS; cnt=1  # position at start of move is now in (posAS)
                                                                # cnt = 1 (start with first vector value)
          print ("pos at start ", posAS," distance to move ", dds, " pos at end ", posAE)  # debug print
          now = datetime.now()             # time move actually started
          print(now.strftime(" starting run %H:%M:%S.%f"))  # debug print of start time
          while (cnt <= len(rdist)-1):                      # 0-29 = up to 30 vector segments for each move
            mv = rdist[cnt]                                 # get the first distance (from the distance vector that was made)
            print(" next point = ", mv)                     # debug print
            if (forward): seek =  posAS + mv                # get next target tacho value (either positive)
            else: seek = posAS - mv                         # or negative
            print("next pair, index, & position ", rdist[cnt], rvesc[cnt], cnt, pos) # debug print both vectors
            while (forward and pos <= seek) or ((not forward) and pos >= seek):      # vector segment while loop
              pos_sav = pos; cs = Motor.tacho_get(self);  pos = cs[0]                # save where we were in pos_sav
              # read cann and get where we are now (pos)
              delta_moved = pos - pos_sav; tot_moved = tot_moved + delta_moved       # debug book keeping of move progress
              vi = cs[1]; sp = cs[2]; cu = cs[3]; du = cs[4]   # can buss status of V, erpm, I and duty
              ms = time(); sci = ms - mso;                     # elapsed time calculations (in micro seconds)
              sci = sci - int(sci); t = t + round(sci * 1000000); t1 = float(t/1000000)
              mso = ms; sci=0.0                                # just for debug purposes (times move progress)
              print("Tacho =, ", pos, " ,delta =, ", delta_moved, " ,eT =, %.4f" % t1, " ,eRPM =, ", sp, " ,Duty =, ", du,
                    " ,Vin =, ", vi, " ,Imot =, %.2f" % cu,  " ,Moved =, ", tot_moved, ) #debug print move "stats"
#             break uncomment this to actually prevent any moving (kills the motors)
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
            cnt += 1              # increment cnt for next vector segment to be processed
            now = datetime.now()  # update the time
            print(now.strftime(" should be end of segment %H:%M:%S.%f")) #debug print of move segment finish time
            # we incremented to next segment so the previous one is done now (above line)
            if (forward and sp <= 1500 and cnt >= (len(rvesc)/2)): cnt = len(rdist)  # if we are moving slowly, then kick in PID
            if ( not forward and sp >= -1500 and cnt >= (len(rvesc)/2)): cnt = len(rdist)
            # no need to wait for all vector segments to finish (otherwise we remain in the "while cnt" loop
          ### --- move is over so enable pid ( will home in to target position and then hold us there )
          else:  ### vectors are done or speed has been reduced so go into PID mode
            print("start PID loop here -------------- ",myStatus[0])  ### debug print the position we seek is in myStatus[0]
            Motor.pid_home(self, myStatus, posAS, posAE, targetsv, forward)

  def pid_home(self, myStatus, posAS, posAE, targetsv, forward):
    global bus
    print('we are in PID with ', posAS, posAE, targetsv)
    now = datetime.now()  # update the time
    print(now.strftime(" entered PID @ %H:%M:%S.%f")) #debug print of move segment finish time
    mot = MOT.MOT()    ### get our intial parameters
    av = mot.motInit() ### import the PID values, tier,  and other parameters
    P=av[0]; I=av[1]; D=av[2]; min=av[3]; max=av[4]; dz=av[5]; tier=av[6] ### set them all
    pid = PID.PID(P, I, D)      ### init the PID controller
    pid.setSampleTime(0.019999) ### PID sample rate 50 times per second
    Motor.stat(self, myStatus)  # get the current status
    cs = Motor.tacho_get(self)  # get the current can buss info
    pos = cs[0]                 # where we are from can buss
    tot_moved = 0               # keep track of how far we move
    dest = int(posAE - posAS)   # destination is the position at start + the size of the move (can be + or - move)
    if (myStatus[9] == 104): dest = int((myStatus[6]-posAS) - 25)  # modify destination if "home" command
    # the reason for above line is to re-adjust the target position to add back in the (5 feet) we shorted the home
    nowT = int(cs[0] - posAS)  # our current target (nowT) is the distance we are from the start position
    pid.clear                  # clear all the PID parameters to a fresh start
    pid.SetPoint = dest        # set PID to desired destination
    pid.update(nowT)           # feed PID our current position
    pid_out = pid.output       # get what the PID has to say
    scale = min/1000           # needs to be scaled
    pid_out = abs(int(pid_out * scale))  # creat the vesc command value from the PID output (make sure itis positive)
    if (pid_out >= max): pid_out = max   # max PID (from parameters in our setup file)
    if (pid_out <= min): pid_out = min   # min PID
    print ("PID destination ", dest, " PID output = ", pid_out, ' (T=For, F=Bak) ', forward) # debug print of PID
    ### PID setup is finished now so go into final while loop (PID finishes current move)
    ### then PID waits for a "new" destination. (ie one that is different from it's current positionj)
    mso = time(); t = 0; sci = 0     # keep track of time for this move
    Motor.clr_buf(self)              # clear out the can buss buffer (just in case)
    Motor.lock(self)                 # start out not moving (just in case) we should have been stopped anyway
    #cs = Motor.tacho_get(self)
    now = datetime.now()  # update the time
    print(now.strftime(" actual start PID loop @ %H:%M:%S.%f")) #debug print of move segment finish time
    while (myStatus[0] == targetsv): # while there is no move needed stay where you are
      #Motor.stat(self, myStatus)     # get the status
      if (forward):                  # if we are not at destination and going forward
        while ( cs[0]-posAS <= dest - dz): # do this while loop
          Motor.stat(self, myStatus)
          pos_sav = pos; cs = Motor.tacho_get(self);  pos = cs[0]       # print("can status: ",cs)
          delta_moved = pos - pos_sav; tot_moved = tot_moved + delta_moved
          vi = cs[1]; sp = cs[2]; cu = cs[3]; du = cs[4]
          ms = time(); sci = ms - mso;                                  # print("uSec = ", sci)
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
          if (pid_out <= min): pid_out = min       # make sure can can move      pidu
          print (" Trgt ", dest, " tm ", t1, "now @", cs[0], " Erpm ", cs[2], " mot I ", cs[3], " pid = ", pid_out )
#         cs = Motor.tacho_get(self)
      else:     # if we are not at destination and going backwards (we need to back up)
        while ( cs[0] - posAS >= dest + dz): # do this while loop
          Motor.stat(self, myStatus)
          pos_sav = pos; cs = Motor.tacho_get(self);  pos = cs[0]                 # print("can status: ",cs)
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
          #else:
          #  pid_out = max                         # for from home pid can go up to max
          if (pid_out >= max): pid_out = max
          if (pid_out <= min): pid_out = min       # make sure car can move
          if ((abs(myStatus[1]-myStatus[6]) <= 345)):
            pid_out = min                          # on [near] home pid is weakened
          print (" Trgt ", dest, ' PID trg ', pidu, " tm ", t1, " now @", cs[0], " Erpm ", cs[2],
                 " mot I ", cs[3], " pid = ", pid_out )
          if ((abs(myStatus[3] <= 10))): myStatus[8] = 0  ### (abs(dest-pidu)<= dz) or
          #print('--- are we still moving? ', abs(dest-pidu), ' end move flag = ',myStatus[8])
      Motor.lock(self) # if we are there then trun off motor
      myStatus[8] = 0  # trun off "moving" status message
      Motor.stat(self, myStatus) # update status
      cs = Motor.tacho_get(self) # get can buss info
      if (cs[0] - posAS >= dest + dz + 1): forward = False  # keep PID on and re-position if some moves us
      if (cs[0] - posAS <= dest - dz - 1): forward = True
    else:
      now = datetime.now()  # update the time
      print(now.strftime(" left PID @ %H:%M:%S.%f")) #debug print of move segment finish time
      Motor.start(self, myStatus)  ### if we get a new motion command then get out of PID and go to Motor.start
#if __name__ == '__main__':
# main()



