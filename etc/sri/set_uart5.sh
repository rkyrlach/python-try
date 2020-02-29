
#!/bin/bash

if [ -d "/sys/class/gpio/gpio78" ]
then
    echo "Directory /sys/class/gpio/gpio78 exists"
else
    echo "78" > /sys/class/gpio/export
fi
config-pin -a P8_37 uart
config-pin -q P8_37                ### serial 5 TX


if [ -d "/sys/class/gpio/gpio79" ]
then
    echo "Directory /sys/class/gpio/gpio79 exists"
else
    echo "79" > /sys/class/gpio/export
fi
config-pin -a P8_38 uart
config-pin -q P8_38                ### serial 5 RX

