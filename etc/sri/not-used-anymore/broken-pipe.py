import sys
import struct
import subprocess
import os

if os.path.isfile('/nohup.out'):
   f = open('/nohup.out', 'rw')
   for x in f:
      ### print x
      cmd = x
      if cmd.find("Broken pipe") != -1:
         subprocess.call(['cp "/etc/crontab-enable-brokenpipe" "/etc/crontab"'], shell=True)
         os.remove('/nohup.out')
   f.close()
