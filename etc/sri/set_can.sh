#!/bin/bash

if [ -d "/sys/class/gpio/gpio46" ]
then
    echo "Directory /sys/class/gpio/gpio46 exists"
else
    echo "46" > /sys/class/gpio/export
fi
config-pin -a P9_20 can
config-pin -q P9_20


if [ -d "/sys/class/gpio/gpio47" ]
then
    echo "Directory /sys/class/gpio/gpio47 exists"
else
    echo "47" > /sys/class/gpio/export
fi
config-pin -a P9_19 can
config-pin -q P9_19




