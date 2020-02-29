
import can
import time
from time import time
from time import sleep
from can import Message
from datetime import datetime
from datetime import timedelta

#bus = can.interface.Bus('can0', bustype='socketcan_native')
bus = can.interface.Bus(channel='can0', bustype='socketcan', fd=True)
forward = True
#       open a can bus socket.... close it after move

#	// Convert tacho into inches
#	// wheel diameter = 59mm = 2.322835 inches
#	// wheel circumference = 7.2974 inches
#	// 1 tacho is 1/42nd of a revolution or 0.17375 inches

# the VESC updates his status 50 times per second 1/50 = 0.020 milliseconds
# at full speed the car moves almost 12 inches (67 tachos) in that amount of time

def tacho_get():
#   VESC status messages 2305: 3585: 3841: 4097: 6913:
#   now = datetime.now()
#   print(now.strftime("%H:%M:%S.%f"))
   num = 0;   m1 = False;   m2 = False;   m3 = False;   m4 = False;   m5 = False
   while ((m1 and m2 and m3 and m4 and m5) == False):
      message0 = bus.recv();  num = int(message0.arbitration_id)
      if (num == 2305):                            #message1
        a=message0.data[0]; b=message0.data[1]; c=message0.data[2]; d=message0.data[3]
        e=message0.data[4]; f=message0.data[5]; g=message0.data[6]; h=message0.data[7]
        rpm = (d + (c*256) + (b*65536) + (a*16777216))
        if (a>=128): rpm = rpm-4294967296
        current = float(f + (e*256))
        if (e>=128): current = current-65536
        duty = (h + (g*256))
        if (g>=128): duty = duty-65536
        m1 = True
      if (num == 3585):                            #message2
        a=message0.data[0]; b=message0.data[1]; c=message0.data[2]; d=message0.data[3]
        e=message0.data[4]; f=message0.data[5]; g=message0.data[6]; h=message0.data[7]
        m2 = True
      if (num == 3841):                            #message3
        a=message0.data[0]; b=message0.data[1]; c=message0.data[2]; d=message0.data[3]
        e=message0.data[4]; f=message0.data[5]; g=message0.data[6]; h=message0.data[7]
        m3 = True
      if (num == 4097):                            #message4
        a=message0.data[0]; b=message0.data[1]; c=message0.data[2]; d=message0.data[3]
        e=message0.data[4]; f=message0.data[5]; g=message0.data[6]; h=message0.data[7]
        Imot = float(f + (e*256))/10.0
        if (e>=128): Imot = Imot-6553.6
        m4 = True
      if (num == 6913):                            #message5
        a=message0.data[0]; b=message0.data[1]; c=message0.data[2]; d=message0.data[3]
        e=message0.data[4]; f=message0.data[5]; g=message0.data[6]; h=message0.data[7]
        tacho = (d + (c*256) + (b*65536) + (a*16777216))
        if (a>=128): tacho = tacho-4294967296
        vin = (f + (e*256))/10.0
        m5 = True
   canstat = [int(tacho), float(vin), float(rpm), float(Imot), float(duty)]
#   now = datetime.now()
#   now.microsecond
#   print(now.strftime("%H:%M:%S.%f"))
   return canstat

def lock():     #keeps can alive and motor stopped
    packet = Message(arbitration_id=1, data=[0, 0, 0, 0])
    bus.send(packet)
    packet = Message(arbitration_id=2, data=[0, 0, 0, 0])
    bus.send(packet)

def erpm_tab(nn):
#                   0   1   2    3    4    5    6     7     8     9     10   11   12   13   14   15   16   17   18
    accelPlus  = [  0,  50, 55,  60,  65,  70,  75,   80,   85,   90,   95,  100, 105, 110, 115, 120, 125, 130, 135,
#                   19   20   21   22   23   24   25    26    27    28    29
                    140, 145, 150, 155, 160, 165, 170,  175,  180,  185,  190]
#                   0   1   2    3    4    5    6     7     8     9     10   11   12   13   14   15   16   17   18
    slowPlus   = [  0, 182, 175, 167, 160, 152, 145,  137,  130,  122,  115, 107, 100, 92,  85,  77,  70,  62,  55,
#                   19   20   21   22   23   24   25  26    27   28    29
                    47,  40,  32,  25,  17,  10,  2,  0,    0,   0,    0]
#                   0    1    2    3    4    5    6    7     8     9     10   11   12   13   14   15   16   17   18
    accelMinus = [  255, 205, 200, 195, 190, 185, 180, 175,  170,  165,  160, 155, 150, 145, 140, 135, 130, 125, 120,
#                   19   20   21   22   23   24   25   26    27    28    29
                    115, 110, 105, 100, 95,  90,  85,  80,   75,   70,   65]
#                   0    1    2    3    4    5    6     7     8     9     10   11   12   13   14   15   16   17   18
    slowMinus  = [  255, 72,  80,  87,  95,  102, 110,  117,  125,  132,  140, 147, 155, 162, 170, 177, 185, 192, 200,
#                   19   20   21   22   23   24   25    26    27   28    29
                    207, 215, 222, 230, 237, 245, 252,  255,  0,   0,    0]
