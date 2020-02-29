#!/bin/bash

# Make sure these services are disable by default
# at next boot.
systemctl disable hostapd.service
systemctl disable wpa_supplicant@wlan0.service
systemctl disable sri-server.service

# Turn off LEDs

cd /sys/class/gpio/gpio69
echo  1 > value                 ### turn off green led for car
cd /sys/class/gpio/gpio67
echo  1 > value                 ### turn off red led for lane


### echo 0 > /sys/class/leds/red/brightness
### echo 0 > /sys/class/leds/green/brightness

echo "Custom service cleanup complete."
