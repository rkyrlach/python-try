#!/bin/bash

# Set CAN0 pins
#config-pin P9.20 can	# TX
#config-pin P9.19 can	# RX

# Set CAN0 network interface
ip link set can0 up type can bitrate 500000

# Set CAN1 pins
#config-pin P9.26 can	# TX
#config-pin P9.24 can	# RX

# Set CAN1 network interface
#ip link set can1 type can bitrate 500000
#ip link set up can1
