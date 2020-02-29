
import sys
import subprocess
import os

fnm = "/home/sri/srip/heartbeat"
h = open(fnm, 'w')
g = open('/etc/sri/dipsw.txt', 'r')
for y in g:
   lkr = y
   hb = 'id,' + lkr
   print (hb)
   h.write(hb)
g.close()
h.close()
