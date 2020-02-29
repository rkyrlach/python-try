
#!/bin/bash
PATH=/root/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/sri/srip:

echo "Press [CTRL+C] to stop.."
while true
do
###	echo "`python3 dmx-idle.py`"
        echo "`cp /home/sri/srip/heartbeat /home/sri/srip/toIpad.txt`"
	echo "`sleep 5s`"
done

### nohup ./test.sh>/dev/null 2>&1 &
