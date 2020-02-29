#!/bin/bash

# We want to use these PWMs for strobing LEDs at 5000 Hz

# Configure pins, re-export & start PWM

#pwm-1:0 -> ../../devices/platform/ocp/48300000.epwmss/48300200.pwm/pwm/pwmchip1/pwm-1:0
config-pin P9.22 pwm
cd /sys/class/pwm/pwmchip1/pwm-1:0
echo 200000 > period ; echo 175000 > duty_cycle ; echo 1 > enable

#pwm-1:1 -> ../../devices/platform/ocp/48300000.epwmss/48300200.pwm/pwm/pwmchip1/pwm-1:1
config-pin P9.21 pwm
cd /sys/class/pwm/pwmchip1/pwm-1:1
echo 200000 > period ; echo 150000 > duty_cycle ; echo 1 > enable

#pwm-4:0 -> ../../devices/platform/ocp/48302000.epwmss/48302200.pwm/pwm/pwmchip4/pwm-4:0
config-pin P9.14 pwm
cd /sys/class/pwm/pwmchip4/pwm-4:0
echo 200000 > period ; echo 125000 > duty_cycle ; echo 1 > enable

#pwm-4:1 -> ../../devices/platform/ocp/48302000.epwmss/48302200.pwm/pwm/pwmchip4/pwm-4:1
config-pin P9.16 pwm
cd /sys/class/pwm/pwmchip4/pwm-4:1
echo 200000 > period ; echo 100000 > duty_cycle ; echo 1 > enable

#pwm-7:0 -> ../../devices/platform/ocp/48304000.epwmss/48304200.pwm/pwm/pwmchip7/pwm-7:0
config-pin P8.19 pwm
cd /sys/class/pwm/pwmchip7/pwm-7:0
echo 200000 > period ; echo 75000 > duty_cycle ; echo 1 > enable

#pwm-7:1 -> ../../devices/platform/ocp/48304000.epwmss/48304200.pwm/pwm/pwmchip7/pwm-7:1
config-pin P8.13 pwm
cd /sys/class/pwm/pwmchip7/pwm-7:1
echo 200000 > period ; echo 50000 > duty_cycle ; echo 1 > enable

#pwm-0:0 -> ../../devices/platform/ocp/48300000.epwmss/48300100.ecap/pwm/pwmchip0/pwm-0:0
config-pin P9.42 pwm
cd /sys/class/pwm/pwmchip0/pwm-0:0
echo 200000 > period ; echo 25000 > duty_cycle ; echo 1 > enable

#pwm-3:0 -> ../../devices/platform/ocp/48302000.epwmss/48302100.ecap/pwm/pwmchip3/pwm-3:0
#config-pin P9.28 pwm
#cd /sys/class/pwm/pwmchip3/pwm-3:0
#echo 200000 > period ; echo 15000 > duty_cycle ; echo 1 > enable

#pwm-6:0 -> ../../devices/platform/ocp/48304000.epwmss/48304100.ecap/pwm/pwmchip6/pwm-6:0
config-pin P9.28 pwm
cd /sys/class/pwm/pwmchip6/pwm-6:0
echo 200000 > period ; echo 10000 > duty_cycle ; echo 1 > enable
