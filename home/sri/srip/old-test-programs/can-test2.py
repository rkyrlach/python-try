import can
import time
from can import Message
bus = can.interface.Bus('can0', bustype='socketcan_native')
print("\033[44;1H                                                          ")
print("\033[45;1H                                                          ")
cnt = 0
def msg(nn):
    switcher={
       2305:'VESC Status message 1 ', # bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00')
       3585:'VESC Status message 2 ', # bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00')
       3841:'VESC Status message 3 ', # bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00')
       4097:'VESC Status message 4 ', # bytearray(b'\x01\x1a\xfc\x99\x00\x00\x18\xf5')
       6913:'VESC Status message 5 '} # bytearray(b'\x00\x00\x00\x96\x00\xef\x00\x00')
    return switcher.get(nn,"Invalid can message")
while cnt <= 50:
      message1 = bus.recv()
      #print('msg from can = ', message.data)
      num = int(message1.arbitration_id)
      msgn = msg(num)
      if(msgn.find('5') != -1):
         a=message1.data[0]; b=message1.data[1]; c=message1.data[2]; d=message1.data[3]
         e=message1.data[4]; f=message1.data[5]
         tacho = (d + (c*256) + (b*65536) + (a*16777216))
         if (a==255): tacho = tacho-4294967296
         vin = (f + (e*256))/10.0
         packet = Message(arbitration_id=1, data=[0, 0, cnt, 0])
         bus.send(packet)
         print("data = ", packet, " \n")
         cnt = cnt + 1
         print ("\033[44;1Htacho = ", tacho, " Vin = ", vin)
#      time.sleep(0.025)
while cnt != 0:
      message1 = bus.recv()
      #print('msg from can = ', message.data)
      num = int(message1.arbitration_id)
      msgn = msg(num)
      if(msgn.find('5') != -1):
         a=message1.data[0]; b=message1.data[1]; c=message1.data[2]; d=message1.data[3]
         e=message1.data[4]; f=message1.data[5]
         tacho = (d + (c*256) + (b*65536) + (a*16777216))
         if (a==255): tacho = tacho-4294967296
         vin = (f + (e*256))/10.0
         packet = Message(arbitration_id=1, data=[0, 0, cnt, 0])
         bus.send(packet)
         print("data = ", packet, " \n")
         cnt = cnt - 1
         print ("\033[44;1Htacho = ", tacho, " Vin = ", vin)
#      time.sleep(0.025)
packet = Message(arbitration_id=1, data=[0, 0, 0, 0, 0])
packet = Message(arbitration_id=1, data=[0, 0, cnt, 0])
exit()

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

