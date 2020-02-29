
#!/bin/bash

if [ -d "/sys/class/gpio/gpio2" ]
then
    echo "Directory /sys/class/gpio/gpio2 exists"
else
    echo "02" > /sys/class/gpio/export
fi
config-pin -a P9_22  uart    ### charger serial input
config-pin -q P9_22          ### serial 2 RX


if [ -d "/sys/class/gpio/gpio8" ]
then
    echo "Directory /sys/class/gpio/gpio8 exists"
else
    echo "08" > /sys/class/gpio/export
fi
config-pin -a P8_35  gpio_pd    ### dip switch power
cd /sys/class/gpio/gpio8
echo out > direction
echo  0 > value
config-pin -q P8_35


if [ -d "/sys/class/gpio/gpio26" ]
then
    echo "Directory /sys/class/gpio/gpio26 exists"
else
    echo "26" > /sys/class/gpio/export
fi
config-pin -a P8_14  gpio_pu    ### dip switch enable
cd /sys/class/gpio/gpio26
echo out > direction
echo  1 > value
config-pin -q P8_14


if [ -d "/sys/class/gpio/gpio66" ]
then
    echo "Directory /sys/class/gpio/gpio66 exists"
else
    echo "66" > /sys/class/gpio/export
fi
config-pin -a P8_7  gpio_pu    ### red led
cd /sys/class/gpio/gpio66
echo out > direction
echo  1 > value
config-pin -q P8_7


if [ -d "/sys/class/gpio/gpio67" ]
then
    echo "Directory /sys/class/gpio/gpio67 exists"
else
    echo "67" > /sys/class/gpio/export
fi
config-pin -a P8_8  gpio_pu    ### blue led
cd /sys/class/gpio/gpio67
echo out > direction
echo  1 > value
config-pin -q P8_8


if [ -d "/sys/class/gpio/gpio69" ]
then
    echo "Directory /sys/class/gpio/gpio69 exists"
else
    echo "69" > /sys/class/gpio/export
fi
config-pin -a P8_9  gpio_pu    ### green led
cd /sys/class/gpio/gpio69
echo out > direction
echo  1 > value
config-pin -q P8_9


if [ -d "/sys/class/gpio/gpio68" ]
then
    echo "Directory /sys/class/gpio/gpio68 exists"
else
    echo "68" > /sys/class/gpio/export
fi
config-pin -a P8_10  gpio_pu
cd /sys/class/gpio/gpio68
echo in > direction
config-pin -q p8_10


if [ -d "/sys/class/gpio/gpio61" ]
then
    echo "Directory /sys/class/gpio/gpio61 exists"
else
    echo "61" > /sys/class/gpio/export
fi
config-pin -a P8_26  gpio_pu
cd /sys/class/gpio/gpio61
echo in > direction
config-pin -q P8_26


if [ -d "/sys/class/gpio/gpio60" ]
then
    echo "Directory /sys/class/gpio/gpio60 exists"
else
    echo "60" > /sys/class/gpio/export
fi
config-pin -a P9_12  gpio_pu
cd /sys/class/gpio/gpio60
echo in > direction
config-pin -q P9_12


if [ -d "/sys/class/gpio/gpio70" ]
then
    echo "Directory /sys/class/gpio/gpio70 exists"
else
    echo "70" > /sys/class/gpio/export
fi
config-pin -a P8_45  gpio_pd
cd /sys/class/gpio/gpio70
echo in > direction
config-pin -q P8_45


if [ -d "/sys/class/gpio/gpio71" ]
then
    echo "Directory /sys/class/gpio/gpio71 exists"
else
    echo "71" > /sys/class/gpio/export
fi
config-pin -a P8_46  gpio_pd
cd /sys/class/gpio/gpio71
echo in > direction
config-pin -q P8_46


if [ -d "/sys/class/gpio/gpio72" ]
then
    echo "Directory /sys/class/gpio/gpio72 exists"
else
    echo "72" > /sys/class/gpio/export
fi
config-pin -a P8_43  gpio_pd
cd /sys/class/gpio/gpio72
echo in > direction
config-pin -q P8_43


if [ -d "/sys/class/gpio/gpio73" ]
then
    echo "Directory /sys/class/gpio/gpio73 exists"
else
    echo "73" > /sys/class/gpio/export
fi
config-pin -a P8_44  gpio_pd
cd /sys/class/gpio/gpio73
echo in > direction
config-pin -q P8_44


