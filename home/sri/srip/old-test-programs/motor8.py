
import can
import time
from time import time
from time import sleep
from can import Message
from datetime import datetime
from datetime import timedelta
import PID

#bus = can.interface.Bus('can0', bustype='socketcan_native')
bus = can.interface.Bus(channel='can0', bustype='socketcan_native', fd=True)
forward = True
pid_on = False
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
#                 0    1    2    3    4    5    6    7    8    9   10
    erpmPlus  = [ 0,  18,  35,  50,  58,  68, 105, 125, 150, 175, 200]
    erpmMinus = [ 0, 237, 220, 205, 197, 187, 150, 130, 105,  80,  55]
    spd = [int(erpmPlus[nn]), int(erpmMinus[nn])]
#    print("speed = ",spd[0]," ",spd[1])
    return spd

def rampDn(dc):
    global forward
    if (not forward):
      dc = 255 - dc
      packet = Message(arbitration_id=1, data=[255, 255, dc, 255])
      bus.send(packet)
      packet = Message(arbitration_id=2, data=[255, 255, dc, 255])
      bus.send(packet)
    else:
      packet = Message(arbitration_id=1, data=[0, 0, dc, 0])
      bus.send(packet)
      packet = Message(arbitration_id=2, data=[0, 0, dc, 0])
      bus.send(packet)

def clr_buf():
    cnt = 0
    while (cnt <= 100):
      cs = tacho_get()
      cnt = cnt + 1

def pid_destination(pos, dist):
    global forward
    global pid
    global pid_on
    spd = erpm_tab(1); crawl_speed = spd[0]                 # set speed to crawl speed [erpm_tab(1)]
    rampDn(crawl_speed)
    cs = tacho_get()
    print("PID started: tachos = ",cs[0], " target = ", pos)
    while ((forward and cs[0] <= pos-1) or (not forward and cs[0] >= pos+1)):
      pid.update(cs[0])
      pid_val = pid.output
      cs = tacho_get()
      print("PID = ",pid_val, " PID cur pos = ",cs[0], " target pos = ", pos)
    rampDn(0); pid_on = True
    pid_hold(pos)     # stop it at the target

def pid_hold(lock_pos):
  global pid_on
  global forward
  global pid
  spd = erpm_tab(1); crawl_speed = spd[0]                 # set speed to crawl speed [erpm_tab(1)]
  while pid_on:
    cs = tacho_get()
    while ((cs[0] <= lock_pos+6) or (cs[0] >= lock_pos-6)):
      cs = tacho_get(); rampDn(0)     #lock
#      print(" lock pos = ",cs[0])
      if (cs[0] >= lock_pos+6):
        forward = False; rampDn(crawl_speed)
      if (cs[0] <= lock_pos-6):
        forward = True; rampDn(crawl_speed)

def main():
  global forward
  global pid
  cnt=0; command=" "
  lock()
  print("enter motor command: (eg t,600 or t,-600 ")
  command = input()                         # string = str(input())
  lock()
  now = datetime.now()
  print(now.strftime("%H:%M:%S.%f"))
  p=command.find(",")                       # find the start of the desired position
  dd='{}'.format(command)[p+1:len(command)] # dd has the value in tenths of inches that we want to move
  dd=round((float(dd)/10.0)*5.755)          # dd now has the number of tachos we need to move
  if (dd > 0): forward = True
  else: forward = False                     # are we going forward or back towards home
  dds = dd; dd = abs(dd)
  tot_moved = 0; delta_moved = 0; cs = tacho_get()                         # get our current position
  pos = cs[0];  pid_only = False; dda = abs(dds)
  targetP = dds + pos
  targetD = dds
  P = 30.0
  I = 0.4
  D = 1.2
  pid = PID.PID(P, I, D)
  pid.SetPoint = float(targetP)
  pid.setSampleTime(0.019999)
  pid.setKp(30.0)
  pid.setKi(0.4)
  pid.setKd(1.2)

