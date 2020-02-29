import serial
import binascii

ser = serial.Serial(port = "/dev/ttyS1", baudrate=500000, stopbits=2)

i=0
while i <16:
	rx_raw = ser.read(9)
	rx=binascii.hexlify(bytearray(rx_raw))
        print(rx),
        print(" - "),
        rx_raw = ser.read(9)
        rx=binascii.hexlify(bytearray(rx_raw))
        print(rx),
        print(" - "),
        rx_raw = ser.read(9)
        rx=binascii.hexlify(bytearray(rx_raw))
        print(rx),
        print(" - "),
        rx_raw = ser.read(9)
	rx=binascii.hexlify(bytearray(rx_raw))
	print(rx),
	print("\n")
	i = i + 1

canbuf = chr(0x00) + chr(0x00) + chr(0x50) + chr(0x00) 
canbuf2 = chr(0x00) + chr(0x00) + chr(0x00) + chr(0x00) 

ser.send_break()
ser.write(canbuf)
ser.write(canbuf2)
ser.close()


