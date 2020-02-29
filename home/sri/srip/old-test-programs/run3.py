import os
from multiprocessing import Pool


processes = ('can-test1.py', ' example3.py')


def run_process(process):
    os.system('python3 {}'.format(process))


pool = Pool(processes=2)
pool.map(run_process, processes)
