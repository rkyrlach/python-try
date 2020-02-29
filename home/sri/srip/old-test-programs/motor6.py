
import can
import time
from time import time
from can import Message
from datetime import datetime
from datetime import timedelta

#bus = can.interface.Bus('can0', bustype='socketcan_native')
bus = can.interface.Bus(channel='can0', bustype='socketcan_native', fd=True)

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
        #message1
      if (num == 2305):
        a=message0.data[0]; b=message0.data[1]; c=message0.data[2]; d=message0.data[3]
        e=message0.data[4]; f=message0.data[5]; g=message0.data[6]; h=message0.data[7]
        rpm = (d + (c*256) + (b*65536) + (a*16777216))
        if (a>=128): rpm = rpm-4294967296
        current = float(f + (e*256))
        if (e>=128): current = current-65536
        duty = (h + (g*256))
        if (g>=128): duty = duty-65536
        m1 = True
      if (num == 3585):
        #message2
        a=message0.data[0]; b=message0.data[1]; c=message0.data[2]; d=message0.data[3]
        e=message0.data[4]; f=message0.data[5]; g=message0.data[6]; h=message0.data[7]
        m2 = True
      if (num == 3841):
        #message3
        a=message0.data[0]; b=message0.data[1]; c=message0.data[2]; d=message0.data[3]
        e=message0.data[4]; f=message0.data[5]; g=message0.data[6]; h=message0.data[7]
        m3 = True
      if (num == 4097):
        #message4
        a=message0.data[0]; b=message0.data[1]; c=message0.data[2]; d=message0.data[3]
        e=message0.data[4]; f=message0.data[5]; g=message0.data[6]; h=message0.data[7]
        Imot = float(f + (e*256))/10.0
        if (e>=128): Imot = Imot-6553.6
        m4 = True
      if (num == 6913):
        #message5
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

def main():
  cnt=0
  print("enter motor command: (eg t,600 or t,-600 ")
  command = input()                         # string = str(input())
  p=command.find(",")                       # find the start of the desired position
  dd='{}'.format(command)[p+1:len(command)] # dd has the value in tenths of inches that we want to move
  dd=round((float(dd)/10.0)*5.755)          # dd now has the number of tachos we need to move

#  if (dd >= 400): dd = dd - 250                     # cut distance moved by 43 inches (250 tachos)
#  if (dd <= 400): dd = dd + 250                     # cut distance moved by 43 inches

  tot_moved = 0; delta_moved = 0; cs = tacho_get()   # get our current position
  pos = cs[0]
  if (dd > 0): forward = True; seek = pos + dd       # are we going forward
  else: forward = False; seek = pos - abs(dd)        # or back towards home
  print("currently at: ", pos, " seeking position: ", seek, " dd = ", dd)
  mso = time(); t = 0; sci = 0
  while (forward and pos <= seek) or ((not forward) and pos >= seek):       # 200 times 0.005 seconds = 1 second run
    pos_sav = pos; cs = tacho_get();  pos = cs[0]                           #    print("can status: ",cs)
    delta_moved = pos - pos_sav; tot_moved = tot_moved + delta_moved
    vi = cs[1]; sp = cs[2]; cu = cs[3]; du = cs[4]
    while (sci <= 0.005): ms = time(); sci = ms - mso; #print("uSec = ", sci)
    sci = sci - int(sci); t = t + round(sci * 1000000); t1 = float(t/1000000)
    mso = ms; sci=0.0
    print("Tacho =, ", pos, " ,delta =, ", delta_moved, " ,eT =, %.4f" % t1, " ,eRPM =, ", sp, " ,Duty =, ", du,
          " ,Vin =, ", vi, " ,Imot =, %.2f" % cu,  " ,Moved =, ", tot_moved, )
    if (forward):  # forward
      packet = Message(arbitration_id=1, data=[0, 0, 200, 0])   # motor 1
      bus.send(packet)
      packet = Message(arbitration_id=2, data=[0, 0, 200, 0])   # motor 2
      bus.send(packet)
    else:          # backwards
      packet = Message(arbitration_id=1, data=[255, 255, 55, 255])   # motor 1
      bus.send(packet)
      packet = Message(arbitration_id=2, data=[255, 255, 55, 255])   # motor 2
      bus.send(packet)

  cnt = 600
  while (cnt >= 0):
    packet = Message(arbitration_id=1, data=[0, 0, 0, 0, 0])
    bus.send(packet)
    packet = Message(arbitration_id=2, data=[0, 0, 0, 0, 0])
    bus.send(packet)

    pos_sav = pos; cs = tacho_get(); pos = cs[0]             #    print("can status: ",cs)
    delta_moved = pos - pos_sav; tot_moved = tot_moved + delta_moved
    vi = cs[1]; sp = cs[2]; cu = cs[3]; du = cs[4]
    while (sci <= 0.005): ms = time(); sci = ms - mso; #print("uSec = ", sci)
    sci = sci - int(sci); t = t + round(sci * 1000000); t1 = float(t/1000000)
    mso = ms; sci=0.0
    print("tacho =, ", pos, " ,delta =, ", delta_moved, " ,eT =, %.4f" % t1, " ,eRPM =, ", sp, " ,Duty =, ", du,
          " ,Vin =, ", vi, " ,Imot =, %.2f" % cu,  " ,Moved =, ", tot_moved, )
    cnt = cnt - 1

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
