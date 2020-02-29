
import can
import time
from can import Message
from datetime import datetime

bus = can.interface.Bus('can0', bustype='socketcan_native')

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
   num = 0
   m1 = False
   m2 = False
   m3 = False
   m4 = False
   m5 = False
#   print("T",  m1 and m2 and m3 and m4 and m5)
   while ((m1 and m2 and m3 and m4 and m5) == False):
      message0 = bus.recv()
      num = int(message0.arbitration_id)
#      print("msg 0 ", message0)
      if (num == 2305):
        a=message0.data[0]; b=message0.data[1]; c=message0.data[2]; d=message0.data[3]
        e=message0.data[4]; f=message0.data[5]; g=message0.data[6]; h=message0.data[7]
        rpm = (d + (c*256) + (b*65536) + (a*16777216))
        if (a==255): rpm = rpm-4294967296
        current = float(f + (e*256))
        if (e>=128): current = current-65536
        duty = (h + (g*256))
        if (g>=128): duty = duty-65536
        m1 = True
      if (num == 3585):
        #message2 = message0
        a=message0.data[0]; b=message0.data[1]; c=message0.data[2]; d=message0.data[3]
        e=message0.data[4]; f=message0.data[5]; g=message0.data[6]; h=message0.data[7]
        m2 = True
      if (num == 3841):
        #message3 = message0
        a=message0.data[0]; b=message0.data[1]; c=message0.data[2]; d=message0.data[3]
        e=message0.data[4]; f=message0.data[5]; g=message0.data[6]; h=message0.data[7]
        m3 = True
      if (num == 4097):
        #message4 = message0
        a=message0.data[0]; b=message0.data[1]; c=message0.data[2]; d=message0.data[3]
        e=message0.data[4]; f=message0.data[5]; g=message0.data[6]; h=message0.data[7]
        m4 = True
      if (num == 6913):
        #message5 = message0
        a=message0.data[0]; b=message0.data[1]; c=message0.data[2]; d=message0.data[3]
        e=message0.data[4]; f=message0.data[5]; g=message0.data[6]; h=message0.data[7]
        tacho = (d + (c*256) + (b*65536) + (a*16777216))
        if (a==255): tacho = tacho-4294967296
        vin = (f + (e*256))/10.0
        m5 = True
   canstat = [int(tacho), float(vin), float(rpm), float(current), float(duty), a, b, c, d, e, f, g, h]
#   now = datetime.now()
#   print(now.strftime("%H:%M:%S.%f"))
   return canstat

def main():
  cnt=0
  # input
  print("enter motor command: (eg t,600 or t,-600 ")
  command = input()  #string = str(input())
  # output
  p=command.find(",")
  dd='{}'.format(command)[p+1:len(command)] # dd has the value in tenths of inches that we want to move
  dd=round((float(dd)/10.0)*5.755)
#  if (dd >= 400): dd = dd - 250              # cut distance moved by 43 inches (250 tachos)
#  if (dd <= 400): dd = dd + 250              # cut distance moved by 43 inches
  tot_moved = 0
  delta_moved = 0
  cs = tacho_get()   # get our current position
  pos = cs[0]
  if (dd > 0):       # are we going forward
    forward = True
    seek = pos + dd
  else:
    forward = False  # or back towards home
    seek = pos - abs(dd)
  print("currently at: ", pos, " seeking position: ", seek, " dd = ", dd)

  while (forward and pos <= seek) or ((not forward) and pos >= seek):       # 200 times 0.005 seconds = 1 second run
    pos_sav = pos
    cs = tacho_get()
#    print("can status: ",cs)
    pos = cs[0]
    delta_moved = pos - pos_sav
    tot_moved = tot_moved + delta_moved
    vi = cs[1]
    sp = cs[2]
    cu = cs[3]
    du = cs[4]
    print("Tacho =, ", pos, " ,delta =, ", delta_moved, " ,eRPM =, ", sp, " ,Duty =, ", du,
           " ,Vin =, ", vi, " ,Imot =, ", cu,  " ,Moved =, ", tot_moved, )
    if (forward):  # forward
      packet = Message(arbitration_id=1, data=[0, 0, 200, 0])   # motor 1
    else:          # backwards
      packet = Message(arbitration_id=1, data=[255, 255, 55, 255])   # motor 1
    bus.send(packet)
    if (forward):  # forward
      packet = Message(arbitration_id=2, data=[0, 0, 200, 0])   # motor 2
    else:          # backwards
      packet = Message(arbitration_id=2, data=[255, 255, 55, 255])   # motor 2
    bus.send(packet)
#    print("data = ", packet, " \n")
#    cnt = cnt + 1
#    print ("\033[44;1Htacho = ", tacho, " Vin = ", vin)
    time.sleep(0.003)

  cnt = 600
  while (cnt >= 0):
    packet = Message(arbitration_id=1, data=[0, 0, 0, 0, 0])
    bus.send(packet)
    packet = Message(arbitration_id=2, data=[0, 0, 0, 0, 0])
    bus.send(packet)
    pos_sav = pos
    cs = tacho_get()
#    print("can status: ",cs)
    pos = cs[0]
    delta_moved = pos - pos_sav
    tot_moved = tot_moved + delta_moved
    vi = cs[1]
    sp = cs[2]
    cu = cs[3]
    du = cs[4]
    print("tacho =, ", pos, " ,delta =, ", delta_moved, " ,eRPM =, ", sp, " ,Duty =, ", du,
           " ,Vin =, ", vi, " ,Imot =, ", cu,  " ,Moved =, ", tot_moved, )
#    print ("\033[40;31Htacho = ", pos, " Volts = ", v)
    cnt = cnt - 1

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