#  pid.proportional_on_measurement = True

  if (dda >= 3100): spd = erpm_tab(8); dd = (dd/1.5) - 85                 ### dda is in "TACHOS"
  else:                                                                    # moving 10 - 50 yards
    if (dda >= 2070): spd = erpm_tab(7); dd = (dd/1.5) - 70
    else:                                                                  # moving 5 - 10 yards
      if (dda >= 1032): spd = erpm_tab(6); dd = (dd/1.8) - 65
      else:                                                                # moving 4 - 5 yards
        if (dda >= 826): spd = erpm_tab(5); dd = (dd/1.9) - 60
        else:                                                              # moving 3 - 4 yards
          if (dda >= 620): spd = erpm_tab(4); dd = (dd/2.0) - 60
          else:                                                            # moving 2 - 3 yards
            if (dda >= 414): spd = erpm_tab(3); dd = (dd/2.1) - 60
            else:                                                          # moving 1 - 2 yards
              if (dda >= 207): spd = erpm_tab(2); dd = (dd/2.2) - 55
              else:                                                        # moving < 1 yard use PID-ONLY
                if (dda >= 12): spd = erpm_tab(1); dd = (dd/2.3) - 50      # minimum move is 2 inches

  if (forward):
    seek = pos + dd                                                      # we are going forward
    if (spd[0] <= 20): seek = pos + dda - 25; pid_only = True
  else:
    seek = pos - dd                                                      # or back towards home
    if (spd[1] >= 235): seek = pos - dda + 25; pid_only = True
  print("currently at: ", pos, " slowing position: ", seek, " distance to move = ", dds, " spd = ", spd[0], " -spd = ", spd[1])
  mso = time(); t = 0; sci = 0
  clr_buf()
  lock()
  now = datetime.now()
  print(now.strftime("%H:%M:%S.%f"))

  while (forward and pos <= seek) or ((not forward) and pos >= seek):       # 200 times 0.005 seconds = 1 second run
    pos_sav = pos; cs = tacho_get();  pos = cs[0]                           #    print("can status: ",cs)
    delta_moved = pos - pos_sav; tot_moved = tot_moved + delta_moved
    vi = cs[1]; sp = cs[2]; cu = cs[3]; du = cs[4]
    ms = time(); sci = ms - mso;                                            #print("uSec = ", sci)
    sci = sci - int(sci); t = t + round(sci * 1000000); t1 = float(t/1000000)
    mso = ms; sci=0.0
    print("Tacho =, ", pos, " ,delta =, ", delta_moved, " ,eT =, %.4f" % t1, " ,eRPM =, ", sp, " ,Duty =, ", du,
          " ,Vin =, ", vi, " ,Imot =, %.2f" % cu,  " ,Moved =, ", tot_moved, )
    if (forward):  # forward
      packet = Message(arbitration_id=1, data=[0, 0, spd[0], 0])   # motor 1
      bus.send(packet)
      packet = Message(arbitration_id=2, data=[0, 0, spd[0], 0])   # motor 2
      bus.send(packet)
    else:          # backwards
      packet = Message(arbitration_id=1, data=[255, 255, spd[1], 255])   # motor 1
      bus.send(packet)
      packet = Message(arbitration_id=2, data=[255, 255, spd[1], 255])   # motor 2
      bus.send(packet)
  now = datetime.now()
  print(now.strftime("%H:%M:%S.%f"))

  if (pid_only): pid_destination(targetP, targetD)                  #engage PID here
  else:
    cnt = spd[0]/4   #150/4 = 37.5  125/4 = 31.25
    rd = 1;
    while (cnt >= 0):
#      rd = 1
#      while (rd <= spd[0]/2):
      aaa = spd[0] - rd
      rampDn(aaa)
      rd = rd + 2
#      sleep(0.008)
      pos_sav = pos; cs = tacho_get(); pos = cs[0]       #    print("can status: ",cs)
      delta_moved = pos - pos_sav; tot_moved = tot_moved + delta_moved
      vi = cs[1]; sp = cs[2]; cu = cs[3]; du = cs[4]
      #while (sci <= 0.005): ms = time(); sci = ms - mso; #print("uSec = ", sci)
      ms = time(); sci = ms - mso
      sci = sci - int(sci); t = t + round(sci * 1000000); t1 = float(t/1000000)
      mso = ms; sci=0.0
      print("tacho =, ", pos, " ,delta =, ", delta_moved, " ,eT =, %.4f" % t1, " ,eRPM =, ", sp, " ,Duty =, ", du,
            " ,Vin =, ", vi, " ,Imot =, %.2f" % cu,  " ,Moved =, ", tot_moved, )
      cnt = cnt - 1
    lock()

  now = datetime.now()
  print(now.strftime("%H:%M:%S.%f"))
  cnt = 100
  if (pid_only): lock()
  else:
    while (cnt >= 0):
      sleep(0.008)
      lock()
      cnt = cnt - 1
      pos_sav = pos; cs = tacho_get(); pos = cs[0]       #    print("can status: ",cs)
      delta_moved = pos - pos_sav; tot_moved = tot_moved + delta_moved
      vi = cs[1]; sp = cs[2]; cu = cs[3]; du = cs[4]
      #while (sci <= 0.005): ms = time(); sci = ms - mso; #print("uSec = ", sci)
      ms = time(); sci = ms - mso
      sci = sci - int(sci); t = t + round(sci * 1000000); t1 = float(t/1000000)
      mso = ms; sci=0.0
      print("tacho =, ", pos, " ,delta =, ", delta_moved, " ,eT =, %.4f" % t1, " ,eRPM =, ", sp, " ,Duty =, ", du,
            " ,Vin =, ", vi, " ,Imot =, %.2f" % cu,  " ,Moved =, ", tot_moved, )
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
