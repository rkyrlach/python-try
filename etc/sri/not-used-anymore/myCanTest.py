import serial

ser = serial.Serial(port = "/dev/ttyS4", baudrate=500000, stopbits=1)

canbuf = chr(0x55) + chr(0xaa) + chr(0x55) + chr(0xaa) + chr(0x55) + chr(0xaa) + chr(0x55) + chr(0xaa) + chr(0x55)

ser.send_break()
ser.write(canbuf)

ser.send_break()
ser.write(canbuf)

ser.send_break()
ser.write(canbuf)

i = 0
while i < 255:
        i += 1
        canbuf = chr(0x00) + chr(0x7f) + chr(0x00) + chr(0x00) + chr(0x00) + chr(0x7f) + chr(0x00) + chr(0x00) + chr(0x00)
        ser.send_break()
        ser.write(canbuf)
        canbuf = chr(0x00) + chr(0x00) + chr(0x7f) + chr(0x00) + chr(0x00) + chr(0x00) + chr(0x7f) + chr(0x00) + chr(0x00)
        ser.send_break()
        ser.write(canbuf)
        canbuf = chr(0x00) + chr(0x00) + chr(0x00) + chr(0x7f) + chr(0x00) + chr(0x00) + chr(0x00) + chr(0x7f) + chr(0x00)
        ser.send_break()
        ser.write(canbuf)
        canbuf = chr(0x00) + chr(0x00) + chr(0x00) + chr(0x00) + chr(0x7f) + chr(0x00) + chr(0x00) + chr(0x00) + chr(0x7f)
        ser.send_break()
        ser.write(canbuf)
        canbuf = chr(0x00) + chr(0x00) + chr(0x00) + chr(0x00) + chr(0x00) + chr(0x00) + chr(0x00) + chr(0x00) + chr(0x00)
        ser.send_break()
        ser.write(canbuf)
ser.close()


