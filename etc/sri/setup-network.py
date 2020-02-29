
import sys
import subprocess
import os

subprocess.call("/etc/sri/get_dip.sh", shell=True)
subprocess.call("python3 /etc/sri/set-heartbeat.py", shell=True)
if os.path.isfile('/etc/sri/dipsw.txt'):
   f = open('/etc/sri/dipsw.txt', 'r')
   for x in f:
      chf = int(x) % 3
      chf = str(chf + 1)
      if chf.find('1') != -1:
         chn = 'channel=1\n'
      if chf.find('2') != -1:
         chn = 'channel=6\n'
      if chf.find('3') != -1:
         chn = 'channel=11\n'
      print (chn)
      fnm = "/etc/sri/wpa_supplicant-" + x
      pp = fnm.find(x)
      pp = pp + len(x)-1
      fnm = fnm[:pp] + ".conf"
      print (fnm)
      subprocess.call("rm wpa_supplicant.conf", shell=True)
      subprocess.call("ln -s " + fnm + " wpa_supplicant.conf", shell=True)
      h = open(fnm, 'w')
      g = open('/etc/sri/wpa_supplicant-master.conf', 'r')
      for y in g:
         lkr = y
         if lkr.find('ssid="SRI-Lane-1"') != -1:
            print (lkr)
            pos = lkr.find('1')
            print (pos)
            lkr = lkr[:pos] +  x
            pos = lkr.find(x)
            pos = pos + len(x)-1
            lkr = lkr[:pos] + '"\n'
            print (lkr)
            h.write(lkr)
         else:
            h.write(lkr)
      g.close()
      h.close()
      fnm = "/etc/sri/hostapd-" + x
      pp = fnm.find(x)
      pp = pp + len(x)-1
      fnm = fnm[:pp] + ".conf"
      print (fnm)
      subprocess.call("rm hostapd.conf", shell=True)
      subprocess.call("ln -s " + fnm + " hostapd.conf", shell=True)
      h = open(fnm, 'w')
      g = open('/etc/sri/hostapd-master.conf', 'r')
      for y in g:
         lkr = y
         if lkr.find('ssid=SRI-Lane-1') != -1:  ##ssid=SRI-Lane-1
            print (lkr)
            pos = lkr.find('1')
            print (pos)
            lkr = lkr[:pos] +  x
            pos = lkr.find(x)
            pos = pos + len(x)-1
            lkr = lkr[:pos] + '\n'
            print (lkr)
            h.write(lkr)
         else:
            if lkr.find('channel=1') != -1:
               lkr = chn
            h.write(lkr)
      g.close()
      h.close()
   f.close()
