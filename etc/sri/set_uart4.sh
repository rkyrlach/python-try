#!/bin/bash


if [ -d "/sys/class/gpio/gpio30" ]
then
    echo "Directory /sys/class/gpio/gpio30 exists"
else
    echo "30" > /sys/class/gpio/export
fi
config-pin -a P9_11 uart
config-pin -q P9_11              ### serial 4 RX

if [ -d "/sys/class/gpio/gpio31" ]
then
    echo "Directory /sys/class/gpio/gpio31 exists"
else
    echo "31" > /sys/class/gpio/export
fi
config-pin -a P9_13 uart
config-pin -q P9_13              ### serial 4 TX


