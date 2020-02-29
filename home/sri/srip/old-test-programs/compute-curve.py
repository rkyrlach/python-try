from array import *
import math
import time

#       // Convert tacho into inches
#       // wheel diameter = 59mm = 2.322835 inches
#       // wheel circumference = 7.2974 inches
#       // 1 tacho is 1/42nd of a revolution or 0.17375 inches

# Wheel diameter (mm)	Wheel circumference (mm)	Wheel circumference (in)	Wheel circumference (ft)
#       59.00           	185.35                  	7.30	                   0.61
#distance moved per wheel rev. (mm)      1 Tacho @ 42/rev. (mm)
#         185.35	                        4.41

# command to GO xxx eRPM (col B)	eRPM (steady) no acceleration	Wheel RPM (eRPM/7)	Wheel RPS
#        110  					 7000   		     1000.00   	          16.67
# distance moved / sec. (mm)	distance moved / sec. (in)	distance moved / sec. (ft)	tachos moved/sec.
#      3089.23	                      121.62	                     10.14	                    425.68	    @10 FPS


#  distance 
#(non-linear)  VESC command
#37		55
#75		60
#112		65
#149		70
#186		75
#224		80
#261		85
#298		90
#336		95
#373		100
#671		100
#970		100
#1268		100
#1566		100
#1865		100
#2163		100
#2462		100
#2760		100
#3058		100
#3357		100
#3394		95
#3431		90
#3469		85
#3506		80
#3543		75
#3580		70
#3618		65
#3655		60
#3692		55
#3730		50


curv = array('f', [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31])
dist = 3800          # first distance needed in tachos (55 feet)
max_spd = 212        # 212 tachos per second using acceleration curve #1
control_level = 69   # 3500 eRPM = 212 tachos / second
per10 = 0.1          # accel 10% and slow 10% 80% max out
spdUp = 0.1*dist
sloDn = 0.1*dist
full  = 0.8*dist
cnt = 0
while (cnt <= 10):
  curv[cnt] = round(((control_level-40)*cnt/10.0)+40)
  cnt += 1
while (cnt <= 20):
  curv[cnt] = control_level
  cnt += 1
  cd = 0.9
while (cnt <= 30):
  curv[cnt] = round(((control_level-40)*cd)+40)
  cnt += 1
  cd -= 0.1

for x in curv:
 print(x)
