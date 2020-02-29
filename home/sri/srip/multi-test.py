import os
from multiprocessing import Pool

processes = ('serv1.py', 'dmx-serv.py', 'proc3.py')

def run_process(process):
    os.system('python3 {}'.format(process))

if __name__=="__main__":
    print("hi Richard ")

pool = Pool(processes=3)
pool.map(run_process, processes)


