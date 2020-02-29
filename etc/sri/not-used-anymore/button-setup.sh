#!/bin/bash

# Sets the boot button for GPIO interrupt testing
config-pin P8.43 gpio
config-pin P8.43 in+

echo 1 > /sys/class/gpio/gpio72/active_low
echo both > /sys/class/gpio/gpio72/edge
