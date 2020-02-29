
#!/bin/bash
PATH=/root/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/sri/srip:/etc/sri:

#SERVER_T1="$(ps -ux | pgrep -f python3)"
#echo "$SERVER_T1"
#MYLEN=${#SERVER_T1}
#echo "$MYLEN"

#if [ $MYLEN -ge 14 ]; then
echo "`kill $(pgrep -f 'python3')`";
echo "You are logged in as: `whoami`";
#echo "`/bin/bash -c 'nohup python3 -u /home/sri/srip/server.py &'`";
#else
#   echo "no match";
#fi




