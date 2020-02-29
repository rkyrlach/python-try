import serial
import binascii
import array as arr

ser = serial.Serial(port = "/dev/ttyS5", baudrate=250000, stopbits=2)

dmxbuf = arr.array('B', [0,0,0,0,0,0,0,0,0])
print ("dmxbuf = ", dmxbuf)

ser.send_break()
ser.write(dmxbuf)

ser.send_break()
ser.write(dmxbuf)

ser.send_break()
ser.write(dmxbuf)

i = 0
while i < 255:
        i += 1
#        dmxbuf = chr(0x00) + chr(0x7f) + chr(0x00) + chr(0x00) + chr(0x00) + chr(0x7f) + chr(0x00) + chr(0x00) + chr(0x00)
        ser.send_break()
        ser.write(dmxbuf)
#        dmxbuf = chr(0x00) + chr(0x00) + chr(0x7f) + chr(0x00) + chr(0x00) + chr(0x00) + chr(0x7f) + chr(0x00) + chr(0x00)
        ser.send_break()
        ser.write(dmxbuf)
#        dmxbuf = chr(0x00) + chr(0x00) + chr(0x00) + chr(0x7f) + chr(0x00) + chr(0x00) + chr(0x00) + chr(0x7f) + chr(0x00)
        ser.send_break()
        ser.write(dmxbuf)
#        dmxbuf = chr(0x00) + chr(0x00) + chr(0x00) + chr(0x00) + chr(0x7f) + chr(0x00) + chr(0x00) + chr(0x00) + chr(0x7f)
        ser.send_break()
        ser.write(dmxbuf)
#        dmxbuf = chr(0x00) + chr(0x00) + chr(0x00) + chr(0x00) + chr(0x00) + chr(0x00) + chr(0x00) + chr(0x00) + chr(0x00)
        ser.send_break()
        ser.write(dmxbuf)