if [ -d "/sys/class/gpio/gpio74" ]
then
    echo "Directory /sys/class/gpio/gpio74 exists"
else
    echo "74" > /sys/class/gpio/export
fi
config-pin -a P8_41  gpio_pd
cd /sys/class/gpio/gpio74
echo in > direction
config-pin -q P8_41


if [ -d "/sys/class/gpio/gpio75" ]
then
    echo "Directory /sys/class/gpio/gpio75 exists"
else
    echo "75" > /sys/class/gpio/export
fi
config-pin -a P8_42  gpio_pd
cd /sys/class/gpio/gpio75
echo in > direction
config-pin -q P8_42


if [ -d "/sys/class/gpio/gpio76" ]
then
    echo "Directory /sys/class/gpio/gpio76 exists"
else
    echo "76" > /sys/class/gpio/export
fi
config-pin -a P8_39  gpio_pd
cd /sys/class/gpio/gpio76
echo in > direction
config-pin -q P8_39


if [ -d "/sys/class/gpio/gpio77" ]
then
    echo "Directory /sys/class/gpio/gpio77 exists"
else
    echo "77" > /sys/class/gpio/export
fi
config-pin -a P8_40  gpio_pd
cd /sys/class/gpio/gpio77
echo in > direction
config-pin -q P8_40


# Do not configure the wireless lan interface
/bin/rm -f /etc/systemd/network/wlan0.network

# Stop and disable wireless lan services
systemctl stop hostapd.service
systemctl disable hostapd.service
systemctl stop wpa_supplicant@wlan0.service
systemctl disable wpa_supplicant@wlan0.service

# Stop and disable server services
systemctl stop sri-server.service
systemctl disable sri-server.service
#systemctl stop echoipad.service
#systemctl disable echoipad.service

# Start cron and rsyslog services
# systemctl enable rsyslog
### service rsyslog start
### service cron start
# start  connect timer to try and find an iPad every 5 seconds
#systemctl stop sri-running.timer
#systemctl stop sri-connect.timer
#systemctl disable sri-running.timer
#systemctl disable sri-connect.timer
#systemctl stop sri-running.service
#systemctl stop sri-connect.service
#systemctl disable sri-running.service
#systemctl disable sri-connect.service

export MYMODE="car"
BTN_MODE=$(cat /sys/class/gpio/gpio68/value)
if [ "$BTN_MODE" == "0"  ];
then
        export MYMODE="lane"
fi
echo $MYMODE

case "$MYMODE" in
lane)
	echo "Setting up mode as Lane Controller..."
	# Start cron and rsyslog services
	# systemctl enable rsyslog
	### service rsyslog starc

        /bin/ln -s /etc/sri/wlan0-ap.network /etc/systemd/network/wlan0.network
        systemctl restart systemd-networkd.service
        systemctl enable hostapd.service
        systemctl start hostapd.service

        systemctl stop sri-server.service
        systemctl disable sri-server.service
        kill $(pgrep -f 'client-iPad.py')

        #systemctl enable sri-connect.timer
        #systemctl enable sri-running.timer
        #systemctl stop sri-running.timer
        #systemctl start sri-connect.timer
        #systemctl enable echoipad.service
        #systemctl start echoipad.service

        ### systemctl enable sri-client.service
        ### systemctl start sri-client.service

        cd /sys/class/gpio/gpio66
        echo  0 > value                 ### turn on red led for lane
	;;
car)
	echo "Setting up mode as Car Controller..."
	# /etc/sri/set_can.sh
	# ip link set can0 up type can bitrate 500000
	sleep 2
	ip link set can0 down
	sleep 2
	ip link set can0 up type can bitrate 500000
	sleep 2

        /bin/ln -s /etc/sri/wlan0-wpa.network /etc/systemd/network/wlan0.network
        systemctl restart systemd-networkd.service
        systemctl enable wpa_supplicant@wlan0.service
        systemctl start wpa_supplicant@wlan0.service

#        systemctl stop sri-running.timer
#        systemctl stop sri-connect.timer
#        systemctl disable sri-running.timer
#        systemctl disable sri-connect.timer
#        systemctl disable echoipad.service

        kill $(pgrep -f 'server.py')

	systemctl enable sri-server.service
	systemctl start sri-server.service

	cd /sys/class/gpio/gpio69
	echo  0 > value                 ### turn on green led for car
	;;
*)
	echo "No mode set."
	;;
esac