#                   0   1   2    3    4    5    6     7     8     9     10   11   12   13   14   15   16   17   18
    distUp =     [  0,  40,  80, 120, 160, 200, 240,  280,  320,  360,  400, 440, 480, 520, 560, 600, 640, 680, 720,
#                   19   20   21   22   23   24   25    26    27    28    29
                    760, 800, 840, 880, 920, 960, 1000, 1040, 1080, 1120, 1160]
#                   0   1    2    3    4    5    6    7    8    9   10   11   12   13   14   15   16   17    18
    distDown =   [  0, 61,  122, 183, 244, 305, 366, 427, 488, 549, 610, 671, 732, 793, 854, 915, 976, 1037, 1098,
#                   19    20    21    22    23    24    25    26    27    28    29
                    1159, 1220, 1281, 1342, 1403, 1464, 1525, 1586, 1647, 1648, 1649]
    val = [int(distUp[nn]), int(distDown[nn]), int(accelPlus[nn]), int(slowPlus[nn]), int(accelMinus[nn]), int(slowMinus[nn]) ]
#    print("seek up = ", val[0], " seek dn = ", val[1], " posvesc = ", val[2]," negvesc = ", val[3])
    return val

def plan(move, tier, dir):          # call with the distance you want to move in tachos
                                    # no moves lees than 5 ft and subtract 1 foot for creep to position
    rvesc = [0]; rdist = [0]
    if (move <= 345):
      rvesc = [ -1 ]; rdist = [ -1 ]
      rv = [ rdist, rvesc ]
      return rv                     # return error code of -1
    move = move - 140               # subtract stopping distance (2 feet)
    if (tier == 1):  maxI = 5       # set tier 1
    if (tier == 2):  maxI = 13      # set tier 2
    if (tier == 3):  maxI = 21      # set tier 3
    if (tier == 4):  maxI = 29      # set tier 4  (max)
    ck = erpm_tab(maxI)             # get highest distance for this tier
    dUp = ck[0]; dDn = ck[1]
    chop = True                     # if we need to move less than this then we must chop the pyramid
    if (move >= (dUp + dDn)): 
      cntLimit = maxI; chop = False
      cnt = 1
      while (not chop and cnt <= cntLimit):
        nxt = erpm_tab(cnt)
        rdist.append(nxt[0])
        if (dir): rvesc.append(nxt[2])
        else: rvesc.append(nxt[4])
        cnt += 1
      nxt = erpm_tab(cnt-1)
      cnt = 1
      middle = move - (dUp + dDn)
      print(" d up, d dn, move, middle ",dUp,dDn,move,middle)
      if (dir): rvesc.append(nxt[2])
      else: rvesc.append(nxt[4])
      dist_sv = nxt[0] + middle
      rdist.append(dist_sv)
      while (not chop and cnt <= cntLimit):
        nxt = erpm_tab(cnt)
        rdist.append(nxt[1]+ dist_sv)
        nxt = erpm_tab(cnt + 6)          ##### error for tier 1,2 and 4... only works for tier 3
        if (dir): rvesc.append(nxt[3])
        else: rvesc.append(nxt[5])
        cnt += 1
    else:
      cnt = 1
      cntLimit = maxI
      while (move <= (dUp + dDn) and cnt <= 25):
        ck = erpm_tab(cntLimit-cnt)               # get next highest distance for this tier
        dUp = ck[0]; dDn = ck[1]
        cnt += 1
        print(" move, count-limit, dUp, dDn  ", move, cntLimit, dUp, dDn)
      cntLimit = maxI - cnt
      cnt = 1
      rvesc = [0]; rdist = [0]
      print(" chopped move count limit = ", move, cntLimit, dUp, dDn)
      while (chop and cnt <= cntLimit):
        nxt = erpm_tab(cnt)
        rdist.append(nxt[0])
        if (dir): rvesc.append(nxt[2])
        else: rvesc.append(nxt[4])
        cnt += 1
      nxt = erpm_tab(cnt-1)
      cnt = 1
      middle = move - (dUp + dDn)
      print(" d up, d dn, move, middle ",dUp,dDn,move,middle)
      if (dir): rvesc.append(nxt[2])
      else: rvesc.append(nxt[4])
      dist_sv = nxt[0] + middle
      rdist.append(dist_sv)
      while (chop and cnt <= cntLimit):
        nxt = erpm_tab(cnt)
        rdist.append(nxt[1]+ dist_sv)
        nxt = erpm_tab(cnt + 6)          ##### error for tier 1,2 and 4... only works for tier 3
        if (dir): rvesc.append(nxt[3])
        else: rvesc.append(nxt[5])
        cnt += 1

