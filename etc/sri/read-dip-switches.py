import Adafruit_BBIO.GPIO as GPIO;
GPIO.setup("P8_45", GPIO.IN)  #bit0
GPIO.setup("P8_46", GPIO.IN)  #bit1
GPIO.setup("P8_43", GPIO.IN)  #bit2
GPIO.setup("P8_44", GPIO.IN)  #bit3
GPIO.setup("P8_41", GPIO.IN)  #bit4
GPIO.setup("P8_42", GPIO.IN)  #bit5
GPIO.setup("P8_39", GPIO.IN)  #bit6
GPIO.setup("P8_40", GPIO.IN)  #bit7
GPIO.setup("P8_35", GPIO.OUT)      # power for the dip switch
GPIO.setup("P8_14", GPIO.OUT)      # enable the dip-sw driver chip
GPIO.output("P8_35", GPIO.HIGH)    # turn on dip sw
GPIO.output("P8_14", GPIO.LOW)     # enable dip
###print GPIO.input("P8_45")
###print GPIO.input("P8_46")
###print GPIO.input("P8_43")
###print GPIO.input("P8_44")
###print GPIO.input("P8_41")
###print GPIO.input("P8_42")
###print GPIO.input("P8_39")
###print GPIO.input("P8_40")

dip_sw = 0

if GPIO.input("P8_40"):
    dip_sw = dip_sw | 0x00
else:
    dip_sw = dip_sw | 0x01

dip_sw = dip_sw << 1
if GPIO.input("P8_39"):
    dip_sw = dip_sw | 0x00
else:
    dip_sw = dip_sw | 0x01

dip_sw = dip_sw << 1
if GPIO.input("P8_42"):
    dip_sw = dip_sw | 0x00
else:
    dip_sw = dip_sw | 0x01

dip_sw = dip_sw << 1
if GPIO.input("P8_41"):
    dip_sw = dip_sw | 0x00
else:
    dip_sw = dip_sw | 0x01

dip_sw = dip_sw << 1
if GPIO.input("P8_44"):
    dip_sw = dip_sw | 0x00
else:
    dip_sw = dip_sw | 0x01

dip_sw = dip_sw << 1
if GPIO.input("P8_43"):
    dip_sw = dip_sw | 0x00
else:
    dip_sw = dip_sw | 0x01

dip_sw = dip_sw << 1
if GPIO.input("P8_46"):
    dip_sw = dip_sw | 0x00
else:
    dip_sw = dip_sw | 0x01

dip_sw = dip_sw << 1
if GPIO.input("P8_45"):
    dip_sw = dip_sw | 0x00
else:
    dip_sw = dip_sw | 0x01

print (dip_sw)
GPIO.output("P8_35", GPIO.LOW)    # turn off dip sw power
GPIO.output("P8_14", GPIO.HIGH)   # disable dip
