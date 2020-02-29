import serial
import binascii
import array as arr

ser = serial.Serial(port = "/dev/ttyS5", baudrate=250000, stopbits=2)

dmxbuf = arr.array('B', [0,0,0,0,0,0,0,0,0])
print ("dmxbuf = ", dmxbuf)

while True:
  ser.send_break()
  ser.write(dmxbuf)
  ser.send_break()
  ser.write(dmxbuf)

