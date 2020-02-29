import serial

ser = serial.Serial(port = "/dev/ttyS5", baudrate=250000, stopbits=2)

ser.close()


