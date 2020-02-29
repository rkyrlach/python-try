#!/bin/bash

# Set usable UART pins

#UART1 -- ttyS1
#config-pin P9.24 uart	# TX -- Used for CAN0 RX
#config-pin P9.26 uart	# RX -- Used for CAN0 TX
#config-pin P9.19 uart	# RTS
#config-pin P9.20 uart	# CTS

#UART2 -- ttyS2
config-pin P9.21 uart	# TX -- Well defined
config-pin P9.22 uart	# RX -- Well defined
stty -F /dev/ttyS2 115200 -drain clocal -crtscts cs8 -cstopb -parity raw -icanon

#UART3 -- ttyS3 (TX only)
config-pin P9.42 uart	# TX -- Use for DMX
#config-pin P8.34 uart	# RTS
#config-pin P8.36 uart	# CTS
stty -F /dev/ttyS3 115200 -drain clocal -crtscts cs8 -cstopb -parity raw -icanon

#UART4 -- ttyS4
config-pin P9.13 uart	# TX -- Well defined
config-pin P9.11 uart	# RX -- Well defined
#config-pin P8.33 uart	# RTS
#config-pin P8.35 uart	# CTS
stty -F /dev/ttyS4 115200 -drain clocal -crtscts cs8 -cstopb -parity raw -icanon

#UART5 -- ttyS5
#config-pin P8.37 uart	# TX -- Doesn't Work
#config-pin P8.38 uart	# RX -- Doesn't Work
#config-pin P8.32 uart	# RTS
#config-pin P8.31 uart	# CTS