#enter motor command: (eg t,600 or t,-600
#t,3000
# d up, d dn, move, middle  840 1281 1586 -535
# chopped move count limit =  20
# d up, d dn, move, middle  840 1281 1586 -535
# vector is  ([0, -535, 40, 80, 120, 160, 200, 240, 280, 320, 360, 400, 440, 480, 520, 560, 600, 640, 680, 720, 760, 800, 265, 326, 387, 448, 509, 570, 631    , 692, 753, 814, 875, 936, 997, 1058, 1119, 1180, 1241, 1302, 1363, 1424, 1485], [0, 0, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 1    25, 130, 135, 140, 145, 145, 137, 130, 122, 115, 107, 100, 92, 85, 77, 70, 62, 55, 47, 40, 32, 25, 17, 10, 2, 0])
#current pos =  6931

#    for x in rvesc:
#      print (x)
#    for x in rdist:
#      print (x)
    rv = ( rdist, rvesc )
    return rv

#    pos = [ 40, 80, 120, 160, 200, 240, 280, 320, 360, 400, 440, 480, 520, 560, 600, 640, 680, 720,
#           760, 800, 840, 2520, 2581, 2642, 2703, 2764, 2825, 2886, 2947, 3008, 3069, 3130, 3191,
#           3252, 3313, 3374, 3435, 3496, 3557, 3618, 3679, 3740]
#    vescPlus = [ 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130, 135, 140,
#                145, 150, 150, 142, 135, 127, 120, 112, 105,  97,  90, 82, 75, 67, 60, 52, 45, 37,
#                 30, 22, 15, 7, 0, 0, 0]
#    vescMinus = [205, 200, 195, 190, 185, 180, 175, 170, 165, 160, 155, 150, 145, 140, 135, 130, 125,
#                 120, 115, 110, 105, 105, 113, 120, 128, 135, 143, 150, 158, 165, 173, 180, 188, 195,
#                 203, 210, 218, 225, 233, 240, 248, 255, 255, 255]
#    dc = [ int(pos[nn]), int(vescPlus[nn]), int(vescMinus[nn]) ]

def clr_buf():
    cnt = 0
    while (cnt <= 100):
      cs = tacho_get()
      cnt = cnt + 1

def main():
  global forward
  cnt=0; command=" "
  lock()
  tier = 3       #will read this from the config file eventually
  print("enter motor command: (eg t,600 or t,-600 ")
  command = input()                         # string = str(input())
  lock()
#  now = datetime.now()
#  print(now.strftime("%H:%M:%S.%f"))
  p=command.find(",")                       # find the start of the desired position
  dd='{}'.format(command)[p+1:len(command)] # dd has the value in tenths of inches that we want to move
  dd=round((float(dd)/10.0)*5.755)          # dd now has the number of tachos we need to move
  if (dd > 0): forward = True
  else: forward = False                     # are we going forward or back towards home
  dds = dd; dd = abs(dd)
  print("distance, tier, direction ", dd, tier, forward)
  ss = plan(dd, tier, forward)
  print (" vector is ", ss)
  rdist = ss[0]
  rvesc = ss[1]
#  print("1st pair = ", rdist[1], rvesc[1], len(rdist), len(rvesc))

#  print("currently at: ", pos, " slowing position: ", seek, " distance to move = ", dds, " spd = ", spd[0], " -spd = ", spd[1])
  mso = time(); t = 0; sci = 0
  clr_buf()
#  lock()
  tot_moved = 0; delta_moved = 0; cs = tacho_get()                      # get our current position
  posAS = cs[0];  pid_only = False; dda = abs(dds); pos = posAS; cnt=1  # position at start of move is now in posAS
  print ("current pos = ",pos)
  now = datetime.now()
  print(now.strftime(" starting run %H:%M:%S.%f"))
  while (cnt <= len(rdist)-1):                           # 0-29 = 30 counts
    mv = rdist[cnt]
    print(" next point = ", mv)
    if (forward): seek =  posAS + mv                     # get next target tacho value
    else: seek = posAS - mv
#    posAS = seek
    print("next pair, index, & position ", rdist[cnt], rvesc[cnt], cnt, pos)
    while (forward and pos <= seek) or ((not forward) and pos >= seek):       # 200 times 0.005 seconds = 1 second run
      pos_sav = pos; cs = tacho_get();  pos = cs[0]                           #    print("can status: ",cs)
      delta_moved = pos - pos_sav; tot_moved = tot_moved + delta_moved
      vi = cs[1]; sp = cs[2]; cu = cs[3]; du = cs[4]
      ms = time(); sci = ms - mso;                                            # print("uSec = ", sci)
      sci = sci - int(sci); t = t + round(sci * 1000000); t1 = float(t/1000000)
      mso = ms; sci=0.0
      print("Tacho =, ", pos, " ,delta =, ", delta_moved, " ,eT =, %.4f" % t1, " ,eRPM =, ", sp, " ,Duty =, ", du,
            " ,Vin =, ", vi, " ,Imot =, %.2f" % cu,  " ,Moved =, ", tot_moved, )
#      sleep(3)
#      break
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
  lock()
  lock()

#  while True:
#     lock()

#    print ("\033[40;31Htacho = ", pos, " Volts = ", v)

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

if __name__ == '__main__':
 main()