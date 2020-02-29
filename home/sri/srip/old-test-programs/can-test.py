import can
import time
from time import time
from can import Message
from datetime import datetime
from datetime import timedelta

can_interface = 'can0'
#bus = can.interface.Bus(can_interface, bustype='socketcan_native')
bus = can.interface.Bus(channel='can0', bustype='socketcan_native', fd=True)

def msg(nn):
    switcher={
       2305:'VESC Status message 1 ', # bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00')
       3585:'VESC Status message 2 ', # bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00')
       3841:'VESC Status message 3 ', # bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00')
       4097:'VESC Status message 4 ', # bytearray(b'\x01\x1a\xfc\x99\x00\x00\x18\xf5')
       6913:'VESC Status message 5 '  # bytearray(b'\x00\x00\x00\x96\x00\xef\x00\x00')
    }
    return switcher.get(nn,"Invalid can message")

while True:
    message = bus.recv()
    num = int(message.arbitration_id)
    print (msg(num),  "".join( chr(x) for x in message.data))
    print ('for ', msg(num), message.data)
    message.data = message.data[::-1]
    print ('rev ', msg(num), message.data)


