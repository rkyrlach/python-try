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

print("\033[44;1H                                                          ")
print("\033[45;1H                                                          ")
cnt = 0

# the VESC updates his status 50 times per second 1/50 = 0.020 milliseconds
# at full speed the car moves almost 12 inches (67 tachos) in that amount of time

def tacho_get():
   now = datetime.now()
   print(now.strftime("%H:%M:%S.%f"))
   num = 0
   while (num != 6913):
      message1 = bus.recv()
      num = int(message1.arbitration_id)
   tacho = -1
   a=message1.data[0]; b=message1.data[1]; c=message1.data[2]; d=message1.data[3]
   tacho = (d + (c*256) + (b*65536) + (a*16777216))
   if (a==255): tacho = tacho-4294967296
   e=message1.data[4]; f=message1.data[5]
   vin = (f + (e*256))/10.0
#   print("Volts = ",vin)
   now = datetime.now()
   print(now.strftime("%H:%M:%S.%f"))
   return tacho

def main():
  cnt=0
  while cnt <= 50:
    pos = tacho_get()
    print("pos = ",pos)
    packet = Message(arbitration_id=1, data=[0, 0, 16, 0])
    bus.send(packet)
    packet = Message(arbitration_id=2, data=[0, 0, 16, 0])
    bus.send(packet)
#   print("data = ", packet, " \n")
    cnt = cnt + 1
#    print ("\033[44;1Htacho = ", tacho, " Vin = ", vin)
#   time.sleep(0.025)

  while cnt != 0:
    pos = tacho_get()
    print("pos = ",pos)
    packet = Message(arbitration_id=1, data=[0, 0, 16, 0])
    bus.send(packet)
    packet = Message(arbitration_id=2, data=[0, 0, 16, 0])
    bus.send(packet)
#   print("data = ", packet, " \n")
    cnt = cnt - 1
#   print ("\033[44;1Htacho = ", tacho, " Vin = ", vin)
#      time.sleep(0.025)
  while True:
    packet = Message(arbitration_id=1, data=[0, 0, 0, 0, 0])
    bus.send(packet)
    packet = Message(arbitration_id=2, data=[0, 0, 0, 0, 0])
    bus.send(packet)
    pos = tacho_get()
    print("tacho = ",pos)
#packet = Message(arbitration_id=1, data=[0, 0, cnt, 0])
#exit()

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
