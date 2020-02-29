#!/bin/bash
PATH=/root/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/sri/srip:

## heartbeat in bash for over 1000 days or until death ##
for i in {1..14400000}
do
   echo "`cp /home/sri/srip/heartbeat /home/sri/srip/toIpad.txt`";
   echo "hb";
   sleep 6s;
done
## sleep in bash for loop ##
exit 1


