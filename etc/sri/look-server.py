
import sys
import subprocess
import os

#subprocess.call(['cp /home/sri/srip/heartbeat /home/sri/srip/toIpad.txt'], shell=True)
#subprocess.call(['pkill -f python3'], shell=True)
print( " restarting the python server " )
subprocess.call(['systemctl start sri-server.service'], shell=True)


#print (" server ?",SERVER_T1)

#if os.path.isfile('/nohup.out'):
#      b = os.path.getsize('/nohup.out')
#      if b >= 1:
#         f = open('/nohup.out', 'r')
#         for x in f:
#            print x
#            cmd = x
#            if cmd.find("Broken pipe") != -1:
#               subprocess.call(['systemctl stop sri-running.timer'], shell=True)
#               subprocess.call(['systemctl start sri-connect.timer'], shell=True)
#               os.remove('/nohup.out')
#               subprocess.call(['pkill -f client'], shell=True)
#               subprocess.call(['pkill -f python'], shell=True)
#         f.close()




