#!/bin/bash
PATH=/root/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/sri/srip:

IPAD_T1="$(lsusb | grep iPad)"
echo "$IPAD_T1"

if echo "$IPAD_T1" | grep -q "iPad"; then
    echo "`systemctl start echoipad.service`";
    echo "You are login as: `whoami`";
else
    echo "no match";
fi
